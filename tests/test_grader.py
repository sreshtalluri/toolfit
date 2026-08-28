from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.grader import grade
from toolfit.run.adapters import ToolCall

TASK = GeneratedTask(
    text="Add a task called Write report with high priority",
    tool_name="create_task",
    arguments={"title": "Write report", "priority": "high"},
)
CATALOG_NAMES = ["create_task", "update_task", "list_tasks"]


def test_grade_passes_on_exact_match():
    call = ToolCall(tool_name="create_task", arguments={"title": "Write report", "priority": "high"})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert result.passed


def test_grade_fails_on_wrong_tool():
    call = ToolCall(tool_name="update_task", arguments={"title": "Write report", "priority": "high"})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert not result.passed
    assert not result.correct_tool


def test_grade_fails_on_wrong_arguments():
    call = ToolCall(tool_name="create_task", arguments={"title": "Wrong title", "priority": "high"})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert not result.passed
    assert result.correct_tool
    assert not result.correct_args


def test_grade_flags_hallucinated_tool_call():
    call = ToolCall(tool_name="delete_everything", arguments={})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert result.hallucinated
    assert not result.passed


def test_grade_flags_no_call():
    call = ToolCall(tool_name=None, arguments={})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert result.no_call
    assert not result.passed
