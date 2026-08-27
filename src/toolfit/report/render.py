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
) -> str:
    lines = [
        "# toolfit spike report",
        "",
        "## Task",
        f"- Generated request: {task.text!r}",
        f"- Ground truth: `{task.tool_name}({task.arguments})`",
        f"- Model called: `{call.tool_name}({call.arguments})`",
        "",
        "## Mutation test",
        f"- Before: correct_tool={mutation.before.correct_tool}, correct_args={mutation.before.correct_args}, hallucinated={mutation.before.hallucinated}",
        f"- After:  correct_tool={mutation.after.correct_tool}, correct_args={mutation.after.correct_args}, hallucinated={mutation.after.hallucinated}",
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
    return "\n".join(lines)
