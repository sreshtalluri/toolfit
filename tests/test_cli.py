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
