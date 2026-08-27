"""Adapter tests use a fake Anthropic response object rather than a real API call — the real
model's actual behavior is proven separately by the e2e test (Task 11), which needs a live key.
This test only proves the adapter correctly translates an Anthropic tool_use block into a
ToolCall, and correctly returns tool_name=None when the model makes no tool call."""

from types import SimpleNamespace

from mcp.types import Tool

from toolfit.run.adapters import AnthropicAdapter, ToolCall

TOOLS = [
    Tool(
        name="create_task",
        description="Add a new task.",
        input_schema={"type": "object", "properties": {"title": {"type": "string"}, "priority": {"type": "string"}}},
    )
]


class _FakeMessages:
    def __init__(self, response):
        self._response = response

    def create(self, **kwargs):
        return self._response


class _FakeAnthropicClient:
    def __init__(self, response):
        self.messages = _FakeMessages(response)


def test_call_with_tools_extracts_a_tool_use_block():
    fake_response = SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", name="create_task", input={"title": "Buy milk", "priority": "low"})]
    )
    adapter = AnthropicAdapter(_FakeAnthropicClient(fake_response))
    result = adapter.call_with_tools(task_text="Add a task to buy milk, low priority", tools=TOOLS)
    assert result == ToolCall(tool_name="create_task", arguments={"title": "Buy milk", "priority": "low"})


def test_call_with_tools_returns_none_when_model_makes_no_tool_call():
    fake_response = SimpleNamespace(content=[SimpleNamespace(type="text", text="Sure, I can help.")])
    adapter = AnthropicAdapter(_FakeAnthropicClient(fake_response))
    result = adapter.call_with_tools(task_text="hello", tools=TOOLS)
    assert result == ToolCall(tool_name=None, arguments={})


import json

from toolfit.run.adapters import OpenRouterAdapter


class _FakeFunction:
    def __init__(self, name, arguments_json):
        self.name = name
        self.arguments = arguments_json


class _FakeToolCall:
    def __init__(self, name, arguments_json):
        self.function = _FakeFunction(name, arguments_json)


class _FakeOpenAIMessage:
    def __init__(self, tool_calls):
        self.tool_calls = tool_calls


class _FakeOpenAIChoice:
    def __init__(self, message):
        self.message = message


class _FakeOpenAIResponse:
    def __init__(self, choices):
        self.choices = choices


class _FakeCompletions:
    def __init__(self, response):
        self._response = response

    def create(self, **kwargs):
        return self._response


class _FakeChat:
    def __init__(self, response):
        self.completions = _FakeCompletions(response)


class _FakeOpenAIClient:
    def __init__(self, response):
        self.chat = _FakeChat(response)


def test_openrouter_adapter_parses_a_tool_call():
    fake_call = _FakeToolCall("create_task", json.dumps({"title": "Buy milk", "priority": "low"}))
    fake_response = _FakeOpenAIResponse(choices=[_FakeOpenAIChoice(_FakeOpenAIMessage(tool_calls=[fake_call]))])
    adapter = OpenRouterAdapter(_FakeOpenAIClient(fake_response), model="test/model")
    result = adapter.call_with_tools(task_text="buy milk, low priority", tools=TOOLS)
    assert result.tool_name == "create_task"
    assert result.arguments == {"title": "Buy milk", "priority": "low"}


def test_openrouter_adapter_returns_none_with_no_tool_calls():
    fake_response = _FakeOpenAIResponse(choices=[_FakeOpenAIChoice(_FakeOpenAIMessage(tool_calls=None))])
    adapter = OpenRouterAdapter(_FakeOpenAIClient(fake_response), model="test/model")
    result = adapter.call_with_tools(task_text="hello", tools=TOOLS)
    assert result.tool_name is None
