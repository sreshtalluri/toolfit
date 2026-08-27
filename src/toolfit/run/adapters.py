"""Minimal model-under-test adapters. Spike scope: Anthropic (primary). OpenRouter is added in
Task 9 as a compatibility check only, per design doc Next Steps #1. No retry/backoff or
concurrency here — those are explicit M2 requirements (Engineering Requirements #1, #2 in the
design doc), out of scope for a single-server, single-request spike.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import anthropic
from mcp.types import Tool


@dataclass
class ToolCall:
    tool_name: str | None  # None means the model made no tool call at all
    arguments: dict


class ModelAdapter(Protocol):
    def call_with_tools(self, *, task_text: str, tools: list[Tool]) -> ToolCall: ...


def _tool_to_anthropic_schema(tool: Tool) -> dict:
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": tool.input_schema,
    }


class AnthropicAdapter:
    MODEL = "claude-sonnet-5"

    def __init__(self, client: anthropic.Anthropic):
        self._client = client

    def call_with_tools(self, *, task_text: str, tools: list[Tool]) -> ToolCall:
        response = self._client.messages.create(
            model=self.MODEL,
            max_tokens=500,
            tools=[_tool_to_anthropic_schema(t) for t in tools],
            messages=[{"role": "user", "content": task_text}],
        )
        for block in response.content:
            if block.type == "tool_use":
                return ToolCall(tool_name=block.name, arguments=block.input)
        return ToolCall(tool_name=None, arguments={})
