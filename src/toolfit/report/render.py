"""Markdown-only report for the spike (design doc Next Steps #1: "Markdown output only")."""

from __future__ import annotations

from toolfit.fix.fixer import ProposedFix
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.mutator import MutationResult
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
