"""Smoke test for the CLI's argument wiring — not a full integration test (that needs a real,
extensively-mocked server connection). build_confusion_matrix and render_confusion_matrix are
already tested directly with fakes in test_confusion.py and test_render.py; this just confirms
the typer app is wired correctly.

Both tests below invoke "eval" as an explicit subcommand name (`["eval", ...]`, not just
positional args) — this only works because cli.py registers an @app.callback(). Verified
empirically: without it, Typer collapses the single-command app so "eval" gets consumed as the
server_path VALUE instead of the subcommand name, and these tests fail/mean something else
(scan/fix/report don't exist yet) if that callback is ever removed — re-verify before removing it.
"""

from typer.testing import CliRunner

from toolfit.cli import app

runner = CliRunner()


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
