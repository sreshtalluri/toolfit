"""Minimal model-under-test adapters. AnthropicAdapter is the primary adapter; OpenRouterAdapter
is a compatibility-check-only adapter added in an earlier milestone, per design doc Next Steps #1.
No retry/backoff or concurrency here — build_confusion_matrix (M1) already drives many sequential
requests through these adapters, and that remains explicitly out of scope: concurrency (Engineering
Requirement #1) and retry/backoff (Engineering Requirement #2) are M2 work per the design doc, not
M1.
"""

from __future__ import annotations

import json
import sys
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

    def __init__(self, client: anthropic.Anthropic, model: str | None = None):
        self._client = client
        self.model = model or self.MODEL

    def call_with_tools(self, *, task_text: str, tools: list[Tool]) -> ToolCall:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=2000,
            tools=[_tool_to_anthropic_schema(t) for t in tools],
            messages=[{"role": "user", "content": task_text}],
        )
        for block in response.content:
            if block.type == "tool_use":
                return ToolCall(tool_name=block.name, arguments=block.input)
        if response.stop_reason == "max_tokens":
            # Sonnet 5 runs adaptive thinking by default and thinking tokens count against
            # max_tokens — if we truncate before a tool_use block appears, falling through to
            # the no-call return below is indistinguishable from a real model failure to
            # grade() (it scores no_call=True either way). That can manufacture a false
            # "IMPROVED" mutation result (a truncated "before" + a clean "after" looks like
            # improvement that never happened). Surface it loudly instead of miscounting it
            # silently. Not restructuring ToolCall/GradeResult to add a real "truncated" state
            # here — that's a separate, out-of-scope concern.
            print(
                "WARNING: response truncated at max_tokens before a tool_use block was found",
                file=sys.stderr,
            )
        return ToolCall(tool_name=None, arguments={})


class OpenRouterAdapter:
    """Compatibility check adapter (design doc Next Steps #1, TODO 4 — validates OpenRouter's
    tool-call behavior before M2 commits to it as a full third adapter). Uses OpenRouter's
    OpenAI-compatible API, not a bespoke client."""

    def __init__(self, client, model: str):
        self._client = client  # an openai.OpenAI configured with base_url="https://openrouter.ai/api/v1"
        self._model = model

    def call_with_tools(self, *, task_text: str, tools: list[Tool]) -> ToolCall:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": task_text}],
            tools=[
                {
                    "type": "function",
                    "function": {"name": t.name, "description": t.description or "", "parameters": t.input_schema},
                }
                for t in tools
            ],
        )
        message = response.choices[0].message
        if message.tool_calls:
            call = message.tool_calls[0]
            return ToolCall(tool_name=call.function.name, arguments=json.loads(call.function.arguments))
        return ToolCall(tool_name=None, arguments={})
