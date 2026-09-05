"""Model-under-test adapters for all three M2 providers (design doc M2 Design §2). AnthropicAdapter
and OpenAIAdapter are native clients; OpenRouterAdapter routes through OpenRouter's
OpenAI-compatible endpoint and shares its call logic with OpenAIAdapter via
_openai_compatible_call. build_confusion_matrix (M1) and run_mutation_trials (M2) both call
adapters sequentially by design; concurrency (Engineering Requirement #1) remains explicitly out
of scope. Retry/backoff (Engineering Requirement #2, design doc M3a Design §1) is handled here via
_with_retry, which wraps only the network-call line inside call_with_tools — never the whole
method, so parsing failures (malformed JSON, empty choices, max_tokens truncation) are never
retried, only a genuine rate-limit response.
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from dataclasses import dataclass
from typing import Callable, Literal, Protocol, TypeVar

import anthropic
import openai
from mcp.types import Tool

T = TypeVar("T")


def _with_retry(
    fn: Callable[[], T],
    *,
    max_retries: int = 5,
    base_delay: float = 1.0,
    sleep_fn: Callable[[float], None] | None = None,
) -> T:
    """Retry a network call on a rate-limit error only (design doc M3a Design §1) — never on a
    parsing failure, which retrying can't fix. Exponential backoff with jitter; re-raises after
    max_retries so a persistent outage is never silently swallowed. sleep_fn is injectable so
    tests run instantly instead of actually sleeping; it defaults to None (rather than binding
    time.sleep at function-definition time) so that `time.sleep` is looked up fresh on every
    call — a `monkeypatch.setattr("toolfit.run.adapters.time.sleep", ...)` in a test would have
    no effect on an already-bound default parameter."""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except (
            anthropic.RateLimitError,
            openai.RateLimitError,
            anthropic.InternalServerError,  # includes 529 "overloaded", Anthropic's most common transient
            openai.InternalServerError,
        ) as e:
            if attempt == max_retries:
                raise
            delay = base_delay * (2**attempt) + random.uniform(0, base_delay)
            print(
                f"WARNING: {type(e).__name__}, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})",
                file=sys.stderr,
            )
            (sleep_fn or time.sleep)(delay)
    raise AssertionError("unreachable")  # every loop iteration above either returns or re-raises


@dataclass
class ToolCall:
    tool_name: str | None  # None means the model made no tool call at all
    arguments: dict
    call_id: str = ""  # provider's id for the call; needed to hand a result back in multi-step runs


ResultFor = Callable[[ToolCall], dict]


class ModelAdapter(Protocol):
    def call_with_tools(self, *, task_text: str, tools: list[Tool]) -> ToolCall: ...


def run_steps(
    adapter: ModelAdapter, *, task_text: str, tools: list[Tool], max_steps: int, result_for: ResultFor
) -> list[ToolCall]:
    """Multi-step trial (design doc M5): let the model make up to `max_steps` calls, feeding each
    a synthetic result from `result_for`. Adapters that implement `run` own their provider's
    multi-turn message format; anything else (test fakes) is treated as single-step."""
    run = getattr(adapter, "run", None)
    if run is None or max_steps <= 1:
        call = adapter.call_with_tools(task_text=task_text, tools=tools)
        return [call] if call.tool_name is not None else []
    return run(task_text=task_text, tools=tools, max_steps=max_steps, result_for=result_for)


def _result_text(result_for: ResultFor, call: ToolCall) -> str:
    return json.dumps(result_for(call))


def _block_dict(block: object) -> dict:
    dump = getattr(block, "model_dump", None)
    return dump(exclude_none=True) if dump else dict(vars(block))


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
        calls = self.run(task_text=task_text, tools=tools, max_steps=1, result_for=lambda _: {})
        return calls[0] if calls else ToolCall(tool_name=None, arguments={})

    def run(self, *, task_text: str, tools: list[Tool], max_steps: int, result_for: ResultFor) -> list[ToolCall]:
        messages: list[dict] = [{"role": "user", "content": task_text}]
        calls: list[ToolCall] = []
        while len(calls) < max_steps:
            response = _with_retry(
                lambda: self._client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    tools=[_tool_to_anthropic_schema(t) for t in tools],
                    messages=messages,
                )
            )
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if not tool_uses:
                if response.stop_reason == "max_tokens":
                    # Adaptive thinking can spend the whole budget before a tool_use block — a real
                    # no-call outcome, scored as a miss by the grader, never a crash here.
                    print("WARNING: response truncated at max_tokens before a tool_use block was found", file=sys.stderr)
                break
            # Blocks go back verbatim (thinking blocks carry signatures the API checks).
            messages.append({"role": "assistant", "content": [_block_dict(b) for b in response.content]})
            results = []
            for b in tool_uses:
                call = ToolCall(tool_name=b.name, arguments=b.input, call_id=getattr(b, "id", ""))
                calls.append(call)
                results.append({"type": "tool_result", "tool_use_id": call.call_id, "content": _result_text(result_for, call)})
            messages.append({"role": "user", "content": results})
        return calls


def _openai_compatible_run(
    client: openai.OpenAI, *, model: str, task_text: str, tools: list[Tool], max_steps: int, result_for: ResultFor
) -> list[ToolCall]:
    """Shared multi-step body for any OpenAI-function-calling-compatible provider (OpenAI itself,
    OpenRouter's endpoint). Request/response shapes are identical; only base_url/api_key differ."""
    messages: list[dict] = [{"role": "user", "content": task_text}]
    calls: list[ToolCall] = []
    tool_specs = [
        {"type": "function", "function": {"name": t.name, "description": t.description or "", "parameters": t.input_schema}}
        for t in tools
    ]
    while len(calls) < max_steps:
        response = _with_retry(lambda: client.chat.completions.create(model=model, messages=messages, tools=tool_specs))
        if not response.choices:
            # Gateways (OpenRouter especially) return an empty choices array on an upstream error —
            # a real no-call outcome, scored as a miss rather than an IndexError mid-catalog.
            print("WARNING: response had no choices (upstream provider error?)", file=sys.stderr)
            break
        message = response.choices[0].message
        if not message.tool_calls:
            break
        messages.append(
            {
                "role": "assistant",
                "content": getattr(message, "content", None),
                "tool_calls": [
                    {
                        "id": getattr(tc, "id", ""),
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in message.tool_calls
                ],
            }
        )
        for tc in message.tool_calls:
            call_id = getattr(tc, "id", "")
            try:
                arguments = json.loads(tc.function.arguments)
                call = ToolCall(tool_name=tc.function.name, arguments=arguments, call_id=call_id)
            except json.JSONDecodeError:
                # Malformed tool-call JSON is a model-output problem, not a server schema problem:
                # record a no-call (the grader scores it as a miss) instead of letting the
                # ValueError subclass reach confusion.py's schema-error handler.
                print(f"WARNING: model returned malformed tool-call JSON arguments: {tc.function.arguments!r}", file=sys.stderr)
                call = ToolCall(tool_name=None, arguments={}, call_id=call_id)
            calls.append(call)
            messages.append({"role": "tool", "tool_call_id": call_id, "content": _result_text(result_for, call)})
    return calls


def _openai_compatible_call(client: openai.OpenAI, *, model: str, task_text: str, tools: list[Tool]) -> ToolCall:
    calls = _openai_compatible_run(client, model=model, task_text=task_text, tools=tools, max_steps=1, result_for=lambda _: {})
    return calls[0] if calls else ToolCall(tool_name=None, arguments={})


class OpenAIAdapter:
    """Native OpenAI adapter (design doc M2 Design §2) — the second of the three M2 provider
    adapters, sharing its call logic with OpenRouterAdapter via _openai_compatible_call."""

    MODEL = "gpt-5.5"

    def __init__(self, client: openai.OpenAI, model: str | None = None):
        self._client = client
        self.model = model or self.MODEL

    def call_with_tools(self, *, task_text: str, tools: list[Tool]) -> ToolCall:
        return _openai_compatible_call(self._client, model=self.model, task_text=task_text, tools=tools)

    def run(self, *, task_text: str, tools: list[Tool], max_steps: int, result_for: ResultFor) -> list[ToolCall]:
        return _openai_compatible_run(
            self._client, model=self.model, task_text=task_text, tools=tools, max_steps=max_steps, result_for=result_for
        )


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

    def run(self, *, task_text: str, tools: list[Tool], max_steps: int, result_for: ResultFor) -> list[ToolCall]:
        return _openai_compatible_run(
            self._client, model=self.model, task_text=task_text, tools=tools, max_steps=max_steps, result_for=result_for
        )


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
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError(f"ANTHROPIC_API_KEY is not set — required to run model {model!r}")
        return AnthropicAdapter(anthropic.Anthropic(), model=model)
    if provider == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError(f"OPENAI_API_KEY is not set — required to run model {model!r}")
        return OpenAIAdapter(openai.OpenAI(), model=model)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(f"OPENROUTER_API_KEY is not set — required to run model {model!r}")
    return OpenRouterAdapter(openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key), model=model)
