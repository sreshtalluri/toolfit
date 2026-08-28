from toolfit.fix.fixer import ProposedFix
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.confusion import ConfusionMatrix, TrialRecord
from toolfit.grade.grader import GradeResult
from toolfit.grade.mutator import MutationResult
from toolfit.report.render import render_confusion_matrix, render_spike_report
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
    report = render_spike_report(
        task=task,
        call=call,
        mutation=mutation,
        fix=fix,
        after_description="Modify an existing task's title given its task_id.",
        model="claude-sonnet-5",
        seed=1,
    )
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
    report = render_spike_report(
        task=task,
        call=call,
        mutation=mutation,
        fix=None,
        after_description="Create a new task with the given title and priority.",
        model="claude-sonnet-5",
        seed=1,
    )
    assert "Proposed fix" not in report


def test_render_spike_report_detects_worsened_mutation():
    task = GeneratedTask(text="delete task t5", tool_name="delete_task", arguments={"task_id": "t5"})
    call = ToolCall(tool_name="delete_task", arguments={"task_id": "t5"})
    mutation = MutationResult(
        before=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
        after=GradeResult(correct_tool=False, correct_args=False, hallucinated=False, no_call=False),
    )
    report = render_spike_report(
        task=task,
        call=call,
        mutation=mutation,
        fix=None,
        after_description="Delete a task by its task_id.",
        model="claude-sonnet-5",
        seed=1,
    )
    assert "Result: WORSENED" in report
    assert "Improved: False" in report


def test_render_spike_report_notes_when_fix_was_rejected_and_includes_metadata():
    # Fix 4(b)/(c): a rejected fix must not read like a real fix was measured, and the report
    # must carry enough metadata (model, seed) for someone else to reproduce the result.
    task = GeneratedTask(text="rename task t1 to Buy milk", tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    call = ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    mutation = MutationResult(
        before=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
        after=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
    )
    fix = ProposedFix(
        tool_name="update_task",
        original_description="Add a new task.",
        new_description="Add a new task.",
        rejected=True,
        rejection_reason="identical to original",
    )
    report = render_spike_report(
        task=task,
        call=call,
        mutation=mutation,
        fix=fix,
        after_description="Add a new task.",
        model="claude-sonnet-5",
        seed=7,
    )
    assert (
        "Note: fix was rejected (identical to original), mutation test below re-measures the "
        "ORIGINAL unchanged description, not a real fix" in report
    )
    assert "Description used for 'after': 'Add a new task.'" in report
    assert "## Metadata" in report
    assert "- Model: claude-sonnet-5" in report
    assert "- Seed: 7" in report


def test_render_confusion_matrix_shows_off_diagonal_mass():
    matrix = ConfusionMatrix()
    matrix.record(intended_tool="tool_a", actual_tool="tool_a")
    matrix.record(intended_tool="tool_a", actual_tool="tool_b")
    matrix.record(intended_tool="tool_b", actual_tool="tool_b")
    matrix.trials_per_tool = {"tool_a": 2, "tool_b": 1}
    matrix.distinct_trials = {"tool_a": 2, "tool_b": 1}

    report = render_confusion_matrix(matrix)

    assert "Confusion Matrix" in report
    assert "| tool_a | 1 | 1 |" in report
    assert "| tool_b | 0 | 1 |" in report


def test_render_confusion_matrix_notes_collided_trials():
    matrix = ConfusionMatrix()
    matrix.record(intended_tool="tool_a", actual_tool="tool_a")
    matrix.trials_per_tool = {"tool_a": 3}
    matrix.distinct_trials = {"tool_a": 2}  # collision: fewer distinct than total

    report = render_confusion_matrix(matrix)

    assert "2/3 distinct" in report
    assert "some seeds sampled identical arguments" in report


def test_render_confusion_matrix_includes_warnings():
    matrix = ConfusionMatrix()
    matrix.record(intended_tool="tool_a", actual_tool="tool_a")
    matrix.trials_per_tool = {"tool_a": 1}
    matrix.distinct_trials = {"tool_a": 1}
    matrix.leakage_warnings = ["tool_a (seed 1): 'leaked text'"]
    matrix.solvability_warnings = ["tool_a (seed 1): ambiguous reasoning"]

    report = render_confusion_matrix(matrix)

    assert "Leakage Warnings" in report
    assert "Solvability Warnings" in report
    assert "leaked text" in report


def test_render_confusion_matrix_includes_schema_warnings():
    matrix = ConfusionMatrix()
    matrix.record(intended_tool="tool_a", actual_tool="tool_a")
    matrix.trials_per_tool = {"tool_a": 1}
    matrix.distinct_trials = {"tool_a": 1}
    matrix.schema_warnings = ["tool_a: excluded from scoring — unsupported $ref construct"]

    report = render_confusion_matrix(matrix)

    assert "Schema Warnings" in report
    assert "excluded from scoring" in report


def test_render_confusion_matrix_includes_metadata():
    matrix = ConfusionMatrix()
    matrix.record(intended_tool="tool_a", actual_tool="tool_a")
    matrix.trials_per_tool = {"tool_a": 1}
    matrix.distinct_trials = {"tool_a": 1}
    matrix.model = "claude-sonnet-5"
    matrix.generator_model = "claude-sonnet-5"
    matrix.seeds = 5
    report = render_confusion_matrix(matrix)
    assert "Model under test: claude-sonnet-5" in report
    assert "Seeds per tool: 5" in report


def test_render_confusion_matrix_includes_pass_rates_with_confidence_interval():
    matrix = ConfusionMatrix()
    matrix.record(intended_tool="tool_a", actual_tool="tool_a")
    matrix.record(intended_tool="tool_a", actual_tool="tool_a")
    matrix.trials_per_tool = {"tool_a": 2}
    matrix.distinct_trials = {"tool_a": 2}
    matrix.trials_by_tool = {
        "tool_a": [
            TrialRecord(task=GeneratedTask(text="x", tool_name="tool_a", arguments={}), passed=True),
            TrialRecord(task=GeneratedTask(text="y", tool_name="tool_a", arguments={}), passed=False),
        ]
    }

    report = render_confusion_matrix(matrix)

    assert "## Pass Rates" in report
    assert "tool_a: 1/2 (50%)" in report
    assert "95% CI" in report


def test_render_confusion_matrix_omits_pass_rates_section_when_no_trial_data_is_present():
    # Matches the existing hand-built ConfusionMatrix() fixtures used elsewhere in this file,
    # which set counts/trials_per_tool/distinct_trials directly without trials_by_tool.
    matrix = ConfusionMatrix()
    matrix.record(intended_tool="tool_a", actual_tool="tool_a")
    matrix.trials_per_tool = {"tool_a": 1}
    matrix.distinct_trials = {"tool_a": 1}

    report = render_confusion_matrix(matrix)

    assert "## Pass Rates" not in report


def test_render_mutation_results_shows_before_after_and_verdict():
    from toolfit.grade.mutator import MutationTrialResult
    from toolfit.report.render import render_mutation_results

    result = MutationTrialResult(
        tool_name="update_task",
        new_description="Modify an existing task's title given its task_id.",
        before_passes=[False, False, True],
        after_passes=[True, True, True],
        p_value=0.02,
        significant=True,
    )

    report = render_mutation_results([result])

    assert "## Mutation Results" in report
    assert "update_task" in report
    assert "Modify an existing task's title given its task_id." in report
    assert "Before: 1/3 (33%)" in report
    assert "After:  3/3 (100%)" in report
    assert "p-value: 0.0200" in report
    assert "SIGNIFICANT" in report


def test_render_mutation_results_shows_not_significant_when_correction_rejects_it():
    from toolfit.grade.mutator import MutationTrialResult
    from toolfit.report.render import render_mutation_results

    result = MutationTrialResult(
        tool_name="update_task",
        new_description="x",
        before_passes=[False],
        after_passes=[True],
        p_value=0.04,
        significant=False,
    )

    report = render_mutation_results([result])

    assert "not significant" in report
