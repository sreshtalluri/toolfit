"""Deterministic rejection-rule tests (pure function, no API key needed) plus one eval-style
quality test (Global Constraints: fix/ needs an eval suite) that requires ANTHROPIC_API_KEY."""

import os

import anthropic
import pytest

from toolfit.fix.fixer import _validate, propose_fix


def test_validate_rejects_empty_rewrite():
    result = _validate("update_task", "Add a new task.", "")
    assert result.rejected
    assert result.rejection_reason == "empty rewrite"


def test_validate_rejects_identical_rewrite():
    result = _validate("update_task", "Add a new task.", "Add a new task.")
    assert result.rejected
    assert result.rejection_reason == "identical to original"


def test_validate_rejects_too_short_rewrite():
    result = _validate("update_task", "Add a new task.", "Task.")
    assert result.rejected
    assert result.rejection_reason == "too short to be a real description"


def test_describe_parameters_lists_type_requiredness_and_enum_values():
    from toolfit.fix.fixer import _describe_parameters

    schema = {
        "type": "object",
        "properties": {
            "task_id": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "high"]},
            "notes": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        },
        "required": ["task_id", "priority"],
    }
    out = _describe_parameters(schema)
    assert out == (
        "task_id (string, required); priority (string, required, values: low, high); "
        "notes (one of string/null, optional)"
    )
    assert _describe_parameters(None) == "(none)"


def test_validate_accepts_a_real_rewrite():
    result = _validate("update_task", "Add a new task.", "Modify an existing task's title given its task_id.")
    assert not result.rejected
    assert result.rejection_reason is None


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY")
def test_propose_fix_produces_a_meaningfully_different_description():
    client = anthropic.Anthropic()
    fix = propose_fix(client, tool_name="update_task", current_description="Add a new task.", other_tool_names=["create_task", "list_tasks"])
    assert not fix.rejected
    assert fix.new_description.strip().lower() != "add a new task."
