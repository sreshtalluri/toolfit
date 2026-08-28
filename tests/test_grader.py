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


def test_grade_treats_different_date_formats_as_equal():
    task = GeneratedTask(text="...", tool_name="create_reminder", arguments={"remind_at": "2026-03-05"})
    call = ToolCall(tool_name="create_reminder", arguments={"remind_at": "03/05/2026"})
    result = grade(task, call, catalog_tool_names=["create_reminder"])
    assert result.passed


def test_grade_treats_array_order_as_insignificant():
    task = GeneratedTask(text="...", tool_name="create_reminder", arguments={"notify_channels": ["email", "sms"]})
    call = ToolCall(tool_name="create_reminder", arguments={"notify_channels": ["sms", "email"]})
    result = grade(task, call, catalog_tool_names=["create_reminder"])
    assert result.passed


def test_grade_folds_case_and_whitespace_for_string_arguments():
    task = GeneratedTask(text="...", tool_name="update_task", arguments={"title": "Book dentist"})
    call = ToolCall(tool_name="update_task", arguments={"title": "  BOOK DENTIST  "})
    result = grade(task, call, catalog_tool_names=["update_task"])
    assert result.passed


def test_grade_still_fails_on_genuinely_different_arguments():
    task = GeneratedTask(text="...", tool_name="update_task", arguments={"title": "Book dentist"})
    call = ToolCall(tool_name="update_task", arguments={"title": "Buy milk"})
    result = grade(task, call, catalog_tool_names=["update_task"])
    assert not result.passed


def test_grade_still_distinguishes_different_times_on_the_same_date():
    task = GeneratedTask(
        text="...", tool_name="create_reminder", arguments={"remind_at": "2026-03-05T14:00:00"}
    )
    call = ToolCall(tool_name="create_reminder", arguments={"remind_at": "2026-03-05T09:30:00"})
    result = grade(task, call, catalog_tool_names=["create_reminder"])
    assert not result.passed
