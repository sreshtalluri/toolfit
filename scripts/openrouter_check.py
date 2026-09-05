"""Validates an OpenRouter model's tool-call/JSON-strictness behavior before M2 commits to it
as a third adapter (design doc Next Steps #1, TODO 4).
Run: ANTHROPIC_API_KEY=... OPENROUTER_API_KEY=... uv run python scripts/openrouter_check.py
"""

from __future__ import annotations

import asyncio
import os

import anthropic
import openai

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.gen.schema_sampler import sample_arguments
from toolfit.gen.taskgen import generate_task
from toolfit.run.adapters import OpenRouterAdapter

# Check https://openrouter.ai/models for current tool-calling-capable model IDs — this default
# may drift over time; override via the OPENROUTER_MODEL env var rather than editing this file.
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-5.5")


async def main() -> None:
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)
    target = catalog.get("create_task")
    args = sample_arguments(target.input_schema, seed=1)

    anthropic_client = anthropic.Anthropic()
    task = generate_task(anthropic_client, tool_name="create_task", tool_description=target.description, arguments=args)

    router_client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    adapter = OpenRouterAdapter(router_client, model=OPENROUTER_MODEL)
    call = adapter.call_with_tools(task_text=task.text, tools=catalog.tools)

    print(f"Task: {task.text!r}")
    print(f"Ground truth: {task.tool_name}({task.arguments})")
    print(f"OpenRouter ({OPENROUTER_MODEL}) called: {call.tool_name}({call.arguments})")
    print()
    print("Record in docs/designs/toolfit-v0-scope.md's Next Steps once run:")
    print("- Did it make a tool call at all, or only text?")
    print("- Did tool_calls[0].function.arguments parse as valid JSON without repair?")
    print("- Did the model name resolve without a 400/404 from OpenRouter?")


if __name__ == "__main__":
    asyncio.run(main())
