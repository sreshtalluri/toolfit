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
    # stop_reason="end_turn" here (a real, non-truncated turn) — distinct from the max_tokens
    # truncation case covered below, since only the latter should print a warning.
    fake_response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="Sure, I can help.")], stop_reason="end_turn"
    )
    adapter = AnthropicAdapter(_FakeAnthropicClient(fake_response))
    result = adapter.call_with_tools(task_text="hello", tools=TOOLS)
    assert result == ToolCall(tool_name=None, arguments={})


def test_call_with_tools_warns_on_truncation_before_a_tool_use_block(capsys):
    # Real risk (design doc / Fix 1): Sonnet 5 runs adaptive thinking by default, and thinking
    # tokens count against max_tokens. If the response is truncated before a tool_use block is
    # emitted, grade() would otherwise silently score this identically to a genuine model
    # failure (no_call=True) — which can manufacture a false "IMPROVED" mutation result. This
    # must be visible on stderr, not silent.
    fake_response = SimpleNamespace(content=[], stop_reason="max_tokens")
    adapter = AnthropicAdapter(_FakeAnthropicClient(fake_response))
    result = adapter.call_with_tools(task_text="hello", tools=TOOLS)
    assert result == ToolCall(tool_name=None, arguments={})
    captured = capsys.readouterr()
    assert "truncated" in captured.err
    assert "max_tokens" in captured.err


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


def test_anthropic_adapter_accepts_a_custom_model():
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(stop_reason="end_turn", content=[])

    fake_client = SimpleNamespace(messages=SimpleNamespace(create=create))
    adapter = AnthropicAdapter(fake_client, model="claude-opus-5")
    adapter.call_with_tools(task_text="hi", tools=[])

    assert captured["model"] == "claude-opus-5"


def test_anthropic_adapter_defaults_to_the_class_model():
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(stop_reason="end_turn", content=[])

    fake_client = SimpleNamespace(messages=SimpleNamespace(create=create))
    adapter = AnthropicAdapter(fake_client)
    adapter.call_with_tools(task_text="hi", tools=[])

    assert captured["model"] == AnthropicAdapter.MODEL


def test_every_adapter_exposes_a_public_model_attribute():
    # build_confusion_matrix records run metadata via `getattr(adapter, "model", "unknown")`, so an
    # adapter that keeps its model private silently labels the whole report's model "unknown".
    from toolfit.run.adapters import OpenRouterAdapter

    assert AnthropicAdapter(_FakeAnthropicClient(None), model="claude-opus-5").model == "claude-opus-5"
    assert OpenRouterAdapter(None, model="openai/gpt-4o").model == "openai/gpt-4o"


from toolfit.run.adapters import OpenAIAdapter, build_adapter, infer_provider


def test_infer_provider_recognizes_claude_models():
    assert infer_provider("claude-sonnet-5") == "anthropic"
    assert infer_provider("claude-opus-5") == "anthropic"


def test_infer_provider_recognizes_openai_models():
    assert infer_provider("gpt-5.5") == "openai"
    assert infer_provider("o3-mini") == "openai"


def test_infer_provider_recognizes_openrouter_models_by_slash():
    assert infer_provider("qwen/qwen-2.5-72b-instruct") == "openrouter"
    assert infer_provider("openai/gpt-5.5") == "openrouter"  # OpenRouter's own naming, not direct OpenAI


def test_infer_provider_defaults_to_anthropic_for_an_unrecognized_name():
    assert infer_provider("some-custom-finetune") == "anthropic"


def test_openai_adapter_parses_a_tool_call():
    fake_call = _FakeToolCall("create_task", json.dumps({"title": "Buy milk", "priority": "low"}))
    fake_response = _FakeOpenAIResponse(choices=[_FakeOpenAIChoice(_FakeOpenAIMessage(tool_calls=[fake_call]))])
    adapter = OpenAIAdapter(_FakeOpenAIClient(fake_response), model="gpt-5.5")
    result = adapter.call_with_tools(task_text="buy milk, low priority", tools=TOOLS)
    assert result.tool_name == "create_task"
    assert result.arguments == {"title": "Buy milk", "priority": "low"}


def test_openai_adapter_returns_none_with_no_tool_calls():
    fake_response = _FakeOpenAIResponse(choices=[_FakeOpenAIChoice(_FakeOpenAIMessage(tool_calls=None))])
    adapter = OpenAIAdapter(_FakeOpenAIClient(fake_response), model="gpt-5.5")
    result = adapter.call_with_tools(task_text="hello", tools=TOOLS)
    assert result.tool_name is None


def test_openai_adapter_defaults_to_its_class_model_constant():
    adapter = OpenAIAdapter(_FakeOpenAIClient(None))
    assert adapter.model == OpenAIAdapter.MODEL


def test_build_adapter_raises_a_clear_error_when_openai_key_is_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    try:
        build_adapter("gpt-5.5")
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "OPENAI_API_KEY" in str(e)


def test_build_adapter_raises_a_clear_error_when_openrouter_key_is_missing(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    try:
        build_adapter("qwen/qwen-2.5-72b-instruct")
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "OPENROUTER_API_KEY" in str(e)
