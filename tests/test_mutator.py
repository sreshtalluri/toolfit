from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.mutator import patch_description, run_mutation_test
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
