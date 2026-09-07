"""Offline tests for grade/confusion.py using a fake generator client and a fake model adapter —
no API key needed. Mirrors grade/mutator.py's fake-adapter pattern (test_mutator.py)."""

from types import SimpleNamespace

from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.grade.confusion import ERROR, HALLUCINATED, MAX_TASK_REGENERATIONS, NO_CALL, build_confusion_matrix
from toolfit.run.adapters import ToolCall

_SIMPLE_SCHEMA = {
    "type": "object",
    "properties": {"title": {"type": "string", "enum": ["Write Q3 report"]}},  # pinned so fakes can match
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


def test_build_confusion_matrix_only_restricts_tasks_but_offers_the_whole_catalog():
    seen: list[int] = []

    class _CountingAdapter:
        def call_with_tools(self, *, task_text, tools):
            seen.append(len(tools))
            return ToolCall(tool_name="tool_a", arguments={"title": "x"})

    matrix = build_confusion_matrix(CATALOG, _CountingAdapter(), _fake_generator_client(), seeds=2, only={"tool_b"})
    assert set(matrix.trials_per_tool) == {"tool_b"}  # tool_a got no tasks...
    assert seen == [2, 2]  # ...but was offered on every call, so it can still steal tool_b's tasks
    assert matrix.counts["tool_b"]["tool_a"] == 2
    assert matrix.only == ["tool_b"]


def test_build_confusion_matrix_tags_unsolvable_tasks_with_their_outcome():
    def create(**kwargs):
        prompt = kwargs["messages"][0]["content"]
        text = "AMBIGUOUS: two tools fit" if "SOLVABLE" in prompt and "AMBIGUOUS" in prompt else "Write a Q3 report"
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    matrix = build_confusion_matrix(CATALOG, _AlwaysToolAAdapter(), client, seeds=1)
    # tool_a's task passed (the adapter always calls tool_a with the right title), tool_b's failed.
    assert matrix.solvability_warnings == [
        f"tool_a (seed 1, passed anyway, after {MAX_TASK_REGENERATIONS} regeneration(s)): two tools fit",
        f"tool_b (seed 1, failed, after {MAX_TASK_REGENERATIONS} regeneration(s)): two tools fit",
    ]


def test_build_confusion_matrix_regenerates_an_ambiguous_task_with_the_reason_as_a_hint():
    prompts: list[str] = []
    verdicts = iter(["AMBIGUOUS: could mean list or count", "SOLVABLE: asks for a number"])

    def create(**kwargs):
        prompt = kwargs["messages"][0]["content"]
        if "SOLVABLE" in prompt and "AMBIGUOUS" in prompt:
            text = next(verdicts)
        else:
            prompts.append(prompt)
            text = "Write a Q3 report"
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    one_tool = ToolCatalog(tools=[CATALOG.tools[0]])
    matrix = build_confusion_matrix(one_tool, _AlwaysToolAAdapter(), client, seeds=1)
    assert len(prompts) == 2  # first attempt, then one regeneration
    assert "could mean list or count" in prompts[1] and "could mean list or count" not in prompts[0]
    assert matrix.solvability_warnings == []  # the second attempt was solvable, so nothing to flag
    assert matrix.trials_per_tool["tool_a"] == 1


def test_build_confusion_matrix_gives_up_regenerating_after_the_budget_and_flags_the_attempts():
    calls = {"gen": 0}

    def create(**kwargs):
        prompt = kwargs["messages"][0]["content"]
        if "SOLVABLE" in prompt and "AMBIGUOUS" in prompt:
            text = "AMBIGUOUS: two tools are described identically"
        else:
            calls["gen"] += 1
            text = "Write a Q3 report"
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    one_tool = ToolCatalog(tools=[CATALOG.tools[0]])
    matrix = build_confusion_matrix(one_tool, _AlwaysToolAAdapter(), client, seeds=1)
    assert calls["gen"] == 1 + MAX_TASK_REGENERATIONS
    assert matrix.solvability_warnings == [
        f"tool_a (seed 1, passed anyway, after {MAX_TASK_REGENERATIONS} regeneration(s)): two tools are described identically"
    ]


def test_build_confusion_matrix_tallies_provider_errors_separately_from_no_calls():
    class _TruncatedAdapter:
        def call_with_tools(self, *, task_text, tools):
            return ToolCall(tool_name=None, arguments={}, error="truncated at max_tokens")

    matrix = build_confusion_matrix(CATALOG, _TruncatedAdapter(), _fake_generator_client(), seeds=1)
    assert matrix.counts["tool_a"] == {ERROR: 1}
    assert NO_CALL not in matrix.counts["tool_a"]


def test_malformed_arguments_with_a_tool_name_count_as_the_right_tool_with_wrong_args():
    class _MalformedArgsAdapter:
        def call_with_tools(self, *, task_text, tools):
            return ToolCall(tool_name="tool_a", arguments={}, error="malformed argument JSON")

    matrix = build_confusion_matrix(CATALOG, _MalformedArgsAdapter(), _fake_generator_client(), seeds=1)
    assert matrix.counts["tool_a"] == {"tool_a": 1}  # routing was right...
    assert matrix.trials_by_tool["tool_a"][0].passed is False  # ...the arguments were not


def test_build_confusion_matrix_with_workers_matches_sequential_and_keeps_catalog_order():
    import threading

    seen_threads: set[int] = set()

    class _ThreadRecordingAdapter:
        def call_with_tools(self, *, task_text, tools):
            seen_threads.add(threading.get_ident())
            return ToolCall(tool_name="tool_a", arguments={"title": "Write Q3 report"})

    tools = [Tool(name=f"tool_{i}", description=f"Does {i}.", inputSchema=_SIMPLE_SCHEMA) for i in range(6)]
    catalog = ToolCatalog(tools=tools)
    seq = build_confusion_matrix(catalog, _ThreadRecordingAdapter(), _fake_generator_client(), seeds=2, workers=1)
    par = build_confusion_matrix(catalog, _ThreadRecordingAdapter(), _fake_generator_client(), seeds=2, workers=4)
    assert par.counts == seq.counts and par.trials_per_tool == seq.trials_per_tool
    assert list(par.counts) == [t.name for t in tools]  # committed in catalog order, not completion order
    assert len(seen_threads) > 1


def test_build_confusion_matrix_records_arg_diff_on_trials():
    class _DropsTitle:
        def call_with_tools(self, *, task_text, tools):
            return ToolCall(tool_name="tool_a", arguments={})

    matrix = build_confusion_matrix(ToolCatalog(tools=[CATALOG.tools[0]]), _DropsTitle(), _fake_generator_client(), seeds=1)
    assert matrix.trials_by_tool["tool_a"][0].arg_diff == {"title": "missing"}


def test_build_confusion_matrix_records_deprecated_tools_from_lint():
    # Wires lint/rules.py's deprecated_tool finding into eval (Failure Attribution bucket 4) —
    # run_lint is pure/static/free, so build_confusion_matrix just calls it once, doesn't
    # reimplement the self-deprecation check.
    catalog = ToolCatalog(
        tools=[
            Tool(name="tool_a", description="DEPRECATED: use tool_b instead.", inputSchema=_SIMPLE_SCHEMA),
            Tool(name="tool_b", description="Does B.", inputSchema=_SIMPLE_SCHEMA),
        ]
    )
    matrix = build_confusion_matrix(catalog, _AlwaysToolAAdapter(), _fake_generator_client(), seeds=1)
    assert matrix.deprecated_tools == {"tool_a"}
