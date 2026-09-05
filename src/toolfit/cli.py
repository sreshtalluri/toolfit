"""Typer CLI. `toolfit scan <server>` runs free static lint with no model calls. `toolfit eval
<server>` builds the confusion matrix; `--mutate` re-measures a hand-supplied description,
`--fix` (M4) proposes one per failing tool and re-measures it, `--badge` writes an SVG, `--strict`
turns pass rates into exit codes for CI.
"""

from __future__ import annotations

import asyncio
import json
import os

import anthropic
import openai
import typer

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.fix.fixer import FixVerdict, run_fix_loop
from toolfit.grade.confusion import ConfusionMatrix, build_confusion_matrix
from toolfit.grade.mutator import MutationTrialResult, run_mutation_trials
from toolfit.grade.significance import bonferroni_correct
from toolfit.lint.rules import run_lint
from toolfit.report.badge import render_badge
from toolfit.report.render import (
    render_confusion_matrix,
    render_fix_results,
    render_lint_report,
    render_mutation_results,
)
from toolfit.run.adapters import build_adapter

app = typer.Typer()


@app.command()
def eval(
    server_path: str = typer.Argument(
        ...,
        help="MCP server: a .py script (run via `uv run`), an http(s):// URL, "
        "or a command line like 'npx -y @modelcontextprotocol/server-github'.",
    ),
    seeds: int = typer.Option(5, min=1, help="Tasks generated per tool."),
    model: str = typer.Option("claude-sonnet-5", help="Model under test."),
    mutate: list[str] = typer.Option(
        [],
        "--mutate",
        help="tool_name:new description (repeatable). Runs a paired mutation trial reusing the "
        "base eval's own generated tasks for that tool.",
    ),
    fix: bool = typer.Option(
        False,
        "--fix",
        help="For every tool with a failed trial, propose a rewritten description, re-run that tool's "
        "tasks against it, and report the measured delta (accepted and rejected). Writes toolfit-fixes.json.",
    ),
    badge: bool = typer.Option(
        False,
        "--badge",
        help="Write a static SVG badge (toolfit-badge.svg) summarizing the overall pass rate, or "
        "a before/after delta if exactly one --mutate or accepted --fix was tested.",
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
            fix=fix,
            badge=badge,
            strict=strict,
            strict_threshold=strict_threshold,
        )
    )


@app.command()
def scan(
    server_path: str = typer.Argument(
        ...,
        help="MCP server: a .py script (run via `uv run`), an http(s):// URL, "
        "or a command line like 'npx -y @modelcontextprotocol/server-github'.",
    ),
    strict: bool = typer.Option(False, "--strict", help="Exit with code 1 if any lint finding exists."),
) -> None:
    """Run free, static lint checks against the given MCP server's tool catalog. Makes no model
    calls and needs no API key."""
    asyncio.run(_run_scan(server_path, strict=strict))


def _root_causes(e: BaseException) -> str:
    # The mcp SDK raises anyio ExceptionGroups whose str() is just "unhandled errors in a
    # TaskGroup"; the useful message (missing binary, refused connection) is in the leaves.
    subs = getattr(e, "exceptions", None)
    if subs:
        return "; ".join(_root_causes(s) for s in subs)
    return f"{type(e).__name__}: {e}"


async def _run_scan(server_path: str, *, strict: bool) -> None:
    params = server_params(server_path)
    try:
        catalog = await fetch_catalog(params)
    except Exception as e:
        # Same Failure Modes handling as _run_eval (design doc, docs/designs/toolfit-v0-scope.md:102-104).
        typer.echo(f"Could not connect to server at {server_path!r}: {_root_causes(e)}", err=True)
        raise typer.Exit(code=1)

    findings = run_lint(catalog)
    print(render_lint_report(catalog, findings))

    if strict and findings:
        typer.echo(f"--strict: {len(findings)} finding(s) present", err=True)
        raise typer.Exit(code=1)


def _write_fixes_json(matrix: ConfusionMatrix, verdicts: list[FixVerdict]) -> None:
    # Machine-applicable counterpart of the markdown section: protocol-level description text only
    # (design doc Premise 1) — nothing from the server's source, no keys, no transcripts.
    payload = {
        "model": matrix.model,
        "generator_model": matrix.generator_model,
        "seeds": matrix.seeds,
        "fixes": [
            {
                "tool": v.proposal.tool_name,
                "before_description": v.proposal.original_description,
                "after_description": v.proposal.new_description,
                "before_passed": sum(v.trial.before_passes) if v.trial else None,
                "after_passed": sum(v.trial.after_passes) if v.trial else None,
                "n": len(v.trial.before_passes) if v.trial else None,
                "p_value": v.trial.p_value if v.trial else None,
                "accepted": v.accepted,
                "reason": v.reason,
            }
            for v in verdicts
        ],
    }
    with open("toolfit-fixes.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    typer.echo("Wrote toolfit-fixes.json", err=True)


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
    fix: bool,
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

    if (parsed_mutations or fix) and seeds < 10:
        # Exact McNemar: with n paired trials the smallest attainable p-value is 1/2**n, and
        # Bonferroni divides alpha further. Say so up front rather than let a run end in
        # "not significant" verdicts that could never have been anything else.
        typer.echo(
            f"WARNING: with --seeds {seeds} the smallest attainable p-value is {1 / 2**seeds:.3f}; "
            "mutation/fix verdicts need --seeds 10 or more to reach significance",
            err=True,
        )

    params = server_params(server_path)
    try:
        catalog = await fetch_catalog(params)
    except Exception as e:
        # Failure Modes (design doc, docs/designs/toolfit-v0-scope.md:102-104): an unreachable
        # server or an auth-required catalog fetch must report the failure explicitly rather than
        # surfacing a raw traceback or failing silently.
        typer.echo(f"Could not connect to server at {server_path!r}: {_root_causes(e)}", err=True)
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

    verdicts: list[FixVerdict] = []
    if fix:
        try:
            verdicts = run_fix_loop(matrix, catalog, adapter, generator_client)
        except (anthropic.APIError, openai.APIError) as e:
            typer.echo(f"Model provider error during --fix: {e}", err=True)
            raise typer.Exit(code=1)

    # One Bonferroni correction across everything re-measured in this run — hand-supplied
    # mutations and proposed fixes alike — so neither can cherry-pick a lenient threshold.
    tested = results + [v.trial for v in verdicts if v.trial is not None]
    for trial, sig in zip(tested, bonferroni_correct([t.p_value for t in tested])):
        trial.significant = sig

    if results:
        print()
        print(render_mutation_results(results))
    if fix:
        print()
        print(render_fix_results(verdicts))
        _write_fixes_json(matrix, verdicts)

    if badge:
        # A badge is one flat number — with exactly one delta measured (a --mutate or an accepted
        # --fix), show it; otherwise fall back to the overall pass rate rather than pick one of
        # several to represent.
        deltas = results + [v.trial for v in verdicts if v.accepted and v.trial is not None]
        mutation_result_for_badge = deltas[0] if len(deltas) == 1 else None
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
