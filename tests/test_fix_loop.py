"""Offline tests for the M4 fix loop — fake fixer client and fake adapter, no API key."""

from types import SimpleNamespace

from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.fix.fixer import FixVerdict, ProposedFix, run_fix_loop
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.confusion import ConfusionMatrix, TrialRecord
from toolfit.grade.mutator import MutationTrialResult
from toolfit.report.render import render_fix_results

_SCHEMA = {"type": "object", "properties": {"title": {"type": "string"}}}


def _catalog() -> ToolCatalog:
    return ToolCatalog(
        tools=[
            Tool(name="create_task", description="Add a new task.", inputSchema=_SCHEMA),
            Tool(name="update_task", description="Add a new task.", inputSchema=_SCHEMA),
            Tool(name="list_tasks", description="List tasks by status.", inputSchema=_SCHEMA),
        ]
    )


def _matrix() -> ConfusionMatrix:
    def trials(tool, passes):
        return [TrialRecord(task=GeneratedTask(text=f"{tool} {i}", tool_name=tool, arguments={}), passed=p) for i, p in enumerate(passes)]

    return ConfusionMatrix(
        counts={
            "create_task": {"create_task": 3},
            "update_task": {"create_task": 2, "update_task": 1},
            "list_tasks": {"list_tasks": 3},
        },
        trials_by_tool={
            "create_task": trials("create_task", [True, True, True]),
            "update_task": trials("update_task", [False, False, True]),
            "list_tasks": trials("list_tasks", [True, True, True]),
        },
        model="fake",
        generator_model="fake",
        seeds=3,
    )


def _fixer_client(reply: str):
    response = SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=reply)])
    return SimpleNamespace(messages=SimpleNamespace(create=lambda **kwargs: response))


class _AlwaysRightAdapter:
    model = "fake"

    def __init__(self):
        self.calls = 0

    def call_with_tools(self, *, task_text, tools):
        self.calls += 1
        return SimpleNamespace(tool_name=task_text.split()[0], arguments={})


def test_run_fix_loop_only_targets_tools_with_a_failed_trial_and_reverifies_them():
    adapter = _AlwaysRightAdapter()
    verdicts = run_fix_loop(_matrix(), _catalog(), adapter, _fixer_client("Modify an existing task's title given its id."))

    assert [v.proposal.tool_name for v in verdicts] == ["update_task"]
    assert verdicts[0].trial is not None
    assert verdicts[0].trial.before_passes == [False, False, True]
    assert verdicts[0].trial.after_passes == [True, True, True]
    assert adapter.calls == 3  # one re-run per base trial, nothing for the all-pass tools


def test_run_fix_loop_lists_confused_with_tools_first_in_the_rewrite_prompt():
    seen = {}

    def create(**kwargs):
        seen["prompt"] = kwargs["messages"][0]["content"]
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="A real replacement.")])

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    run_fix_loop(_matrix(), _catalog(), _AlwaysRightAdapter(), client)

    assert "create_task, list_tasks" in seen["prompt"]


def test_run_fix_loop_records_a_rejected_proposal_without_spending_any_adapter_calls():
    adapter = _AlwaysRightAdapter()
    verdicts = run_fix_loop(_matrix(), _catalog(), adapter, _fixer_client("Add a new task."))  # identical

    assert verdicts[0].trial is None
    assert not verdicts[0].accepted
    assert "identical" in verdicts[0].reason
    assert adapter.calls == 0


def _verdict(before, after, *, significant, rejected=False):
    proposal = ProposedFix("update_task", "Add a new task.", "Modify an existing task.", rejected, "empty rewrite" if rejected else None)
    trial = None if rejected else MutationTrialResult("update_task", "Modify an existing task.", before, after, 0.05, significant)
    return FixVerdict(proposal, trial)


def test_verdict_accepted_only_when_significant_and_better():
    assert _verdict([False, False], [True, True], significant=True).accepted
    assert not _verdict([False, False], [True, True], significant=False).accepted
    assert "not significant" in _verdict([False, False], [True, True], significant=False).reason
    assert "worse" in _verdict([True, True], [False, True], significant=False).reason
    assert "no change" in _verdict([True, False], [True, False], significant=False).reason
    assert "before re-measurement" in _verdict([], [], significant=False, rejected=True).reason


def test_render_fix_results_shows_rejected_and_accepted_alike():
    out = render_fix_results([_verdict([False, False], [True, True], significant=True), _verdict([], [], significant=False, rejected=True)])
    assert "## Proposed Fixes" in out
    assert "update_task — ACCEPTED" in out
    assert "update_task — REJECTED" in out
    assert "0/2 → 2/2" in out
    assert "empty rewrite" in out


def test_render_fix_results_with_nothing_to_fix():
    assert "nothing to fix" in render_fix_results([])
