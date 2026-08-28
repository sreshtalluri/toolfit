"""CLI entrypoint for the toolfit spike (design doc Next Steps #1).
Run: ANTHROPIC_API_KEY=... uv run python scripts/run_spike.py
"""

from __future__ import annotations

import asyncio
import os
import sys

import anthropic

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.fix.fixer import propose_fix
from toolfit.gen.schema_sampler import count_distinct, sample_arguments
from toolfit.gen.taskgen import check_no_leakage, check_solvability, generate_task
from toolfit.grade.mutator import run_mutation_test
from toolfit.report.render import render_spike_report
from toolfit.run.adapters import AnthropicAdapter

MODEL = "claude-sonnet-5"

# Design doc "Residual circularity risk": when set, the task generator never sees the tool's
# own description text, only the sampled arguments. scripts/circularity_check.py already
# studies this in isolation; this flag just makes the withheld path reachable from the main
# run without editing source. Default False keeps current behavior unchanged.
WITHHOLD_DESCRIPTION = os.environ.get("TOOLFIT_WITHHOLD_DESCRIPTION", "") == "1"

# Which ambiguous pair to test. Default is count_tasks/list_tasks, the neutral-description pair
# (no create/update phrasing confound — see examples/toy_server.py). Set to "update_task" to
# re-run the original, harder create/update pair instead.
TARGET_TOOL = os.environ.get("TOOLFIT_TARGET_TOOL", "count_tasks")


async def main() -> None:
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)

    target = catalog.get(TARGET_TOOL)

    anthropic_client = anthropic.Anthropic()
    adapter = AnthropicAdapter(anthropic_client)

    # A single binary paired observation against a nondeterministic model can't distinguish
    # signal from noise (design doc: "every metric with n, seeds, CI") — run the full chain
    # across several seeds instead of just one.
    seeds = list(range(1, 9))

    # Fix proposal doesn't depend on the sampled task/seed, so it only runs once, outside the
    # loop, and the same proposed (or rejected-and-unchanged) description is measured against
    # every seed's trial below.
    fix = propose_fix(
        anthropic_client,
        tool_name=TARGET_TOOL,
        current_description=target.description,
        other_tool_names=[t for t in catalog.names() if t != TARGET_TOOL],
    )
    new_description = target.description if fix.rejected else fix.new_description

    before_passed_count = 0
    after_passed_count = 0
    all_sampled_args: list[dict[str, str]] = []

    for seed in seeds:
        args = sample_arguments(target.input_schema, seed=seed)
        all_sampled_args.append(args)
        task = generate_task(
            anthropic_client,
            tool_name=TARGET_TOOL,
            tool_description=target.description,
            arguments=args,
            withhold_description=WITHHOLD_DESCRIPTION,
        )
        if not check_no_leakage(task, catalog_tool_names=catalog.names()):
            print(f"WARNING: generated task may leak a tool name: {task.text!r}", file=sys.stderr)

        before_descriptions = {t.name: (t.description or "") for t in catalog.tools}
        solvability_before = check_solvability(anthropic_client, task, catalog_descriptions=before_descriptions)
        if not solvability_before.solvable:
            print(
                f"WARNING: generated task may be ambiguous given the ORIGINAL catalog "
                f"({solvability_before.reasoning}): {task.text!r}",
                file=sys.stderr,
            )

        # Same check against the catalog AFTER the proposed fix, so we can tell "the fix didn't
        # resolve the ambiguity" apart from "the catalog is fine now, the model just got it
        # wrong anyway" — those are different findings and the report shouldn't conflate them.
        after_descriptions = {**before_descriptions, TARGET_TOOL: new_description}
        solvability_after = check_solvability(anthropic_client, task, catalog_descriptions=after_descriptions)
        if not solvability_after.solvable:
            print(
                f"WARNING: generated task STILL ambiguous given the FIXED catalog "
                f"({solvability_after.reasoning}): {task.text!r}",
                file=sys.stderr,
            )

        mutation = run_mutation_test(
            adapter, task, original_catalog=catalog, tool_name=TARGET_TOOL, new_description=new_description
        )
        if mutation.before.passed:
            before_passed_count += 1
        if mutation.after.passed:
            after_passed_count += 1

        call = adapter.call_with_tools(task_text=task.text, tools=catalog.tools)
        print(f"\n# Trial (seed={seed})")
        print(
            render_spike_report(
                task=task,
                call=call,
                mutation=mutation,
                fix=fix,
                after_description=new_description,
                model=MODEL,
                seed=seed,
            )
        )

    distinct = count_distinct(all_sampled_args)
    print(f"\n## Aggregate (N={len(seeds)} trials)")
    print(f"- Distinct trials: {distinct}/{len(seeds)}" + (" (some seeds sampled identical arguments — treat the effective n as this, not N)" if distinct < len(seeds) else ""))
    print(f"- Before passed: {before_passed_count}/{len(seeds)}")
    print(f"- After passed: {after_passed_count}/{len(seeds)}")


if __name__ == "__main__":
    asyncio.run(main())
