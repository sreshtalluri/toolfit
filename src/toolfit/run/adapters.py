"""Model-under-test adapters for all three M2 providers (design doc M2 Design §2). AnthropicAdapter
and OpenAIAdapter are native clients; OpenRouterAdapter routes through OpenRouter's
OpenAI-compatible endpoint and shares its call logic with OpenAIAdapter via
_openai_compatible_call. No retry/backoff or concurrency here — build_confusion_matrix (M1) and
run_mutation_trials (M2) both call adapters sequentially by design; concurrency (Engineering
Requirement #1) and retry/backoff (Engineering Requirement #2) remain explicitly out of scope.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Literal, Protocol

import anthropic
import openai
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
            # Sonnet 5's adaptive thinking can consume the whole budget before reaching a
            # tool_use block — this is a real no-call outcome, not a bug in this adapter, and
            # scoring it (grade/grader.py) treats it as a miss rather than a crash. Grading logic
            # never lives here — that's a separate, out-of-scope concern.
            print(
                "WARNING: response truncated at max_tokens before a tool_use block was found",
                file=sys.stderr,
            )
        return ToolCall(tool_name=None, arguments={})


def _openai_compatible_call(client: openai.OpenAI, *, model: str, task_text: str, tools: list[Tool]) -> ToolCall:
    """Shared call_with_tools body for any OpenAI-function-calling-compatible provider (OpenAI
    itself, OpenRouter's OpenAI-compatible endpoint). The request/response shape is identical;
    only the client's base_url/api_key differ, which the caller already configured."""
    response = client.chat.completions.create(
        model=model,
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


class OpenAIAdapter:
    """Native OpenAI adapter (design doc M2 Design §2) — the second of the three M2 provider
    adapters, sharing its call logic with OpenRouterAdapter via _openai_compatible_call."""

    MODEL = "gpt-5.5"

    def __init__(self, client: openai.OpenAI, model: str | None = None):
        self._client = client
        self.model = model or self.MODEL

    def call_with_tools(self, *, task_text: str, tools: list[Tool]) -> ToolCall:
        return _openai_compatible_call(self._client, model=self.model, task_text=task_text, tools=tools)


class OpenRouterAdapter:
    """Third M2 adapter, routed through OpenRouter's OpenAI-compatible endpoint (design doc M2
    Design §2) — promoted from the spike's compatibility-check-only role now that M2 wires it in
    as a real adapter, sharing call logic with OpenAIAdapter via _openai_compatible_call. `.model`
    is public (not `_model`) so report renderers can read the model under test off the adapter
    via `getattr(adapter, "model", ...)`, matching AnthropicAdapter/OpenAIAdapter."""

    def __init__(self, client: openai.OpenAI, model: str):
        self._client = client
        self.model = model

    def call_with_tools(self, *, task_text: str, tools: list[Tool]) -> ToolCall:
        return _openai_compatible_call(self._client, model=self.model, task_text=task_text, tools=tools)


Provider = Literal["anthropic", "openai", "openrouter"]

_OPENAI_MODEL_PREFIXES = ("gpt", "o1", "o3", "o4")


def infer_provider(model: str) -> Provider:
    """Infer which adapter a --model string names (design doc M2 Design §2): '/' in the name is
    OpenRouter's own vendor/model convention (e.g. "qwen/qwen-2.5-72b-instruct", or even
    "openai/gpt-5.5" when routed through OpenRouter rather than called directly); a claude* name
    is Anthropic; a gpt*/o1*/o3*/o4* name is OpenAI; anything else defaults to Anthropic, matching
    the CLI's existing default model."""
    if "/" in model:
        return "openrouter"
    if model.startswith("claude"):
        return "anthropic"
    if model.startswith(_OPENAI_MODEL_PREFIXES):
        return "openai"
    return "anthropic"


def build_adapter(model: str) -> ModelAdapter:
    """Construct the right client and adapter for --model, reading API keys from the environment
    (design doc M2 Design §2 — bring-your-own-key, Premise 7). Raises RuntimeError with a clear
    message on a missing key, before any network call, so the CLI can catch it and print a clean
    error instead of a raw SDK traceback."""
    provider = infer_provider(model)
    if provider == "anthropic":
        return AnthropicAdapter(anthropic.Anthropic(), model=model)
    if provider == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError(f"OPENAI_API_KEY is not set — required to run model {model!r}")
        return OpenAIAdapter(openai.OpenAI(), model=model)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(f"OPENROUTER_API_KEY is not set — required to run model {model!r}")
    return OpenRouterAdapter(openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key), model=model)
