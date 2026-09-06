"""Confusion matrix: for each tool in the catalog, generate multiple tasks and tally which tool
the model-under-test actually called against which tool was intended (design doc M1 Design §4).
The headline artifact — off-diagonal mass names the exact tool pairs to fix. Grades all pairs,
not just near-neighbor-targeted ones (design doc M1 Design §2 decision)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import anthropic

from toolfit.connect.client import ToolCatalog
from toolfit.gen.schema_sampler import count_distinct, sample_arguments
from toolfit.gen.taskgen import GENERATOR_MODEL, GeneratedTask, check_no_leakage, check_solvability, generate_task
from toolfit.grade.grader import grade_sequence
from toolfit.run.adapters import ModelAdapter, ResultFor, ToolCall, run_steps

NO_CALL = "(no call)"
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
) -> ConfusionMatrix:
    matrix = ConfusionMatrix()
    matrix.model = getattr(adapter, "model", "unknown")
    matrix.generator_model = GENERATOR_MODEL
    matrix.seeds = seeds
    matrix.max_steps = max_steps
    catalog_names = catalog.names()
    catalog_descriptions = {t.name: (t.description or "") for t in catalog.tools}
    matrix.descriptions = catalog_descriptions

    for tool in catalog.tools:
        sampled_args: list[dict] = []
        # Buffer this tool's (intended, actual) pairs and only commit them to matrix.counts —
        # atomically, with trials_per_tool/distinct_trials — once every seed for this tool has
        # completed without error. Otherwise a ValueError on a later seed (e.g. a oneOf/anyOf
        # branch that only some seeds happen to sample) would leave matrix.counts holding a
        # partial tool with no matching trials_per_tool/distinct_trials entry, which is exactly
        # what makes render_confusion_matrix's `matrix.distinct_trials[tool]` raise KeyError.
        pending_records: list[tuple[str, str]] = []
        pending_trials: list[TrialRecord] = []
        try:
            for seed in range(1, seeds + 1):
                args = sample_arguments(tool.input_schema, seed=seed)
                sampled_args.append(args)

                task = generate_task(
                    generator_client,
                    tool_name=tool.name,
                    tool_description=tool.description or "",
                    arguments=args,
                )

                if not check_no_leakage(task, catalog_tool_names=catalog_names):
                    matrix.leakage_warnings.append(f"{tool.name} (seed {seed}): {task.text!r}")

                solvability = check_solvability(generator_client, task, catalog_descriptions=catalog_descriptions)
                if not solvability.solvable:
                    matrix.solvability_warnings.append(f"{tool.name} (seed {seed}): {solvability.reasoning}")

                calls = run_steps(
                    adapter,
                    task_text=task.text,
                    tools=catalog.tools,
                    max_steps=max_steps,
                    result_for=synthetic_result(catalog, seed=seed),
                )
                result = grade_sequence(task, calls, catalog_tool_names=catalog_names)
                # The matrix stays intended × FIRST call so it is comparable with single-step
                # runs; the precondition edges below are what explain an off-diagonal first call.
                if result.no_call:
                    actual = NO_CALL
                elif result.hallucinated:
                    actual = HALLUCINATED
                else:
                    actual = next(c.tool_name for c in calls if c.tool_name is not None)
                pending_records.append((tool.name, actual))
                pending_trials.append(TrialRecord(task=task, passed=result.passed, calls=calls, preceding=result.preceding))

            for intended_tool, actual_tool in pending_records:
                matrix.record(intended_tool=intended_tool, actual_tool=actual_tool)
            for trial in pending_trials:
                if trial.via_precondition:
                    row = matrix.precondition_edges.setdefault(tool.name, {})
                    for earlier in dict.fromkeys(trial.preceding):
                        row[earlier] = row.get(earlier, 0) + 1
            matrix.trials_per_tool[tool.name] = seeds
            matrix.distinct_trials[tool.name] = count_distinct(sampled_args)
            matrix.trials_by_tool[tool.name] = pending_trials
        except ValueError as e:
            # Failure Modes (design doc, docs/designs/toolfit-v0-scope.md:103): a malformed schema
            # on one tool must not abort the whole run — flag it and exclude it from scoring,
            # leave every other tool in the catalog to be processed normally. pending_records is
            # simply discarded here (never committed to matrix.counts) so a tool that failed
            # partway through never appears in counts/trials_per_tool/distinct_trials at all.
            matrix.schema_warnings.append(f"{tool.name}: excluded from scoring — {e}")
            continue

    return matrix
