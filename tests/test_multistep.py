"""Offline tests for M5: multi-step trials, sequence grading, the observed precondition graph, and
its rendering. Fake clients/adapters only — no API key."""

import json
from types import SimpleNamespace

from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.confusion import ConfusionMatrix, build_confusion_matrix, synthetic_result, undeclared_preconditions
from toolfit.grade.grader import grade_sequence
from toolfit.grade.mutator import run_mutation_trials
from toolfit.report.render import render_confusion_matrix, render_mutation_results
from toolfit.run.adapters import AnthropicAdapter, OpenAIAdapter, ToolCall, run_steps

_SCHEMA = {"type": "object", "properties": {"repo_path": {"type": "string"}}, "required": ["repo_path"]}


def _catalog() -> ToolCatalog:
    return ToolCatalog(
        tools=[
            Tool(name="git_add", description="Stage files.", inputSchema=_SCHEMA),
            Tool(name="git_commit", description="Records changes to the repository.", inputSchema=_SCHEMA),
            Tool(name="git_status", description="Shows the working tree status.", inputSchema=_SCHEMA),
        ]
    )


def _task(tool="git_commit"):
    return GeneratedTask(text=f"do {tool}", tool_name=tool, arguments={"repo_path": "/r"})


# --- grading ---------------------------------------------------------------------------------


def test_grade_sequence_passes_anywhere_and_records_the_precondition_path():
    calls = [ToolCall("git_status", {"repo_path": "/r"}), ToolCall("git_add", {"repo_path": "/r"}), ToolCall("git_commit", {"repo_path": "/r"})]
    r = grade_sequence(_task(), calls, catalog_tool_names=["git_add", "git_commit", "git_status"])
    assert r.passed and r.steps_to_correct == 3 and r.preceding == ["git_status", "git_add"]
    assert r.via_precondition


def test_grade_sequence_single_call_matches_the_old_rule():
    names = ["git_add", "git_commit"]
    assert grade_sequence(_task(), [ToolCall("git_commit", {"repo_path": "/r"})], catalog_tool_names=names).passed
    assert not grade_sequence(_task(), [ToolCall("git_commit", {"repo_path": "/r"})], catalog_tool_names=names).via_precondition
    miss = grade_sequence(_task(), [ToolCall("git_add", {"repo_path": "/r"})], catalog_tool_names=names)
    assert not miss.passed and not miss.correct_tool and not miss.hallucinated
    assert grade_sequence(_task(), [ToolCall("nope", {})], catalog_tool_names=names).hallucinated
    assert grade_sequence(_task(), [], catalog_tool_names=names).no_call
    assert grade_sequence(_task(), [ToolCall(None, {})], catalog_tool_names=names).no_call


def test_grade_sequence_right_tool_wrong_args_then_right_args_passes_on_the_later_call():
    calls = [ToolCall("git_commit", {"repo_path": "/wrong"}), ToolCall("git_commit", {"repo_path": "/r"})]
    r = grade_sequence(_task(), calls, catalog_tool_names=["git_commit"])
    assert r.passed and r.steps_to_correct == 2
    assert r.preceding == [] and not r.via_precondition  # a retry is not a precondition


def test_grade_sequence_preceding_excludes_retries_and_hallucinated_names():
    calls = [
        ToolCall("git_commit", {"repo_path": "/wrong"}),
        ToolCall("ghost", {}),
        ToolCall("git_add", {"repo_path": "/r"}),
        ToolCall("git_commit", {"repo_path": "/r"}),
    ]
    r = grade_sequence(_task(), calls, catalog_tool_names=["git_add", "git_commit"])
    assert r.passed and r.steps_to_correct == 4 and r.preceding == ["git_add"]


# --- adapters --------------------------------------------------------------------------------


def _anthropic_client(script):
    """script: list of responses; each is a list of (name, input) tool_use blocks or [] for text."""
    sent = []

    def create(**kwargs):
        sent.append(kwargs["messages"])
        blocks = script.pop(0)
        content = [SimpleNamespace(type="tool_use", id=f"id{i}", name=n, input=a) for i, (n, a) in enumerate(blocks)] or [
            SimpleNamespace(type="text", text="done")
        ]
        return SimpleNamespace(content=content, stop_reason="tool_use" if blocks else "end_turn")

    return SimpleNamespace(messages=SimpleNamespace(create=create)), sent


def test_anthropic_run_chains_calls_and_feeds_synthetic_results_back():
    client, sent = _anthropic_client([[("git_add", {"repo_path": "/r"})], [("git_commit", {"repo_path": "/r"})], []])
    adapter = AnthropicAdapter(client, model="m")
    calls = adapter.run(task_text="commit", tools=_catalog().tools, max_steps=3, result_for=lambda c: {"ok": True, "for": c.tool_name})
    assert [c.tool_name for c in calls] == ["git_add", "git_commit"]
    # Second request carried the assistant turn (rebuilt from API-accepted fields only) plus a
    # tool_result for git_add.
    second = sent[1]
    assert second[1]["role"] == "assistant"
    assert second[1]["content"] == [{"type": "tool_use", "id": "id0", "name": "git_add", "input": {"repo_path": "/r"}}]
    result_block = second[2]["content"][0]
    assert result_block["type"] == "tool_result" and result_block["tool_use_id"] == "id0"
    assert json.loads(result_block["content"]) == {"ok": True, "for": "git_add"}


def test_anthropic_run_stops_at_max_steps_and_counts_parallel_blocks():
    client, _ = _anthropic_client([[("git_status", {}), ("git_add", {})], [("git_commit", {})]])
    calls = AnthropicAdapter(client, model="m").run(task_text="x", tools=_catalog().tools, max_steps=2, result_for=lambda c: {})
    assert [c.tool_name for c in calls] == ["git_status", "git_add"]  # second response never requested


def test_openai_run_uses_role_tool_messages():
    sent = []
    script = [
        [("git_add", '{"repo_path": "/r"}')],
        [("git_commit", '{"repo_path": "/r"}')],
        [],
    ]

    def create(**kwargs):
        sent.append(kwargs["messages"])
        tcs = [
            SimpleNamespace(id=f"c{i}", function=SimpleNamespace(name=n, arguments=a)) for i, (n, a) in enumerate(script.pop(0))
        ]
        message = SimpleNamespace(content=None, tool_calls=tcs or None)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    calls = OpenAIAdapter(client, model="gpt").run(task_text="commit", tools=_catalog().tools, max_steps=3, result_for=lambda c: {"ok": True})
    assert [c.tool_name for c in calls] == ["git_add", "git_commit"]
    assert sent[1][1]["role"] == "assistant" and sent[1][1]["tool_calls"][0]["id"] == "c0"
    assert sent[1][2] == {"role": "tool", "tool_call_id": "c0", "content": '{"ok": true}'}


def test_run_steps_falls_back_to_single_call_for_adapters_without_run():
    fake = SimpleNamespace(call_with_tools=lambda *, task_text, tools: ToolCall("git_commit", {"repo_path": "/r"}))
    assert [c.tool_name for c in run_steps(fake, task_text="x", tools=[], max_steps=3, result_for=lambda c: {})] == ["git_commit"]
    none = SimpleNamespace(call_with_tools=lambda *, task_text, tools: ToolCall(None, {}))
    assert run_steps(none, task_text="x", tools=[], max_steps=3, result_for=lambda c: {}) == []


def test_synthetic_result_samples_output_schema_or_stubs():
    tool = Tool(
        name="git_status",
        description="d",
        inputSchema=_SCHEMA,
        outputSchema={"type": "object", "properties": {"clean": {"type": "boolean"}}, "required": ["clean"]},
    )
    catalog = ToolCatalog(tools=[tool, _catalog().tools[0]])
    rf = synthetic_result(catalog, seed=1)
    assert set(rf(ToolCall("git_status", {}))) == {"clean"}
    assert rf(ToolCall("git_add", {})) == {"ok": True}
    assert rf(ToolCall("unknown", {})) == {"ok": True}


# --- matrix + report -------------------------------------------------------------------------


class _StagesFirst:
    """Scripted model that always stages before committing: for git_commit tasks it calls git_add
    then git_commit (with the task's own arguments); other tools it calls directly. Task text is
    `do <tool> <json args>` (see _matrix_multistep), so the fake can echo the sampled arguments."""

    model = "fake"

    @staticmethod
    def _plan(task_text):
        _, target, raw = task_text.split(" ", 2)
        args = json.loads(raw)
        seq = [ToolCall("git_add", {"repo_path": args["repo_path"]})] if target == "git_commit" else []
        seq.append(ToolCall(target, args))
        return seq

    def call_with_tools(self, *, task_text, tools):
        return self._plan(task_text)[0]  # single-step: the model's FIRST call, i.e. git_add

    def run(self, *, task_text, tools, max_steps, result_for):
        return self._plan(task_text)[:max_steps]


def _matrix_multistep(max_steps, monkeypatch):
    # Bypass the LLM generator: the task text carries the intended tool and sampled arguments so
    # the scripted adapter can act on them; the solvability check is stubbed as solvable.
    import toolfit.grade.confusion as confusion

    monkeypatch.setattr(
        confusion,
        "generate_task",
        lambda client, *, tool_name, tool_description, arguments: GeneratedTask(
            text=f"do {tool_name} {json.dumps(arguments)}", tool_name=tool_name, arguments=arguments
        ),
    )
    monkeypatch.setattr(
        confusion, "check_solvability", lambda client, task, *, catalog_descriptions: SimpleNamespace(solvable=True, reasoning="")
    )
    return build_confusion_matrix(_catalog(), _StagesFirst(), SimpleNamespace(), seeds=4, max_steps=max_steps)


def test_multistep_matrix_records_first_call_and_precondition_edges(monkeypatch):
    m = _matrix_multistep(3, monkeypatch)
    assert m.counts["git_commit"] == {"git_add": 4}  # matrix stays intended × first call
    assert all(t.passed for t in m.trials_by_tool["git_commit"])  # ...but the trials pass
    assert m.precondition_edges == {"git_commit": {"git_add": 4}}
    assert m.max_steps == 3
    assert undeclared_preconditions(m) == [
        "git_commit: models call git_add first in 4/4 trials, but git_commit's description never mentions git_add"
    ]


def test_single_step_reproduces_the_old_behaviour(monkeypatch):
    m = _matrix_multistep(1, monkeypatch)
    assert m.counts["git_commit"] == {"git_add": 4}
    assert not any(t.passed for t in m.trials_by_tool["git_commit"])
    assert m.precondition_edges == {}


def test_declared_precondition_is_not_flagged(monkeypatch):
    m = _matrix_multistep(3, monkeypatch)
    m.descriptions["git_commit"] = "Records staged changes; call git_add first."
    assert undeclared_preconditions(m) == []


def test_render_shows_preconditions_graph_and_undeclared_findings(monkeypatch):
    m = _matrix_multistep(3, monkeypatch)
    out = render_confusion_matrix(m)
    assert "## Preconditions (observed)" in out
    assert "- git_add → git_commit: 4/4 trials" in out
    assert "```mermaid" in out
    assert 't0["git_add"]' in out and 't1["git_commit"]' in out and "t0 -->|4/4| t1" in out
    assert "## Undeclared Preconditions" in out
    assert "Max steps per task: 3" in out


def test_mutation_trials_report_precondition_counts_before_and_after(monkeypatch):
    m = _matrix_multistep(3, monkeypatch)
    r = run_mutation_trials(m, _catalog(), _StagesFirst(), tool_name="git_commit", new_description="Commits staged changes.", max_steps=3)
    assert r.before_preconditions == 4 and r.after_preconditions == 4
    assert "Reached via an earlier call: 4/4 → 4/4" in render_mutation_results([r])
