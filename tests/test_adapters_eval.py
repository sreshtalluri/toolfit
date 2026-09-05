"""Eval-style test for OpenAIAdapter/build_adapter — makes a real OpenAI API call, same skip
pattern as tests/test_taskgen_eval.py (skipped cleanly without a key, never a hard failure)."""

import os

import pytest
from mcp.types import Tool

from toolfit.run.adapters import build_adapter

pytestmark = pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="requires OPENAI_API_KEY")

TOOLS = [
    Tool(
        name="create_task",
        description="Add a new task.",
        input_schema={"type": "object", "properties": {"title": {"type": "string"}, "priority": {"type": "string"}}},
    ),
    Tool(
        name="list_tasks",
        description="Get tasks by status.",
        input_schema={"type": "object", "properties": {"status": {"type": "string"}}},
    ),
]


def test_openai_adapter_calls_the_right_tool_for_a_clear_request():
    adapter = build_adapter("gpt-5.5")
    result = adapter.call_with_tools(
        task_text="Create a task to write the Q3 report, high priority.", tools=TOOLS
    )
    assert result.tool_name == "create_task"
    assert "report" in result.arguments.get("title", "").lower()
