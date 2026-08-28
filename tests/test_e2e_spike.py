"""End-to-end: connect to the real toy server (subprocess), fetch its catalog, run the full
gen -> run -> grade -> mutate loop once against a real model. Requires ANTHROPIC_API_KEY — this
is the test that proves the spike's actual purpose (design doc Premise 5)."""

import os

import anthropic
import pytest

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.gen.schema_sampler import sample_arguments
from toolfit.gen.taskgen import generate_task
from toolfit.grade.mutator import run_mutation_test
from toolfit.run.adapters import AnthropicAdapter

pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY")


@pytest.mark.asyncio
async def test_full_loop_against_the_toy_server():
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)
    assert catalog.names() == ["create_task", "update_task", "list_tasks", "count_tasks"]

    target_tool = catalog.get("update_task")
    args = sample_arguments(target_tool.input_schema, seed=1)

    client = anthropic.Anthropic()
    task = generate_task(client, tool_name="update_task", tool_description=target_tool.description, arguments=args)

    adapter = AnthropicAdapter(client)
    result = run_mutation_test(
        adapter,
        task,
        original_catalog=catalog,
        tool_name="update_task",
        new_description="Modify an existing task's title, given its task_id.",
    )
    # Not asserting `improved` as always-true — that's the empirical question this spike exists
    # to answer, not an assumption to bake into the test (design doc: never suppress a result).
    assert result.before is not None
    assert result.after is not None
