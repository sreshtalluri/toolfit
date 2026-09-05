"""Typer CLI: `toolfit eval <server_path>` (design doc Distribution Plan, M1 Design), extended in
M2 with `--mutate` for paired mutation testing (design doc M2 Design §4). `toolfit scan
<server_path>` (M0's static lint) now also exists as a real command, running free lint checks
with no model calls; `fix`/`report` per the source doc's fuller architecture still come later
(M4's fix loop). `--mutate` takes a hand-supplied description and reports a rigorous before/after
verdict on it; it never generates a candidate description itself — that stays M4's fix loop
(design doc M2 Design, "Explicitly out of scope").
"""

from __future__ import annotations

import asyncio
import os

import anthropic
import openai
import typer

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.grade.confusion import build_confusion_matrix
from toolfit.grade.mutator import MutationTrialResult, run_mutation_trials
from toolfit.grade.significance import bonferroni_correct
from toolfit.lint.rules import run_lint
from toolfit.report.badge import render_badge
from toolfit.report.render import render_confusion_matrix, render_lint_report, render_mutation_results
from toolfit.run.adapters import build_adapter

app = typer.Typer()


@app.command()
def eval(
    server_path: str = typer.Argument(..., help="Path to a local stdio MCP server script."),
    seeds: int = typer.Option(5, min=1, help="Tasks generated per tool."),
    model: str = typer.Option("claude-sonnet-5", help="Model under test."),
    mutate: list[str] = typer.Option(
        [],
        "--mutate",
        help="tool_name:new description (repeatable). Runs a paired mutation trial reusing the "
        "base eval's own generated tasks for that tool.",
    ),
    badge: bool = typer.Option(
        False,
        "--badge",
        help="Write a static SVG badge (toolfit-badge.svg) summarizing the overall pass rate, or "
        "a before/after delta if exactly one --mutate was tested.",
    ),
    strict: bool = typer.Option(
        False, "--strict", help="Exit with code 1 if any tool's pass rate falls below --strict-threshold."
    ),
    strict_threshold: float = typer.Option(
        0.9,
        "--strict-threshold",
        min=0.0,
        max=1.0,
        help="Minimum acceptable per-tool pass rate when --strict is set.",
    ),
) -> None:
    """Build and print a confusion matrix for the given MCP server, optionally testing description
    mutations against it."""
    asyncio.run(
        _run_eval(
            server_path,
            seeds=seeds,
            model=model,
            mutate=mutate,
            badge=badge,
            strict=strict,
            strict_threshold=strict_threshold,
        )
    )


@app.command()
def scan(
    server_path: str = typer.Argument(..., help="Path to a local stdio MCP server script."),
    strict: bool = typer.Option(False, "--strict", help="Exit with code 1 if any lint finding exists."),
) -> None:
    """Run free, static lint checks against the given MCP server's tool catalog. Makes no model
    calls and needs no API key."""
    asyncio.run(_run_scan(server_path, strict=strict))


async def _run_scan(server_path: str, *, strict: bool) -> None:
    params = server_params(server_path)
    try:
        catalog = await fetch_catalog(params)
    except Exception as e:
        # Same Failure Modes handling as _run_eval (design doc, docs/designs/toolfit-v0-scope.md:102-104).
        typer.echo(f"Could not connect to server at {server_path!r}: {e}", err=True)
        raise typer.Exit(code=1)

    findings = run_lint(catalog)
    print(render_lint_report(catalog, findings))

    if strict and findings:
        typer.echo(f"--strict: {len(findings)} finding(s) present", err=True)
        raise typer.Exit(code=1)


def _parse_mutation(spec: str) -> tuple[str, str]:
    if ":" not in spec:
        raise ValueError(f"--mutate value {spec!r} must be of the form 'tool_name:new description'")
    tool_name, _, new_description = spec.partition(":")
    if not new_description.strip():
        raise ValueError(f"--mutate value {spec!r} has an empty new description")
    return tool_name.strip(), new_description.strip()


async def _run_eval(
    server_path: str,
    *,
    seeds: int,
    model: str,
    mutate: list[str],
    badge: bool,
    strict: bool,
    strict_threshold: float,
) -> None:
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
    try:
        matrix = build_confusion_matrix(catalog, adapter, generator_client, seeds=seeds)
    except (anthropic.APIError, openai.APIError) as e:
        # Non-transient provider errors (400 invalid tool name, 401, exhausted retries) surface as a
        # named CLI error, not a traceback. Nothing is printed for the partial run on purpose: a
        # partial matrix looks complete.
        typer.echo(f"Model provider error during eval: {e}", err=True)
        raise typer.Exit(code=1)
    print(render_confusion_matrix(matrix))

    results: list[MutationTrialResult] = []
    if parsed_mutations:
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
            try:
                results.append(
                    run_mutation_trials(matrix, catalog, adapter, tool_name=tool_name, new_description=new_description)
                )
            except (anthropic.APIError, openai.APIError) as e:
                typer.echo(f"Model provider error during --mutate {tool_name!r}: {e}", err=True)
                raise typer.Exit(code=1)

        if results:
            significances = bonferroni_correct([r.p_value for r in results])
            for r, sig in zip(results, significances):
                r.significant = sig
            print()
            print(render_mutation_results(results))

    if badge:
        # A badge is one flat number — with exactly one mutation tested, show its before/after
        # delta; with zero or several, fall back to the overall pass rate rather than picking an
        # arbitrary one of several mutations to represent.
        mutation_result_for_badge = results[0] if len(results) == 1 else None
        svg = render_badge(matrix, mutation_result_for_badge)
        with open("toolfit-badge.svg", "w", encoding="utf-8") as f:
            f.write(svg)
        typer.echo("Wrote badge to toolfit-badge.svg", err=True)

    if strict:
        below_threshold = []
        for tool_name, trials in matrix.trials_by_tool.items():
            passed = sum(1 for t in trials if t.passed)
            rate = passed / len(trials)
            if rate < strict_threshold:
                below_threshold.append(f"{tool_name} ({rate:.0%})")

        # A tool excluded entirely by a schema warning never enters matrix.trials_by_tool, so it
        # can never be "below threshold" above — it's simply absent from the check. Left silent,
        # a catalog where every tool failed schema sampling would make --strict exit 0: a green
        # CI gate on a server that was never actually evaluated. This warning must be visible
        # regardless of whether below_threshold also triggers an exit below (docs/designs/
        # toolfit-v0-scope.md, "--strict semantics when a tool couldn't be evaluated at all").
        if matrix.schema_warnings:
            typer.echo(
                f"--strict: {len(matrix.schema_warnings)} tool(s) could not be evaluated (excluded by schema "
                "warning — see Schema Warnings above) and are NOT included in the pass/fail verdict",
                err=True,
            )

        if below_threshold:
            typer.echo(
                f"--strict: {len(below_threshold)} tool(s) below {strict_threshold:.0%} pass rate: "
                f"{', '.join(sorted(below_threshold))}",
                err=True,
            )
            raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
