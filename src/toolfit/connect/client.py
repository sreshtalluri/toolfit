"""Wraps the official mcp SDK v2 Client to fetch a server's tool catalog.

Dry-run only for the spike: we fetch tools/list to build the catalog handed to models under
test, but never call_tool against the target server — the harness only needs to see which tool
+ arguments a model WOULD choose, not execute it (design doc Constraints: dry-run by default).
"""

from __future__ import annotations

from dataclasses import dataclass

from mcp import Client, StdioServerParameters
from mcp.types import Tool


@dataclass
class ToolCatalog:
    tools: list[Tool]

    def get(self, name: str) -> Tool | None:
        return next((t for t in self.tools if t.name == name), None)

    def names(self) -> list[str]:
        return [t.name for t in self.tools]


def server_params(script_path: str) -> StdioServerParameters:
    """Describe a toy MCP server, launched via `uv run <script_path>`."""
    return StdioServerParameters(command="uv", args=["run", script_path], env={})


async def fetch_catalog(params: StdioServerParameters) -> ToolCatalog:
    """Connect to the server, fetch tools/list, and return the catalog."""
    async with Client(params) as client:
        result = await client.list_tools()
        return ToolCatalog(tools=result.tools)
