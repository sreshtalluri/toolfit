"""Wraps the official mcp SDK v2 Client to fetch a server's tool catalog.

Dry-run only for the spike: we fetch tools/list to build the catalog handed to models under
test, but never call_tool against the target server — the harness only needs to see which tool
+ arguments a model WOULD choose, not execute it (design doc Constraints: dry-run by default).
"""

from __future__ import annotations

import os
import shlex
from dataclasses import dataclass

from mcp import Client, StdioServerParameters
from mcp.types import Tool

_TOOLFIT_KEYS = frozenset({"ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY"})


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
    The subprocess gets the caller's environment (the mcp SDK's default is a six-variable
    whitelist, which would strip GITHUB_TOKEN and friends) minus toolfit's own provider keys, which
    a third-party server binary has no business seeing.
    """
    if not server.strip():
        raise ValueError("server must not be empty")
    if server.startswith(("http://", "https://")):
        return server
    env = {k: v for k, v in os.environ.items() if k not in _TOOLFIT_KEYS}
    if server.endswith(".py") and (os.path.isfile(server) or not any(c.isspace() for c in server)):
        return StdioServerParameters(command="uv", args=["run", server], env=env)
    command, *args = shlex.split(server)
    return StdioServerParameters(command=command, args=args, env=env)


async def fetch_catalog(params: StdioServerParameters | str) -> ToolCatalog:
    """Connect to the server, fetch tools/list, and return the catalog."""
    async with Client(params) as client:
        result = await client.list_tools()
        return ToolCatalog(tools=result.tools)
