"""Wraps the official mcp SDK v2 Client to fetch a server's tool catalog.

Dry-run only for the spike: we fetch tools/list to build the catalog handed to models under
test, but never call_tool against the target server — the harness only needs to see which tool
+ arguments a model WOULD choose, not execute it (design doc Constraints: dry-run by default).
"""

from __future__ import annotations

import shlex
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


def server_params(server: str) -> StdioServerParameters | str:
    """Turn the CLI's server argument into something `mcp.Client` accepts.

    - `http(s)://...`      -> Streamable HTTP URL, passed through as-is.
    - `path/to/server.py`  -> launched via `uv run <path>` (the toy-server convention).
    - anything else        -> a shell-style command line, e.g. `npx -y @modelcontextprotocol/server-github`.
    The subprocess inherits the caller's environment, so servers that read API tokens from env work.
    """
    if server.startswith(("http://", "https://")):
        return server
    command, *args = shlex.split(server)
    if not args and command.endswith(".py"):
        return StdioServerParameters(command="uv", args=["run", command])
    return StdioServerParameters(command=command, args=args)


async def fetch_catalog(params: StdioServerParameters | str) -> ToolCatalog:
    """Connect to the server, fetch tools/list, and return the catalog."""
    async with Client(params) as client:
        result = await client.list_tools()
        return ToolCatalog(tools=result.tools)
