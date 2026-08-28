"""Typer CLI: `toolfit eval <server_path>` (design doc Distribution Plan, M1 Design), extended in
M2 with `--mutate` for paired mutation testing (design doc M2 Design §4). Only the `eval`
subcommand exists — `scan`/`fix`/`report` per the source doc's fuller architecture come later
(M0's static lint, M4's fix loop). `--mutate` takes a hand-supplied description and reports a
rigorous before/after verdict on it; it never generates a candidate description itself — that
stays M4's fix loop (design doc M2 Design, "Explicitly out of scope").
"""

from __future__ import annotations

import asyncio
import os

import anthropic
import typer

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.grade.confusion import build_confusion_matrix
from toolfit.grade.mutator import run_mutation_trials
from toolfit.grade.significance import bonferroni_correct
from toolfit.report.render import render_confusion_matrix, render_mutation_results
from toolfit.run.adapters import build_adapter

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
    mutate: list[str] = typer.Option(
        [],
        "--mutate",
        help="tool_name:new description (repeatable). Runs a paired mutation trial reusing the "
        "base eval's own generated tasks for that tool.",
    ),
) -> None:
    """Build and print a confusion matrix for the given MCP server, optionally testing description
    mutations against it."""
    asyncio.run(_run_eval(server_path, seeds=seeds, model=model, mutate=mutate))


def _parse_mutation(spec: str) -> tuple[str, str]:
    if ":" not in spec:
        raise ValueError(f"--mutate value {spec!r} must be of the form 'tool_name:new description'")
    tool_name, _, new_description = spec.partition(":")
    return tool_name.strip(), new_description.strip()


async def _run_eval(server_path: str, *, seeds: int, model: str, mutate: list[str]) -> None:
    # Parse --mutate specs before any I/O — a malformed flag should fail fast, not after
    # spending time connecting to a server that was never going to matter.
    parsed_mutations: list[tuple[str, str]] = []
    for spec in mutate:
        try:
            parsed_mutations.append(_parse_mutation(spec))
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(code=1)

    params = server_params(server_path)
    try:
        catalog = await fetch_catalog(params)
    except Exception as e:
        # Failure Modes (design doc, docs/designs/toolfit-v0-scope.md:102-104): an unreachable
        # server or an auth-required catalog fetch must report the failure explicitly rather than
        # surfacing a raw traceback or failing silently.
        typer.echo(f"Could not connect to server at {server_path!r}: {e}", err=True)
        raise typer.Exit(code=1)

    for tool_name, _ in parsed_mutations:
        if tool_name not in catalog.names():
            typer.echo(
                f"--mutate references unknown tool {tool_name!r} (catalog has: {', '.join(catalog.names())})",
                err=True,
            )
            raise typer.Exit(code=1)

    try:
        adapter = build_adapter(model)
    except RuntimeError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)

    # Task generation always uses Anthropic (GENERATOR_MODEL, gen/taskgen.py), regardless of which
    # --model the user chose for the model under test — before M2's multi-provider support, --model
    # was always Anthropic too, so this key requirement was invisible. anthropic.Anthropic() does
    # not raise on a missing key at construction time; without this explicit check, the failure
    # would surface as a raw, unhandled TypeError traceback on the first real generator call inside
    # build_confusion_matrix, not the clean CLI error (exit code 1, message on stderr) required for
    # missing API keys.
    if not os.environ.get("ANTHROPIC_API_KEY"):
        typer.echo(
            "ANTHROPIC_API_KEY is not set — required for task generation regardless of --model",
            err=True,
        )
        raise typer.Exit(code=1)
    generator_client = anthropic.Anthropic()
    matrix = build_confusion_matrix(catalog, adapter, generator_client, seeds=seeds)
    print(render_confusion_matrix(matrix))

    if not parsed_mutations:
        return

    results = []
    for tool_name, new_description in parsed_mutations:
        if tool_name not in matrix.trials_by_tool:
            # Excluded from the base eval for a schema warning — already reported above, in the
            # confusion matrix's own Schema Warnings section. Never suppress this: say explicitly
            # why the mutation this tool asked for didn't run.
            typer.echo(
                f"Skipping --mutate for {tool_name!r}: excluded from the base eval (see Schema Warnings above)",
                err=True,
            )
            continue
        results.append(
            run_mutation_trials(matrix, catalog, adapter, tool_name=tool_name, new_description=new_description)
        )

    if not results:
        return

    significances = bonferroni_correct([r.p_value for r in results])
    for r, sig in zip(results, significances):
        r.significant = sig

    print()
    print(render_mutation_results(results))


if __name__ == "__main__":
    app()
