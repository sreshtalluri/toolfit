"""Confusion matrix: for each tool in the catalog, generate multiple tasks and tally which tool
the model-under-test actually called against which tool was intended (design doc M1 Design §4).
The headline artifact — off-diagonal mass names the exact tool pairs to fix. Grades all pairs,
not just near-neighbor-targeted ones (design doc M1 Design §2 decision)."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import partial

import anthropic
from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.gen.schema_sampler import count_distinct, sample_arguments
from toolfit.gen.taskgen import GENERATOR_MODEL, GeneratedTask, check_no_leakage, check_solvability, generate_task
from toolfit.grade.grader import grade_sequence
from toolfit.run.adapters import ModelAdapter, ResultFor, ToolCall, run_steps

NO_CALL = "(no call)"
ERROR = "(error)"  # provider/model output unusable: truncated, empty, or unparseable before any call
MAX_TASK_REGENERATIONS = 2  # extra generator attempts when the solvability check says AMBIGUOUS
HALLUCINATED = "(hallucinated)"


def synthetic_result(catalog: ToolCatalog, *, seed: int) -> ResultFor:
    """Dry-run tool results for multi-step trials: sampled from the tool's declared outputSchema
    when it has one, else a neutral stub. Never a model's invention (design doc M5) — a
    fabricated result would steer the model under test."""

    def result_for(call: ToolCall) -> dict:
        tool = catalog.get(call.tool_name) if call.tool_name else None
        schema = getattr(tool, "output_schema", None) if tool else None
        if schema:
            try:
                return sample_arguments(schema, seed=seed)
            except ValueError:
                pass
        return {"ok": True}

    return result_for


@dataclass
class TrialRecord:
    task: GeneratedTask
    passed: bool
    calls: list[ToolCall] = field(default_factory=list)
    preceding: list[str] = field(default_factory=list)  # tools called before the passing call
    arg_diff: dict[str, str] = field(default_factory=dict)  # per-parameter reason when args failed

    @property
    def via_precondition(self) -> bool:
        return self.passed and bool(self.preceding)


@dataclass
class ConfusionMatrix:
    counts: dict[str, dict[str, int]] = field(default_factory=dict)
    distinct_trials: dict[str, int] = field(default_factory=dict)
    trials_per_tool: dict[str, int] = field(default_factory=dict)
    trials_by_tool: dict[str, list[TrialRecord]] = field(default_factory=dict)
    # Observed precondition graph (design doc M5): edges[intended][earlier_tool] = trials in which
    # earlier_tool was called before the correct call of intended.
    precondition_edges: dict[str, dict[str, int]] = field(default_factory=dict)
    descriptions: dict[str, str] = field(default_factory=dict)
    solvability_warnings: list[str] = field(default_factory=list)
    leakage_warnings: list[str] = field(default_factory=list)
    schema_warnings: list[str] = field(default_factory=list)
    model: str = ""
    generator_model: str = ""
    seeds: int = 0
    max_steps: int = 1
    only: list[str] = field(default_factory=list)  # --only: tools that got tasks; [] = whole catalog

    def record(self, *, intended_tool: str, actual_tool: str) -> None:
        row = self.counts.setdefault(intended_tool, {})
        row[actual_tool] = row.get(actual_tool, 0) + 1


def undeclared_preconditions(matrix: ConfusionMatrix, *, min_rate: float = 0.3) -> list[str]:
    """Edges the model follows often whose target description never mentions the earlier tool —
    the catalog is silent about a dependency the model believes exists. Authors either state it
    or make the tool self-sufficient; either way the next run shows whether it moved."""
    findings = []
    for intended, edges in sorted(matrix.precondition_edges.items()):
        n = len(matrix.trials_by_tool.get(intended, []))
        description = matrix.descriptions.get(intended, "")
        for earlier, count in sorted(edges.items(), key=lambda kv: -kv[1]):
            if n and count / n >= min_rate and not re.search(rf"\b{re.escape(earlier)}\b", description):
                findings.append(
                    f"{intended}: models call {earlier} first in {count}/{n} trials, but {intended}'s "
                    f"description never mentions {earlier}"
                )
    return findings


def build_confusion_matrix(
    catalog: ToolCatalog,
    adapter: ModelAdapter,
    generator_client: anthropic.Anthropic,
    *,
    seeds: int = 5,
    max_steps: int = 1,
    only: set[str] | None = None,
    workers: int = 4,
) -> ConfusionMatrix:
    """`only` restricts which tools get tasks generated; the model is still offered the WHOLE
    catalog on every call, so a one-tool run measures that tool against all its neighbours."""
    matrix = ConfusionMatrix()
    matrix.model = getattr(adapter, "model", "unknown")
    matrix.generator_model = GENERATOR_MODEL
    matrix.seeds = seeds
    matrix.max_steps = max_steps
    matrix.only = sorted(only) if only is not None else []
    catalog_names = catalog.names()
    catalog_descriptions = {t.name: (t.description or "") for t in catalog.tools}
    matrix.descriptions = catalog_descriptions

    todo = [t for t in catalog.tools if only is None or t.name in only]
    work = partial(
        _evaluate_tool,
        catalog=catalog,
        adapter=adapter,
        generator_client=generator_client,
        seeds=seeds,
        max_steps=max_steps,
        catalog_names=catalog_names,
        catalog_descriptions=catalog_descriptions,
    )
    # Tools are independent: each has its own tasks and its own model calls, and nothing is
    # written to `matrix` until a tool has finished. So run them across threads (the provider
    # clients are httpx-based and thread-safe; 429s are already retried with backoff) and commit
    # the outcomes in catalog order, which keeps the report byte-for-byte deterministic for a
    # given set of model answers regardless of which thread finished first.
    if workers <= 1:
        outcomes = [work(t) for t in todo]
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            outcomes = list(pool.map(work, todo))

    for tool, outcome in zip(todo, outcomes):
        if outcome.error is not None:
            # Failure Modes (design doc, docs/designs/toolfit-v0-scope.md:103): a malformed schema
            # on one tool must not abort the whole run — flag it and exclude it from scoring. A
            # tool that failed partway through never appears in counts/trials_per_tool at all.
            matrix.schema_warnings.append(f"{tool.name}: excluded from scoring — {outcome.error}")
            continue
        matrix.leakage_warnings.extend(outcome.leakage_warnings)
        matrix.solvability_warnings.extend(outcome.solvability_warnings)
        for intended_tool, actual_tool in outcome.records:
            matrix.record(intended_tool=intended_tool, actual_tool=actual_tool)
        for trial in outcome.trials:
            if trial.via_precondition:
                row = matrix.precondition_edges.setdefault(tool.name, {})
                for earlier in dict.fromkeys(trial.preceding):
                    row[earlier] = row.get(earlier, 0) + 1
        matrix.trials_per_tool[tool.name] = seeds
        matrix.distinct_trials[tool.name] = count_distinct(outcome.sampled_args)
        matrix.trials_by_tool[tool.name] = outcome.trials

    return matrix


@dataclass
class _ToolOutcome:
    records: list[tuple[str, str]] = field(default_factory=list)
    trials: list[TrialRecord] = field(default_factory=list)
    sampled_args: list[dict] = field(default_factory=list)
    leakage_warnings: list[str] = field(default_factory=list)
    solvability_warnings: list[str] = field(default_factory=list)
    error: str | None = None  # set when the tool must be excluded (schema the sampler can't do)


def _evaluate_tool(
    tool: Tool,
    *,
    catalog: ToolCatalog,
    adapter: ModelAdapter,
    generator_client: anthropic.Anthropic,
    seeds: int,
    max_steps: int,
    catalog_names: list[str],
    catalog_descriptions: dict[str, str],
) -> _ToolOutcome:
    """All of one tool's seeds. Touches nothing shared; the caller commits the outcome."""
    out = _ToolOutcome()
    try:
        for seed in range(1, seeds + 1):
            args = sample_arguments(tool.input_schema, seed=seed)
            out.sampled_args.append(args)

            # The generator never sees the tool's name, only its description and arguments, so
            # a vague description yields a vague request ("show me the open tasks" for a
            # count tool) that no rewrite can rescue, because mutation/fix trials reuse the
            # task. When the solvability check calls the request ambiguous, regenerate with
            # its reason as a hint — bounded, and the last attempt is kept and flagged either
            # way (on a catalog with duplicate descriptions the ambiguity is the finding).
            hint: str | None = None
            for attempt in range(MAX_TASK_REGENERATIONS + 1):
                task = generate_task(
                    generator_client,
                    tool_name=tool.name,
                    tool_description=tool.description or "",
                    arguments=args,
                    ambiguity_hint=hint,
                )
                solvability = check_solvability(generator_client, task, catalog_descriptions=catalog_descriptions)
                if solvability.solvable:
                    break
                hint = solvability.reasoning

            if not check_no_leakage(task, catalog_tool_names=catalog_names):
                out.leakage_warnings.append(f"{tool.name} (seed {seed}): {task.text!r}")

            calls = run_steps(
                adapter,
                task_text=task.text,
                tools=catalog.tools,
                max_steps=max_steps,
                result_for=synthetic_result(catalog, seed=seed),
            )
            result = grade_sequence(task, calls, catalog_tool_names=catalog_names)
            if not solvability.solvable:
                # Unsolvable tasks are still graded: on a catalog with duplicate tools the
                # ambiguity IS the finding, so excluding them would hide real confusion. The
                # outcome tag lets a reader see whether a tool's failures sit on these seeds
                # (sampler's fault, e.g. head+tail) or on solvable ones (the description's).
                outcome = "passed anyway" if result.passed else "failed"
                out.solvability_warnings.append(
                    f"{tool.name} (seed {seed}, {outcome}, after {attempt} regeneration(s)): {solvability.reasoning}"
                )
            # The matrix stays intended × FIRST call so it is comparable with single-step
            # runs; the precondition edges are what explain an off-diagonal first call.
            if result.no_call:
                actual = ERROR if any(c.error for c in calls) else NO_CALL
            elif result.hallucinated:
                actual = HALLUCINATED
            else:
                actual = next(c.tool_name for c in calls if c.tool_name is not None)
            out.records.append((tool.name, actual))
            out.trials.append(
                TrialRecord(task=task, passed=result.passed, calls=calls, preceding=result.preceding, arg_diff=result.arg_diff)
            )
    except ValueError as e:
        out.error = str(e)
    return out
