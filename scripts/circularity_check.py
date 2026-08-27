"""The spike's circularity experiment (design doc "Residual circularity risk" under The Core
Technique). Generates the SAME sampled tuple's task twice — once with the tool's description
visible to the generator, once withheld — and prints both so a human can judge whether
withholding produces a meaningfully different (less description-echoing) task.
Run: ANTHROPIC_API_KEY=... uv run python scripts/circularity_check.py
"""

from __future__ import annotations

import asyncio

import anthropic

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.gen.schema_sampler import sample_arguments
from toolfit.gen.taskgen import generate_task


async def main() -> None:
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)
    target = catalog.get("update_task")
    args = sample_arguments(target.input_schema, seed=1)

    client = anthropic.Anthropic()
    with_desc = generate_task(
        client, tool_name="update_task", tool_description=target.description, arguments=args, withhold_description=False
    )
    without_desc = generate_task(
        client, tool_name="update_task", tool_description=target.description, arguments=args, withhold_description=True
    )

    print(f"Tool description (for reference only): {target.description!r}")
    print(f"Sampled arguments: {args}")
    print()
    print(f"WITH description visible:    {with_desc.text!r}")
    print(f"WITHOUT description visible: {without_desc.text!r}")
    print()
    print("Judge manually: does the WITH version echo words from the description that the")
    print("WITHOUT version doesn't? If yes and WITHOUT is still natural, prefer withholding")
    print("by default (see docs/designs/toolfit-v0-scope.md, The Core Technique). If WITHOUT")
    print("reads awkward/unnatural, keep the description visible and document the residual")
    print("risk explicitly instead of claiming it away.")


if __name__ == "__main__":
    asyncio.run(main())
