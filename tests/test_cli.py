"""Smoke test for the CLI's argument wiring — not a full integration test (that needs a real,
extensively-mocked server connection). build_confusion_matrix and render_confusion_matrix are
already tested directly with fakes in test_confusion.py and test_render.py; this just confirms
the typer app is wired correctly.

Tests below invoke "eval" and "scan" as explicit subcommand names (`["eval", ...]`, not just
positional args). Historically (single-command app, `eval` only) this required cli.py to
register an @app.callback() — Typer otherwise collapses a single @app.command() into "no
subcommand name needed" mode and consumes "eval" as the server_path VALUE instead of the
subcommand name. That callback was removed once `scan` became a second registered command:
re-verified empirically (all tests in this file still pass with the callback commented out) that
Typer stops collapsing on its own once there are two-or-more commands — see cli.py's module
docstring history / task-3-report.md for the experiment.
"""

from types import SimpleNamespace

from mcp.types import Tool
from typer.testing import CliRunner

import toolfit.cli as cli
from toolfit.cli import app
from toolfit.connect.client import ToolCatalog
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.confusion import ConfusionMatrix, TrialRecord
from toolfit.grade.mutator import MutationTrialResult

runner = CliRunner()

_SIMPLE_SCHEMA = {"type": "object", "properties": {"title": {"type": "string"}}}


def test_eval_help_shows_server_path_argument():
    result = runner.invoke(app, ["eval", "--help"])
    assert result.exit_code == 0
    assert "SERVER_PATH" in result.output or "server_path" in result.output


def test_eval_requires_server_path_argument():
    result = runner.invoke(app, ["eval"])
    assert result.exit_code != 0


def test_eval_reports_a_clear_error_for_an_unreachable_server():
    result = runner.invoke(app, ["eval", "/nonexistent/path/to/server.py"])
    assert result.exit_code != 0
    # Assert the handled message is actually emitted, and that the command exited via typer.Exit
    # rather than propagating the raw connection exception. Checking only `"Traceback" not in
    # result.output` would pass even with no error handling at all, because CliRunner captures an
    # unhandled exception into result.exception and leaves result.output empty.
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert "Could not connect to server" in result.output
    assert "/nonexistent/path/to/server.py" in result.output


def test_eval_help_shows_mutate_option():
    result = runner.invoke(app, ["eval", "--help"])
    assert result.exit_code == 0
    assert "--mutate" in result.output


def test_eval_rejects_a_malformed_mutate_spec_before_connecting_to_any_server():
    # No colon in the spec — this must fail on parsing alone, before ever attempting to reach
    # the (nonexistent) server, so the error message is about the flag, not a connection failure.
    result = runner.invoke(app, ["eval", "/nonexistent/path/to/server.py", "--mutate", "no-colon-here"])
    assert result.exit_code != 0
    assert "must be of the form 'tool_name:new description'" in result.output
    assert "Could not connect to server" not in result.output


def test_eval_reports_a_clear_error_when_anthropic_api_key_is_missing_for_generation(monkeypatch):
    # Task generation always uses Anthropic (GENERATOR_MODEL in taskgen.py), regardless of which
    # --model the user picked for the model under test. anthropic.Anthropic() does not raise at
    # construction time on a missing key, so without an explicit guard this failure would surface
    # deep inside build_confusion_matrix's first generator call as a raw, unhandled traceback —
    # not the clean CLI error (exit code 1, message on stderr) the project requires.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    async def fake_fetch_catalog(params):
        return ToolCatalog(tools=[Tool(name="tool_a", description="Does A.", inputSchema=_SIMPLE_SCHEMA)])

    monkeypatch.setattr(cli, "fetch_catalog", fake_fetch_catalog)
    monkeypatch.setattr(cli, "build_adapter", lambda model: SimpleNamespace(model=model))

    result = runner.invoke(app, ["eval", "somepath", "--model", "gpt-5.5"])

    assert result.exit_code == 1
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert "Traceback" not in result.output
    assert "ANTHROPIC_API_KEY" in result.output
    assert "generation" in result.output.lower()


def test_eval_mutate_rejects_an_unknown_tool_name(monkeypatch):
    async def fake_fetch_catalog(params):
        return ToolCatalog(tools=[Tool(name="tool_a", description="Does A.", inputSchema=_SIMPLE_SCHEMA)])

    monkeypatch.setattr(cli, "fetch_catalog", fake_fetch_catalog)

    result = runner.invoke(app, ["eval", "somepath", "--mutate", "no_such_tool:new description"])

    assert result.exit_code == 1
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert "unknown tool" in result.output.lower()
    assert "no_such_tool" in result.output


def test_eval_mutate_skips_a_tool_excluded_by_a_schema_warning(monkeypatch):
    # A tool named in --mutate can be validly in the catalog but still absent from
    # matrix.trials_by_tool if the base eval excluded it for a schema warning. This must be a
    # skip-with-explanation, not a hard failure — the CLI still exits 0.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")

    async def fake_fetch_catalog(params):
        return ToolCatalog(
            tools=[
                Tool(name="tool_a", description="Does A.", inputSchema=_SIMPLE_SCHEMA),
                Tool(name="tool_b", description="Does B.", inputSchema=_SIMPLE_SCHEMA),
            ]
        )

    matrix = ConfusionMatrix(
        counts={"tool_a": {"tool_a": 2}},
        distinct_trials={"tool_a": 2},
        trials_per_tool={"tool_a": 2},
        trials_by_tool={
            "tool_a": [TrialRecord(task=GeneratedTask(text="t", tool_name="tool_a", arguments={}), passed=True)]
        },
        schema_warnings=["tool_b: excluded from scoring — some schema error"],
        model="gpt-5.5",
        generator_model="claude-sonnet-5",
        seeds=2,
    )

    monkeypatch.setattr(cli, "fetch_catalog", fake_fetch_catalog)
    monkeypatch.setattr(cli, "build_adapter", lambda model: SimpleNamespace(model=model))
    monkeypatch.setattr(cli, "build_confusion_matrix", lambda catalog, adapter, generator_client, seeds: matrix)

    result = runner.invoke(app, ["eval", "somepath", "--mutate", "tool_b:new description"])

    assert result.exit_code == 0
    assert "Skipping --mutate" in result.output
    assert "tool_b" in result.output


def test_eval_mutate_applies_bonferroni_correction_across_multiple_mutations(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")

    async def fake_fetch_catalog(params):
        return ToolCatalog(
            tools=[
                Tool(name="tool_a", description="Does A.", inputSchema=_SIMPLE_SCHEMA),
                Tool(name="tool_b", description="Does B.", inputSchema=_SIMPLE_SCHEMA),
            ]
        )

    def make_trial(tool_name):
        return TrialRecord(task=GeneratedTask(text=f"t-{tool_name}", tool_name=tool_name, arguments={}), passed=True)

    matrix = ConfusionMatrix(
        counts={"tool_a": {"tool_a": 2}, "tool_b": {"tool_b": 2}},
        distinct_trials={"tool_a": 2, "tool_b": 2},
        trials_per_tool={"tool_a": 2, "tool_b": 2},
        trials_by_tool={"tool_a": [make_trial("tool_a")], "tool_b": [make_trial("tool_b")]},
        model="gpt-5.5",
        generator_model="claude-sonnet-5",
        seeds=2,
    )

    # Bonferroni-corrected alpha for 2 tests is 0.05 / 2 = 0.025. p=0.01 clears it (significant);
    # p=0.04 does not (not significant) — even though both would read "significant" against a
    # naive, uncorrected alpha=0.05. This is the exact distinction the correction loop must make.
    preset_results = {
        "tool_a": MutationTrialResult(
            tool_name="tool_a", new_description="better a", before_passes=[False], after_passes=[True], p_value=0.01
        ),
        "tool_b": MutationTrialResult(
            tool_name="tool_b", new_description="better b", before_passes=[False], after_passes=[True], p_value=0.04
        ),
    }

    def fake_run_mutation_trials(matrix, catalog, adapter, *, tool_name, new_description):
        return preset_results[tool_name]

    monkeypatch.setattr(cli, "fetch_catalog", fake_fetch_catalog)
    monkeypatch.setattr(cli, "build_adapter", lambda model: SimpleNamespace(model=model))
    monkeypatch.setattr(cli, "build_confusion_matrix", lambda catalog, adapter, generator_client, seeds: matrix)
    monkeypatch.setattr(cli, "run_mutation_trials", fake_run_mutation_trials)

    result = runner.invoke(
        app, ["eval", "somepath", "--mutate", "tool_a:better a", "--mutate", "tool_b:better b"]
    )

    assert result.exit_code == 0
    tool_a_block = result.output.split("### tool_a")[1].split("### tool_b")[0]
    tool_b_block = result.output.split("### tool_b")[1]
    assert "SIGNIFICANT" in tool_a_block
    assert "not significant" in tool_b_block


def test_scan_help_shows_server_path_argument():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "SERVER_PATH" in result.output or "server_path" in result.output


def test_scan_requires_server_path_argument():
    result = runner.invoke(app, ["scan"])
    assert result.exit_code != 0


def test_scan_reports_a_clear_error_for_an_unreachable_server():
    result = runner.invoke(app, ["scan", "/nonexistent/path/to/server.py"])
    assert result.exit_code != 0
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert "Could not connect to server" in result.output
    assert "/nonexistent/path/to/server.py" in result.output


def test_eval_still_requires_explicit_subcommand_name_alongside_scan():
    # Regression guard for the Typer single-command-collapse quirk this file already hit once
    # (see this file's module docstring): now that TWO commands are registered (eval, scan),
    # `["eval", ...]` must still work as an explicit subcommand name.
    result = runner.invoke(app, ["eval", "--help"])
    assert result.exit_code == 0
    assert "SERVER_PATH" in result.output or "server_path" in result.output
