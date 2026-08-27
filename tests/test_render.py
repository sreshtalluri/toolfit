from toolfit.fix.fixer import ProposedFix
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.grader import GradeResult
from toolfit.grade.mutator import MutationResult
from toolfit.report.render import render_spike_report
from toolfit.run.adapters import ToolCall


def test_render_spike_report_includes_task_call_and_mutation_delta():
    task = GeneratedTask(text="rename task t1 to Buy milk", tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    call = ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    mutation = MutationResult(
        before=GradeResult(correct_tool=False, correct_args=False, hallucinated=False, no_call=False),
        after=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
    )
    fix = ProposedFix(
        tool_name="update_task",
        original_description="Add a new task.",
        new_description="Modify an existing task's title given its task_id.",
        rejected=False,
        rejection_reason=None,
    )
    report = render_spike_report(task=task, call=call, mutation=mutation, fix=fix)
    assert "rename task t1 to Buy milk" in report
    assert "update_task" in report
    assert "Improved: True" in report
    assert "Modify an existing task's title given its task_id." in report


def test_render_spike_report_handles_no_fix():
    task = GeneratedTask(text="x", tool_name="create_task", arguments={})
    call = ToolCall(tool_name="create_task", arguments={})
    mutation = MutationResult(
        before=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
        after=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
    )
    report = render_spike_report(task=task, call=call, mutation=mutation, fix=None)
    assert "Proposed fix" not in report


def test_render_spike_report_detects_worsened_mutation():
    task = GeneratedTask(text="delete task t5", tool_name="delete_task", arguments={"task_id": "t5"})
    call = ToolCall(tool_name="delete_task", arguments={"task_id": "t5"})
    mutation = MutationResult(
        before=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
        after=GradeResult(correct_tool=False, correct_args=False, hallucinated=False, no_call=False),
    )
    report = render_spike_report(task=task, call=call, mutation=mutation, fix=None)
    assert "Result: WORSENED" in report
    assert "Improved: False" in report
