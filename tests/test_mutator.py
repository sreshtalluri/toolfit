import pytest
from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.confusion import ConfusionMatrix, TrialRecord
from toolfit.grade.mutator import patch_description, run_mutation_test, run_mutation_trials
from toolfit.run.adapters import ToolCall

CATALOG = ToolCatalog(
    tools=[
        Tool(
            name="create_task",
            description="Add a new task.",
            input_schema={"type": "object", "properties": {"title": {"type": "string"}, "priority": {"type": "string"}}},
        ),
        Tool(
            name="update_task",
            description="Add a new task.",
            input_schema={"type": "object", "properties": {"task_id": {"type": "string"}, "title": {"type": "string"}}},
        ),
    ]
)


def test_patch_description_replaces_only_the_named_tool():
    patched = patch_description(CATALOG, tool_name="update_task", new_description="Modify an existing task's title given its task_id.")
    assert patched.get("create_task").description == "Add a new task."
    assert patched.get("update_task").description == "Modify an existing task's title given its task_id."


def test_patch_description_does_not_mutate_the_original_catalog():
    patch_description(CATALOG, tool_name="update_task", new_description="Something else.")
    assert CATALOG.get("update_task").description == "Add a new task."


class _FakeAdapter:
    """Deterministic stand-in for a real model adapter — the mutator's own logic (re-running the
    same task before/after a patch, computing improved) is tested in isolation from real model
    behavior, which the e2e test (Task 11) covers separately with a live model."""

    def __init__(self, before_call: ToolCall, after_call: ToolCall):
        self._calls = [before_call, after_call]

    def call_with_tools(self, *, task_text, tools):
        return self._calls.pop(0)


def test_run_mutation_test_detects_improvement():
    task = GeneratedTask(text="rename task t1 to Buy milk", tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    adapter = _FakeAdapter(
        before_call=ToolCall(tool_name="create_task", arguments={"title": "Buy milk", "priority": "t1"}),  # confused with create_task
        after_call=ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"}),  # correct after the patch
    )
    result = run_mutation_test(
        adapter, task, original_catalog=CATALOG, tool_name="update_task", new_description="Modify an existing task's title given its task_id."
    )
    assert result.improved
    assert not result.before.passed
    assert result.after.passed


def test_run_mutation_test_reports_no_improvement_honestly():
    task = GeneratedTask(text="rename task t1 to Buy milk", tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    adapter = _FakeAdapter(
        before_call=ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"}),  # already correct
        after_call=ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"}),  # still correct, no delta to claim
    )
    result = run_mutation_test(
        adapter, task, original_catalog=CATALOG, tool_name="update_task", new_description="Modify an existing task's title given its task_id."
    )
    assert not result.improved  # was already passing — never suppress this into a false "improved"


def test_run_mutation_trials_reuses_matrix_trials_as_before_and_only_calls_adapter_for_after():
    task1 = GeneratedTask(
        text="rename task t1 to Buy milk", tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"}
    )
    task2 = GeneratedTask(
        text="rename task t2 to Fix bug", tool_name="update_task", arguments={"task_id": "t2", "title": "Fix bug"}
    )
    matrix = ConfusionMatrix()
    matrix.trials_by_tool["update_task"] = [
        TrialRecord(task=task1, passed=False),
        TrialRecord(task=task2, passed=False),
    ]

    class _AlwaysCorrectAfterPatch:
        def __init__(self):
            self.calls = 0  # counts every adapter invocation — used below to prove no stray
            # 'before' call happened in addition to the two expected 'after' calls.

        def call_with_tools(self, *, task_text, tools):
            self.calls += 1
            if "Buy milk" in task_text:
                return ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
            return ToolCall(tool_name="update_task", arguments={"task_id": "t2", "title": "Fix bug"})

    adapter = _AlwaysCorrectAfterPatch()
    result = run_mutation_trials(
        matrix,
        CATALOG,
        adapter,
        tool_name="update_task",
        new_description="Modify an existing task's title given its task_id.",
    )

    assert result.tool_name == "update_task"
    assert result.before_passes == [False, False]  # read straight from the matrix, not re-run
    assert result.after_passes == [True, True]
    assert adapter.calls == 2  # exactly one call per trial for 'after' — no repeat 'before' call
    assert result.p_value == 0.25  # exact test: 2 fail->pass, 0 pass->fail -> 1/2^2
    assert result.significant is False  # caller sets this after Bonferroni-correcting, not this function


def test_run_mutation_trials_raises_for_a_tool_with_no_matrix_trials():
    matrix = ConfusionMatrix()  # never ran update_task

    class _UnusedAdapter:
        def call_with_tools(self, *, task_text, tools):
            raise AssertionError("should never be called — the tool has no trials to pair against")

    with pytest.raises(KeyError):
        run_mutation_trials(
            matrix, CATALOG, _UnusedAdapter(), tool_name="update_task", new_description="Anything."
        )
