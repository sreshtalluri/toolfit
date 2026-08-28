"""Typer CLI: `toolfit eval <server_path>` (design doc Distribution Plan, M1 Design). Only the
`eval` subcommand exists in M1 — `scan`/`fix`/`report` per the source doc's fuller architecture
come later (M0's static lint, M4's fix loop). No mutation/fix flag here — that's explicitly M2/M4
scope, not M1 (design doc M1 Design, Global Constraints).
"""

from __future__ import annotations

import asyncio

import anthropic
import typer

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.grade.confusion import build_confusion_matrix
from toolfit.report.render import render_confusion_matrix
from toolfit.run.adapters import AnthropicAdapter

app = typer.Typer()


@app.callback()
def _callback() -> None:
    """Empty on purpose: Typer collapses a single @app.command() into "no subcommand name
    needed" mode unless an @app.callback() is also registered (verified empirically — without
    this, `toolfit eval <path>` wouldn't work as documented in the design doc's Distribution
    Plan; `toolfit <path>` would work instead, which isn't what's specified). Remove once a
    second command (scan/fix/report) exists — that's the point Typer stops collapsing on its
    own."""


@app.command()
def eval(
    server_path: str = typer.Argument(..., help="Path to a local stdio MCP server script."),
    seeds: int = typer.Option(5, help="Tasks generated per tool."),
    model: str = typer.Option("claude-sonnet-5", help="Model under test."),
) -> None:
    """Build and print a confusion matrix for the given MCP server."""
    asyncio.run(_run_eval(server_path, seeds=seeds, model=model))


async def _run_eval(server_path: str, *, seeds: int, model: str) -> None:
    params = server_params(server_path)
    try:
        catalog = await fetch_catalog(params)
    except Exception as e:
        # Failure Modes (design doc, docs/designs/toolfit-v0-scope.md:102-104): an unreachable
        # server or an auth-required catalog fetch must report the failure explicitly rather than
        # surfacing a raw traceback or failing silently.
        typer.echo(f"Could not connect to server at {server_path!r}: {e}", err=True)
        raise typer.Exit(code=1)

    client = anthropic.Anthropic()
    adapter = AnthropicAdapter(client, model=model)

    matrix = build_confusion_matrix(catalog, adapter, client, seeds=seeds)
    print(render_confusion_matrix(matrix))


if __name__ == "__main__":
    app()
