"""Confusion matrix: for each tool in the catalog, generate multiple tasks and tally which tool
the model-under-test actually called against which tool was intended (design doc M1 Design §4).
The headline artifact — off-diagonal mass names the exact tool pairs to fix. Grades all pairs,
not just near-neighbor-targeted ones (design doc M1 Design §2 decision)."""

from __future__ import annotations

from dataclasses import dataclass, field

import anthropic

from toolfit.connect.client import ToolCatalog
from toolfit.gen.schema_sampler import count_distinct, sample_arguments
from toolfit.gen.taskgen import check_no_leakage, check_solvability, generate_task
from toolfit.grade.grader import grade
from toolfit.run.adapters import ModelAdapter

NO_CALL = "(no call)"
HALLUCINATED = "(hallucinated)"


@dataclass
class ConfusionMatrix:
    counts: dict[str, dict[str, int]] = field(default_factory=dict)
    distinct_trials: dict[str, int] = field(default_factory=dict)
    trials_per_tool: dict[str, int] = field(default_factory=dict)
    solvability_warnings: list[str] = field(default_factory=list)
    leakage_warnings: list[str] = field(default_factory=list)

    def record(self, *, intended_tool: str, actual_tool: str) -> None:
        row = self.counts.setdefault(intended_tool, {})
        row[actual_tool] = row.get(actual_tool, 0) + 1


def build_confusion_matrix(
    catalog: ToolCatalog,
    adapter: ModelAdapter,
    generator_client: anthropic.Anthropic,
    *,
    seeds: int = 5,
) -> ConfusionMatrix:
    matrix = ConfusionMatrix()
    catalog_names = catalog.names()
    catalog_descriptions = {t.name: (t.description or "") for t in catalog.tools}

    for tool in catalog.tools:
        sampled_args: list[dict] = []
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

            call = adapter.call_with_tools(task_text=task.text, tools=catalog.tools)
            result = grade(task, call, catalog_tool_names=catalog_names)
            if result.no_call:
                actual = NO_CALL
            elif result.hallucinated:
                actual = HALLUCINATED
            else:
                actual = call.tool_name
            matrix.record(intended_tool=tool.name, actual_tool=actual)

        matrix.trials_per_tool[tool.name] = seeds
        matrix.distinct_trials[tool.name] = count_distinct(sampled_args)

    return matrix
