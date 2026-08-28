"""Offline tests for grade/confusion.py using a fake generator client and a fake model adapter —
no API key needed. Mirrors grade/mutator.py's fake-adapter pattern (test_mutator.py)."""

from types import SimpleNamespace

from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.grade.confusion import HALLUCINATED, NO_CALL, build_confusion_matrix
from toolfit.run.adapters import ToolCall

_SIMPLE_SCHEMA = {
    "type": "object",
    "properties": {"title": {"type": "string"}},
    "required": ["title"],
}

CATALOG = ToolCatalog(
    tools=[
        Tool(name="tool_a", description="Does A.", inputSchema=_SIMPLE_SCHEMA),
        Tool(name="tool_b", description="Does B.", inputSchema=_SIMPLE_SCHEMA),
    ]
)


class _AlwaysToolAAdapter:
    """Always calls tool_a, regardless of the task — deterministic for testing the matrix's
    tallying logic, not real model behavior."""

    def call_with_tools(self, *, task_text, tools):
        return ToolCall(tool_name="tool_a", arguments={"title": "Write Q3 report"})


def _fake_generator_client():
    """Fake Anthropic client covering both prompts taskgen.py sends: generate_task's task-writing
    prompt, and check_solvability's judgment prompt (distinguished by the literal "SOLVABLE"/
    "AMBIGUOUS" instruction text that only the solvability prompt template contains)."""

    def create(**kwargs):
        prompt = kwargs["messages"][0]["content"]
        if "SOLVABLE" in prompt and "AMBIGUOUS" in prompt:
            text = "SOLVABLE: clear from context"
        else:
            text = "Write a Q3 report"
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])

    return SimpleNamespace(messages=SimpleNamespace(create=create))


def test_build_confusion_matrix_tallies_calls_per_intended_tool():
    matrix = build_confusion_matrix(CATALOG, _AlwaysToolAAdapter(), _fake_generator_client(), seeds=2)
    assert matrix.counts["tool_a"]["tool_a"] == 2
    assert matrix.counts["tool_b"]["tool_a"] == 2  # all of tool_b's tasks got misrouted to tool_a
    assert matrix.trials_per_tool["tool_a"] == 2
    assert matrix.trials_per_tool["tool_b"] == 2


def test_build_confusion_matrix_records_no_call():
    class _NoCallAdapter:
        def call_with_tools(self, *, task_text, tools):
            return ToolCall(tool_name=None, arguments={})

    matrix = build_confusion_matrix(CATALOG, _NoCallAdapter(), _fake_generator_client(), seeds=1)
    assert matrix.counts["tool_a"][NO_CALL] == 1
    assert matrix.counts["tool_b"][NO_CALL] == 1


def test_build_confusion_matrix_records_hallucination():
    class _HallucinatingAdapter:
        def call_with_tools(self, *, task_text, tools):
            return ToolCall(tool_name="nonexistent_tool", arguments={})

    matrix = build_confusion_matrix(CATALOG, _HallucinatingAdapter(), _fake_generator_client(), seeds=1)
    assert matrix.counts["tool_a"][HALLUCINATED] == 1


def test_build_confusion_matrix_tracks_distinct_trials():
    matrix = build_confusion_matrix(CATALOG, _AlwaysToolAAdapter(), _fake_generator_client(), seeds=2)
    assert matrix.distinct_trials["tool_a"] <= matrix.trials_per_tool["tool_a"]
    assert "tool_a" in matrix.distinct_trials
    assert "tool_b" in matrix.distinct_trials
