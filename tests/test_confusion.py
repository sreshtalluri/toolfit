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


def test_build_confusion_matrix_excludes_a_tool_with_an_unsupported_schema_but_keeps_going():
    # sample_arguments (gen/schema_sampler.py) raises ValueError on schema constructs outside the
    # M1 subset — e.g. "$ref" — by design. One tool's broken schema must not abort the whole run
    # (design doc Failure Modes, docs/designs/toolfit-v0-scope.md:103): it should be flagged and
    # excluded, while the rest of the catalog is still scored normally.
    broken_schema = {
        "type": "object",
        "properties": {"thing": {"$ref": "#/definitions/Thing"}},
        "required": ["thing"],
    }
    catalog = ToolCatalog(
        tools=[
            Tool(name="tool_a", description="Does A.", inputSchema=_SIMPLE_SCHEMA),
            Tool(name="tool_broken", description="Has a bad schema.", inputSchema=broken_schema),
        ]
    )

    matrix = build_confusion_matrix(catalog, _AlwaysToolAAdapter(), _fake_generator_client(), seeds=2)

    assert matrix.counts["tool_a"]["tool_a"] == 2
    assert matrix.trials_per_tool["tool_a"] == 2
    assert "tool_a" in matrix.distinct_trials

    assert "tool_broken" not in matrix.counts
    assert "tool_broken" not in matrix.trials_per_tool
    assert "tool_broken" not in matrix.distinct_trials
    assert len(matrix.schema_warnings) == 1
    assert "tool_broken" in matrix.schema_warnings[0]


def test_build_confusion_matrix_excludes_a_tool_that_fails_partway_through_its_seed_loop():
    # Fix 1: a tool whose schema only fails on a LATER seed (not the first one) must still be
    # excluded atomically — it must not leave partial entries in matrix.counts with no matching
    # trials_per_tool/distinct_trials, which is what previously produced a KeyError in
    # render_confusion_matrix downstream.
    flaky_schema = {
        "type": "object",
        "properties": {"thing": {"oneOf": [{"type": "string"}, {"$ref": "#/definitions/Thing"}]}},
        "required": ["thing"],
    }
    catalog = ToolCatalog(
        tools=[
            Tool(name="tool_a", description="Does A.", inputSchema=_SIMPLE_SCHEMA),
            Tool(name="tool_flaky", description="Sometimes breaks.", inputSchema=flaky_schema),
        ]
    )

    # seed=1 picks the plain-string branch (succeeds); a later seed picks the $ref branch (fails).
    matrix = build_confusion_matrix(catalog, _AlwaysToolAAdapter(), _fake_generator_client(), seeds=5)

    assert "tool_flaky" not in matrix.counts
    assert "tool_flaky" not in matrix.trials_per_tool
    assert "tool_flaky" not in matrix.distinct_trials
    assert any("tool_flaky" in w for w in matrix.schema_warnings)

    from toolfit.report.render import render_confusion_matrix

    render_confusion_matrix(matrix)  # must not raise


def test_build_confusion_matrix_records_run_metadata():
    matrix = build_confusion_matrix(CATALOG, _AlwaysToolAAdapter(), _fake_generator_client(), seeds=2)
    assert matrix.seeds == 2
    assert matrix.generator_model


def test_build_confusion_matrix_records_paired_trials_for_mutation_testing():
    matrix = build_confusion_matrix(CATALOG, _AlwaysToolAAdapter(), _fake_generator_client(), seeds=2)

    assert len(matrix.trials_by_tool["tool_a"]) == 2
    for trial in matrix.trials_by_tool["tool_a"]:
        assert trial.task.tool_name == "tool_a"  # ground truth, not what was actually called
        assert trial.passed is True  # _AlwaysToolAAdapter always gets tool_a's own tasks right

    assert len(matrix.trials_by_tool["tool_b"]) == 2
    for trial in matrix.trials_by_tool["tool_b"]:
        assert trial.task.tool_name == "tool_b"
        assert trial.passed is False  # tool_b's tasks got misrouted to tool_a


def test_build_confusion_matrix_excludes_a_broken_tool_from_trials_by_tool_too():
    broken_schema = {
        "type": "object",
        "properties": {"thing": {"$ref": "#/definitions/Thing"}},
        "required": ["thing"],
    }
    catalog = ToolCatalog(
        tools=[
            Tool(name="tool_a", description="Does A.", inputSchema=_SIMPLE_SCHEMA),
            Tool(name="tool_broken", description="Has a bad schema.", inputSchema=broken_schema),
        ]
    )
    matrix = build_confusion_matrix(catalog, _AlwaysToolAAdapter(), _fake_generator_client(), seeds=2)
    assert "tool_a" in matrix.trials_by_tool
    assert "tool_broken" not in matrix.trials_by_tool
