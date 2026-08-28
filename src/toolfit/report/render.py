"""Markdown-only report for the spike (design doc Next Steps #1: "Markdown output only")."""

from __future__ import annotations

from toolfit.fix.fixer import ProposedFix
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.confusion import HALLUCINATED, NO_CALL, ConfusionMatrix
from toolfit.grade.mutator import MutationResult
from toolfit.grade.significance import wilson_interval
from toolfit.run.adapters import ToolCall


def render_spike_report(
    *,
    task: GeneratedTask,
    call: ToolCall,
    mutation: MutationResult,
    fix: ProposedFix | None,
    after_description: str,
    model: str = "claude-sonnet-5",
    seed: int,
) -> str:
    # Compute tri-state result label: IMPROVED, WORSENED, or UNCHANGED
    if mutation.improved:
        result_label = "IMPROVED"
    elif mutation.before.passed and not mutation.after.passed:
        result_label = "WORSENED"
    else:
        result_label = "UNCHANGED"

    lines = [
        "# toolfit spike report",
        "",
        "## Task",
        f"- Generated request: {task.text!r}",
        f"- Ground truth: `{task.tool_name}({task.arguments})`",
        f"- Model called: `{call.tool_name}({call.arguments})`",
        "",
        "## Mutation test",
    ]
    if fix is not None and fix.rejected:
        # Without this, a rejected fix (new_description patched back to the original) still
        # produces a guaranteed "Result: UNCHANGED" that reads like "we tried a fix and it
        # didn't help" — when no real fix was ever tested at all.
        lines.append(
            f"- Note: fix was rejected ({fix.rejection_reason}), mutation test below re-measures "
            "the ORIGINAL unchanged description, not a real fix"
        )
    lines += [
        f"- Description used for 'after': {after_description!r}",
        f"- Before: correct_tool={mutation.before.correct_tool}, correct_args={mutation.before.correct_args}, hallucinated={mutation.before.hallucinated}",
        f"- After:  correct_tool={mutation.after.correct_tool}, correct_args={mutation.after.correct_args}, hallucinated={mutation.after.hallucinated}",
        f"- Result: {result_label}",
        f"- Improved: {mutation.improved}",
    ]
    if fix is not None:
        lines += [
            "",
            "## Proposed fix",
            f"- Tool: {fix.tool_name}",
            f"- Original: {fix.original_description!r}",
            f"- Proposed: {fix.new_description!r}",
            f"- Rejected: {fix.rejected}" + (f" ({fix.rejection_reason})" if fix.rejected else ""),
        ]
    lines += [
        "",
        "## Metadata",
        f"- Model: {model}",
        f"- Seed: {seed}",
    ]
    return "\n".join(lines)


def render_confusion_matrix(matrix: ConfusionMatrix) -> str:
    tools = sorted(matrix.counts.keys())
    actual_values = {actual for row in matrix.counts.values() for actual in row}
    ordered_columns = sorted((actual_values | set(tools)) - {NO_CALL, HALLUCINATED})
    for special in (NO_CALL, HALLUCINATED):
        if special in actual_values:
            ordered_columns.append(special)

    lines = ["## Confusion Matrix", "", "| Intended \\ Called | " + " | ".join(ordered_columns) + " |"]
    lines.append("|---" * (len(ordered_columns) + 1) + "|")
    for tool in tools:
        row = [str(matrix.counts[tool].get(col, 0)) for col in ordered_columns]
        lines.append(f"| {tool} | " + " | ".join(row) + " |")

    lines += ["", "## Trial Diversity"]
    for tool in tools:
        distinct = matrix.distinct_trials[tool]
        total = matrix.trials_per_tool[tool]
        note = " (some seeds sampled identical arguments)" if distinct < total else ""
        lines.append(f"- {tool}: {distinct}/{total} distinct{note}")

    pass_rate_lines: list[str] = []
    for tool in tools:
        trials = matrix.trials_by_tool.get(tool, [])
        if not trials:
            continue
        passed = sum(1 for t in trials if t.passed)
        total = len(trials)
        lo, hi = wilson_interval(passed, total)
        pass_rate_lines.append(f"- {tool}: {passed}/{total} ({passed / total:.0%}), 95% CI [{lo:.0%}, {hi:.0%}]")
    if pass_rate_lines:
        lines += ["", "## Pass Rates"] + pass_rate_lines

    if matrix.leakage_warnings:
        lines += ["", "## Leakage Warnings"] + [f"- {w}" for w in matrix.leakage_warnings]
    if matrix.solvability_warnings:
        lines += ["", "## Solvability Warnings"] + [f"- {w}" for w in matrix.solvability_warnings]
    if matrix.schema_warnings:
        lines += ["", "## Schema Warnings"] + [f"- {w}" for w in matrix.schema_warnings]

    lines += [
        "",
        "## Metadata",
        f"- Model under test: {matrix.model}",
        f"- Generator model: {matrix.generator_model}",
        f"- Seeds per tool: {matrix.seeds}",
    ]

    return "\n".join(lines)
