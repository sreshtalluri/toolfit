"""Offline tests for lint/rules.py — pure functions over a hand-built catalog, no I/O, no model
calls (design doc M0 Design)."""

from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.lint.rules import run_lint

_EMPTY_SCHEMA = {"type": "object", "properties": {}}


def _catalog(*tools: Tool) -> ToolCatalog:
    return ToolCatalog(tools=list(tools))


def test_run_lint_flags_a_missing_description():
    catalog = _catalog(Tool(name="create_task", description=None, input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert any(f.rule_id == "missing_description" and f.tool_name == "create_task" for f in findings)


def test_run_lint_flags_a_whitespace_only_description():
    catalog = _catalog(Tool(name="create_task", description="   ", input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert any(f.rule_id == "missing_description" and f.tool_name == "create_task" for f in findings)


def test_run_lint_does_not_flag_a_present_description_as_missing():
    catalog = _catalog(Tool(name="create_task", description="Add a new task to the list.", input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert not any(f.rule_id == "missing_description" for f in findings)


def test_run_lint_flags_a_short_description():
    catalog = _catalog(Tool(name="create_task", description="Adds one.", input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert any(f.rule_id == "short_description" and f.tool_name == "create_task" for f in findings)


def test_run_lint_does_not_flag_a_missing_description_as_also_short():
    # missing_description already covers the empty case — short_description must not double-report it.
    catalog = _catalog(Tool(name="create_task", description=None, input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert not any(f.rule_id == "short_description" for f in findings)


def test_run_lint_does_not_flag_a_sufficiently_long_description_as_short():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task to the user's list.", input_schema=_EMPTY_SCHEMA)
    )
    findings = run_lint(catalog)
    assert not any(f.rule_id == "short_description" for f in findings)


def test_run_lint_flags_two_tools_sharing_an_identical_description():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task.", input_schema=_EMPTY_SCHEMA),
        Tool(name="update_task", description="Add a new task.", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    duplicate_findings = [f for f in findings if f.rule_id == "duplicate_description"]
    assert len(duplicate_findings) == 1
    assert duplicate_findings[0].tool_name is None
    assert "create_task" in duplicate_findings[0].message
    assert "update_task" in duplicate_findings[0].message


def test_run_lint_flags_duplicates_case_and_whitespace_insensitively():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task.", input_schema=_EMPTY_SCHEMA),
        Tool(name="update_task", description="  ADD A NEW TASK.  ", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    assert len([f for f in findings if f.rule_id == "duplicate_description"]) == 1


def test_run_lint_flags_duplicates_with_different_internal_whitespace():
    # Descriptions commonly originate from Python docstrings that get line-wrapped or
    # re-indented, producing different *internal* whitespace runs (not just leading/trailing) —
    # the normalized grouping key must collapse those too, not just casefold + strip.
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task.", input_schema=_EMPTY_SCHEMA),
        Tool(name="update_task", description="Add a  new   task.", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    assert len([f for f in findings if f.rule_id == "duplicate_description"]) == 1


def test_run_lint_does_not_flag_a_single_unique_description_as_duplicate():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task to the list.", input_schema=_EMPTY_SCHEMA),
        Tool(name="delete_task", description="Remove an existing task entirely.", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    assert not any(f.rule_id == "duplicate_description" for f in findings)


def test_run_lint_does_not_flag_two_tools_with_missing_descriptions_as_duplicates():
    # Two empty descriptions are not a meaningful "shared text" duplicate — each already gets its
    # own missing_description finding, and grouping empty strings together would be noise.
    catalog = _catalog(
        Tool(name="create_task", description=None, input_schema=_EMPTY_SCHEMA),
        Tool(name="update_task", description=None, input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    assert not any(f.rule_id == "duplicate_description" for f in findings)


def test_run_lint_groups_three_tools_sharing_one_description_into_a_single_finding():
    catalog = _catalog(
        Tool(name="a", description="Do the thing.", input_schema=_EMPTY_SCHEMA),
        Tool(name="b", description="Do the thing.", input_schema=_EMPTY_SCHEMA),
        Tool(name="c", description="Do the thing.", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    duplicate_findings = [f for f in findings if f.rule_id == "duplicate_description"]
    assert len(duplicate_findings) == 1
    assert all(name in duplicate_findings[0].message for name in ("a", "b", "c"))


def test_run_lint_flags_a_tool_that_calls_itself_deprecated():
    catalog = ToolCatalog(
        tools=[
            Tool(name="read_file", description="Read a file. DEPRECATED: Use read_text_file instead.", inputSchema={}),
            Tool(name="read_text_file", description="Read the complete contents of a file as text.", inputSchema={}),
        ]
    )
    findings = [f for f in run_lint(catalog) if f.rule_id == "deprecated_tool"]
    assert [f.tool_name for f in findings] == ["read_file"]


def test_run_lint_returns_no_findings_for_a_clean_catalog():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task to the user's list.", input_schema=_EMPTY_SCHEMA),
        Tool(name="delete_task", description="Remove an existing task from the list entirely.", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    assert findings == []
