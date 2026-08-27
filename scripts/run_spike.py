"""CLI entrypoint for the toolfit spike (design doc Next Steps #1).
Run: ANTHROPIC_API_KEY=... uv run python scripts/run_spike.py
"""

from __future__ import annotations

import asyncio

import anthropic

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.fix.fixer import propose_fix
from toolfit.gen.schema_sampler import sample_arguments
from toolfit.gen.taskgen import generate_task
from toolfit.grade.mutator import run_mutation_test
from toolfit.report.render import render_spike_report
from toolfit.run.adapters import AnthropicAdapter


async def main() -> None:
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)

    target = catalog.get("update_task")
    args = sample_arguments(target.input_schema, seed=1)

    anthropic_client = anthropic.Anthropic()
    task = generate_task(anthropic_client, tool_name="update_task", tool_description=target.description, arguments=args)

    adapter = AnthropicAdapter(anthropic_client)
    fix = propose_fix(
        anthropic_client,
        tool_name="update_task",
        current_description=target.description,
        other_tool_names=[t for t in catalog.names() if t != "update_task"],
    )

    new_description = target.description if fix.rejected else fix.new_description
    mutation = run_mutation_test(adapter, task, original_catalog=catalog, tool_name="update_task", new_description=new_description)

    call = adapter.call_with_tools(task_text=task.text, tools=catalog.tools)
    print(render_spike_report(task=task, call=call, mutation=mutation, fix=fix))


if __name__ == "__main__":
    asyncio.run(main())
