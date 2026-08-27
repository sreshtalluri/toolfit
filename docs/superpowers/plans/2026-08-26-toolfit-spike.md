# toolfit Weekend Spike Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the core toolfit loop end-to-end — sample ground truth from a schema, generate a task without naming the tool, run a real model against it, grade structurally, mutate one description, re-measure, and propose+validate a fix — against one toy 3-tool MCP server.

**Architecture:** Real target module names from day one (`connect/`, `gen/`, `run/`, `grade/`, `fix/`, `report/`) so working code graduates into M0/M1 rather than being rebuilt (design doc Premise 5: disposable scope, not disposable code). Dry-run only — the harness fetches the toy server's tool catalog and reasons about which tool a model *would* call, but never executes a real call against the target's backend.

**Tech Stack:** Python 3.10+, official `mcp` SDK v2 (`Client` + `StdioServerParameters`), Anthropic Python SDK (generator + model-under-test + fixer), OpenAI SDK pointed at OpenRouter (compatibility check only), pytest + pytest-asyncio.

**Spec:** `docs/designs/toolfit-v0-scope.md` (Next Steps #1 — the spike; Premise 5; Engineering Requirement #5; "Residual circularity risk" under The Core Technique). Executors should read that doc's Pipeline section alongside this plan.

## Global Constraints

- Dry-run only: never call a tool against the toy server's real backend, only `tools/list` for the catalog (spec: Constraints, Premise 1 spirit).
- `gen/` and `fix/` require an eval-style test (asserts output *quality*, not just "returned a string"), not just unit tests (spec: Engineering Requirement #5).
- Any mutation or fix result — improved, worsened, or unchanged — is reported explicitly, never suppressed (spec: Failure Modes).
- A hallucinated/nonexistent tool call from the model under test is scored as a miss, never a crash (spec: Failure Modes).
- A fix-generation result that's empty, identical to the original, or under 10 characters is rejected before re-measurement (spec: Failure Modes).
- API keys come from environment variables only (`ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`) — never a CLI flag (spec: Engineering Requirement #3).
- Real JSON Schema complexity (`$ref`, `oneOf`/`anyOf`/`allOf`, formats, regex) and canonicalized structural matching are explicitly OUT of scope for this spike — they're M1 work (spec: Next Steps #3). The spike's schema sampler only needs to handle flat string-typed properties, and must raise loudly (not guess) on anything else.
- Markdown output only — no HTML report, no CI, no multi-model concurrency (spec: Next Steps #1).

---

### Task 1: Project scaffolding, toy MCP server, and catalog fetch

**Files:**
- Create: `pyproject.toml`
- Create: `src/toolfit/__init__.py`
- Create: `src/toolfit/connect/__init__.py`
- Create: `src/toolfit/connect/client.py`
- Create: `src/toolfit/gen/__init__.py`
- Create: `src/toolfit/run/__init__.py`
- Create: `src/toolfit/grade/__init__.py`
- Create: `src/toolfit/fix/__init__.py`
- Create: `src/toolfit/report/__init__.py`
- Create: `examples/toy_server.py`
- Test: `tests/test_toy_server.py`

**Interfaces:**
- Produces: an MCP stdio server, launchable via `uv run examples/toy_server.py`, exposing three tools: `create_task(title: str, priority: str) -> str`, `update_task(task_id: str, title: str) -> str`, `list_tasks(status: str) -> str`. `create_task` and `update_task` intentionally share the identical docstring `"Add a new task."` — this is the deliberate ambiguity the spike's mutation test targets. Also produces `ToolCatalog` (fields: `tools: list[mcp.types.Tool]`; methods: `get(name: str) -> Tool | None`, `names() -> list[str]`), `server_params(script_path: str) -> StdioServerParameters`, `async fetch_catalog(params: StdioServerParameters) -> ToolCatalog`. Every later task that touches a tool catalog imports `ToolCatalog` from `toolfit.connect.client`.

Scaffolding and the toy server are bundled with `connect/` in one task, not split, because neither is independently verifiable — testing "does the toy server work" *is* testing "does connect/ talk to it correctly."

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "toolfit"
version = "0.0.1"
description = "Finds the specific places your MCP server confuses models, and proves a fix with a before-and-after eval."
requires-python = ">=3.10"
license = "MIT"
dependencies = [
    "mcp>=2.0,<3",
    "anthropic>=0.40",
    "openai>=1.50",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.hatch.build.targets.wheel]
packages = ["src/toolfit"]
```

- [ ] **Step 2: Create empty package `__init__.py` files**

```bash
mkdir -p src/toolfit/connect src/toolfit/gen src/toolfit/run src/toolfit/grade src/toolfit/fix src/toolfit/report
touch src/toolfit/__init__.py src/toolfit/connect/__init__.py src/toolfit/gen/__init__.py src/toolfit/run/__init__.py src/toolfit/grade/__init__.py src/toolfit/fix/__init__.py src/toolfit/report/__init__.py
```

- [ ] **Step 3: Write the toy server**

```python
# examples/toy_server.py
"""Toy MCP server for the toolfit spike — 3 tools, one intentionally ambiguous pair.

create_task and update_task share the identical docstring on purpose: this is the realistic
"copy-pasted description" bug the spike's mutation test (grade/mutator.py) is built to find
and, via fix/fixer.py, propose a fix for.
"""

from mcp.server import MCPServer

mcp = MCPServer("ToyTasks")

_TASKS: dict[str, dict] = {}
_NEXT_ID = 1


@mcp.tool()
def create_task(title: str, priority: str) -> str:
    """Add a new task."""
    global _NEXT_ID
    task_id = f"t{_NEXT_ID}"
    _NEXT_ID += 1
    _TASKS[task_id] = {"title": title, "priority": priority, "status": "open"}
    return f"Created task {task_id}: {title} (priority: {priority})"


@mcp.tool()
def update_task(task_id: str, title: str) -> str:
    """Add a new task."""
    if task_id not in _TASKS:
        return f"No such task: {task_id}"
    _TASKS[task_id]["title"] = title
    return f"Updated task {task_id}: {title}"


@mcp.tool()
def list_tasks(status: str) -> str:
    """List all tasks, optionally filtered by status (open, done)."""
    matches = [f"{tid}: {t['title']}" for tid, t in _TASKS.items() if t["status"] == status]
    return "\n".join(matches) if matches else f"No tasks with status {status!r}"


if __name__ == "__main__":
    mcp.run()
```

- [ ] **Step 4: Write the failing test**

```python
# tests/test_toy_server.py
"""Confirms the toy server actually starts over stdio and exposes the expected 3 tools with the
intentional description bug — the fixture every other test in this plan depends on."""

import pytest

from toolfit.connect.client import fetch_catalog, server_params


@pytest.mark.asyncio
async def test_toy_server_exposes_three_tools_with_the_intentional_bug():
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)
    assert catalog.names() == ["create_task", "update_task", "list_tasks"]
    assert catalog.get("create_task").description == catalog.get("update_task").description == "Add a new task."
```

- [ ] **Step 5: Run test to verify it fails**

Run: `uv sync --extra dev && uv run pytest tests/test_toy_server.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'toolfit.connect.client'`

- [ ] **Step 6: Write `connect/client.py`**

```python
# src/toolfit/connect/client.py
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
```

- [ ] **Step 7: Run test to verify it passes**

Run: `uv run pytest tests/test_toy_server.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml src/toolfit examples/toy_server.py tests/test_toy_server.py
git commit -m "spike: scaffold project, toy MCP server, and connect/ catalog fetch"
```

---

### Task 2: gen/schema_sampler.py — ground-truth argument sampling

**Files:**
- Create: `src/toolfit/gen/schema_sampler.py`
- Test: `tests/test_schema_sampler.py`

**Interfaces:**
- Consumes: nothing from earlier tasks (pure function over a JSON Schema dict).
- Produces: `sample_arguments(schema: dict, *, seed: int) -> dict[str, str]`. Task 3 (taskgen) and the e2e task (Task 11) consume this.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_schema_sampler.py
import pytest

from toolfit.gen.schema_sampler import sample_arguments

CREATE_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "priority": {"type": "string"},
    },
    "required": ["title", "priority"],
}


def test_sample_arguments_returns_all_required_properties():
    result = sample_arguments(CREATE_TASK_SCHEMA, seed=1)
    assert set(result.keys()) == {"title", "priority"}


def test_sample_arguments_is_deterministic_for_same_seed():
    first = sample_arguments(CREATE_TASK_SCHEMA, seed=42)
    second = sample_arguments(CREATE_TASK_SCHEMA, seed=42)
    assert first == second


def test_sample_arguments_rejects_non_object_schema():
    with pytest.raises(ValueError, match="expected object schema"):
        sample_arguments({"type": "string"}, seed=1)


def test_sample_arguments_rejects_unknown_property_name():
    schema = {
        "type": "object",
        "properties": {"unregistered_field": {"type": "string"}},
        "required": ["unregistered_field"],
    }
    with pytest.raises(ValueError, match="no example values registered"):
        sample_arguments(schema, seed=1)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_schema_sampler.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'toolfit.gen.schema_sampler'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/toolfit/gen/schema_sampler.py
"""Sample one concrete, valid argument set from a tool's JSON Schema.

Spike scope only: handles the flat string-typed schemas used by examples/toy_server.py. Real
$ref/oneOf/anyOf/allOf/format/regex/nullable/dependent-constraint handling is explicitly scoped
to M1 (docs/designs/toolfit-v0-scope.md, Next Steps #3), not this spike.
"""

from __future__ import annotations

import random

# Deterministic example values per parameter name, so spike runs are reproducible without an
# LLM call for sampling itself (that call is reserved for the *task generator*, see taskgen.py).
_EXAMPLES: dict[str, list[str]] = {
    "title": ["Write Q3 report", "Fix login bug", "Book dentist appointment"],
    "priority": ["high", "medium", "low"],
    "task_id": ["t1", "t2", "t3"],
    "status": ["open", "done"],
}


def sample_arguments(schema: dict, *, seed: int) -> dict[str, str]:
    """Sample one valid argument value per property in `schema`.

    Only handles `type: object` schemas whose properties are `type: string` with no
    `enum`/`format`/`$ref` — the toy server's shape. Raises ValueError on anything more complex,
    on purpose: a spike that silently produces wrong samples on schemas it doesn't understand is
    worse than one that fails loudly (same "never suppress" ethos as the design doc's Failure
    Modes).
    """
    rng = random.Random(seed)
    if schema.get("type") != "object":
        raise ValueError(f"sample_arguments: expected object schema, got {schema.get('type')!r}")
    result: dict[str, str] = {}
    for prop_name, prop_schema in schema.get("properties", {}).items():
        if prop_schema.get("type") != "string":
            raise ValueError(
                f"sample_arguments: unsupported property type for {prop_name!r}: {prop_schema.get('type')!r}"
            )
        choices = _EXAMPLES.get(prop_name)
        if not choices:
            raise ValueError(f"sample_arguments: no example values registered for property {prop_name!r}")
        result[prop_name] = rng.choice(choices)
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_schema_sampler.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/gen/schema_sampler.py tests/test_schema_sampler.py
git commit -m "spike: gen/schema_sampler deterministically samples ground-truth arguments"
```

---

### Task 3: gen/taskgen.py — inverted task generation

**Files:**
- Create: `src/toolfit/gen/taskgen.py`
- Test: `tests/test_taskgen_eval.py`

**Interfaces:**
- Consumes: nothing structurally (takes plain `tool_name`, `tool_description`, `arguments` — decoupled from `ToolCatalog` so it's easy to unit-test).
- Produces: `GeneratedTask` (fields: `text: str`, `tool_name: str`, `arguments: dict[str, str]`), `generate_task(client, *, tool_name, tool_description, arguments, withhold_description=False) -> GeneratedTask`, `check_no_leakage(task, *, catalog_tool_names: list[str]) -> bool`. Task 5 (grader), Task 6 (mutator), and later scripts consume `GeneratedTask`.

- [ ] **Step 1: Write the failing eval-style tests**

This is an eval suite, not plain unit tests (Global Constraints: `gen/` needs one) — it asserts *quality* properties of a real LLM call, not just "returned a string." Requires `ANTHROPIC_API_KEY`; skipped otherwise so the rest of the suite still runs without one.

```python
# tests/test_taskgen_eval.py
"""Eval suite for gen/taskgen.py. The risk here is OUTPUT QUALITY (a generated task that leaks
the tool name, or is unrelated to the sampled arguments), not "did it return a string" — plain
unit tests can't catch that, so this calls the real generator model."""

import os

import anthropic
import pytest

from toolfit.gen.taskgen import check_no_leakage, generate_task

pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY")


@pytest.fixture
def client():
    return anthropic.Anthropic()


def test_generated_task_does_not_leak_any_tool_name(client):
    task = generate_task(
        client,
        tool_name="create_task",
        tool_description="Add a new task.",
        arguments={"title": "Write report", "priority": "high"},
    )
    assert check_no_leakage(task, catalog_tool_names=["create_task", "update_task", "list_tasks"])


def test_generated_task_is_traceable_to_the_sampled_arguments(client):
    task = generate_task(
        client,
        tool_name="create_task",
        tool_description="Add a new task.",
        arguments={"title": "Write report", "priority": "high"},
    )
    # Quality bar: the sentence must be about the sampled args, or grading against them later
    # is meaningless — this is what a bare "did it return non-empty string" check would miss.
    assert "report" in task.text.lower()


def test_withheld_description_still_produces_a_usable_task(client):
    task = generate_task(
        client,
        tool_name="create_task",
        tool_description="Add a new task.",
        arguments={"title": "Write report", "priority": "high"},
        withhold_description=True,
    )
    assert len(task.text) > 0
    assert check_no_leakage(task, catalog_tool_names=["create_task", "update_task", "list_tasks"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_taskgen_eval.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'toolfit.gen.taskgen'` (if `ANTHROPIC_API_KEY` is unset, these instead SKIP — set the key locally to actually exercise Steps 1-2 as intended)

- [ ] **Step 3: Write minimal implementation**

```python
# src/toolfit/gen/taskgen.py
"""Inverted task generation (design doc "The Core Technique").

Samples a ground-truth (tool, arguments) tuple FIRST (schema_sampler.py), then asks a generator
model to write the natural-language request that leads to exactly those arguments, without
naming the tool. Grading (grade/grader.py) compares the model-under-test's actual call against
this sampled tuple — never against the generator's opinion.
"""

from __future__ import annotations

from dataclasses import dataclass

import anthropic

GENERATOR_MODEL = "claude-sonnet-5"

_PROMPT_TEMPLATE = """A user wants to trigger this action:
{description_line}It requires exactly these arguments: {arguments}

Write ONE short, natural sentence a real user would type to a task-management assistant that \
would require calling that action with exactly those arguments. Do not name or hint at any \
internal function/tool/method name — describe only what the user wants, in plain language. \
Reply with just the sentence, nothing else."""


@dataclass
class GeneratedTask:
    text: str
    tool_name: str
    arguments: dict[str, str]


def generate_task(
    client: anthropic.Anthropic,
    *,
    tool_name: str,
    tool_description: str,
    arguments: dict[str, str],
    withhold_description: bool = False,
) -> GeneratedTask:
    """Generate the natural-language request for a sampled (tool, arguments) tuple.

    `withhold_description` is the spike's circularity check (scripts/circularity_check.py,
    design doc "Residual circularity risk"): when True, the prompt never sees the tool's own
    description text, only the sampled arguments.
    """
    description_line = "" if withhold_description else f"Action description: {tool_description}\n"
    prompt = _PROMPT_TEMPLATE.format(description_line=description_line, arguments=arguments)
    response = client.messages.create(
        model=GENERATOR_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    return GeneratedTask(text=text, tool_name=tool_name, arguments=arguments)


def check_no_leakage(task: GeneratedTask, *, catalog_tool_names: list[str]) -> bool:
    """Guardrail (design doc / source doc S4): reject a generated task if it leaks any tool's
    literal name. Returns True if clean. Checked against ALL catalog tool names, not just the
    target — a task that accidentally names a *different* tool is just as invalid.
    """
    lowered = task.text.lower()
    return not any(name.lower() in lowered for name in catalog_tool_names)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `ANTHROPIC_API_KEY=<key> uv run pytest tests/test_taskgen_eval.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/gen/taskgen.py tests/test_taskgen_eval.py
git commit -m "spike: gen/taskgen inverts task generation with a leakage guardrail"
```

---

### Task 4: run/adapters.py — Anthropic model-under-test adapter

**Files:**
- Create: `src/toolfit/run/adapters.py`
- Test: `tests/test_adapters.py`

**Interfaces:**
- Consumes: `mcp.types.Tool` list (from Task 1's `ToolCatalog.tools`).
- Produces: `ToolCall` (fields: `tool_name: str | None`, `arguments: dict`), `ModelAdapter` (Protocol with `call_with_tools(*, task_text: str, tools: list[Tool]) -> ToolCall`), `AnthropicAdapter(client)`. Task 5 (grader), Task 6 (mutator), and the e2e task consume `ToolCall` and `AnthropicAdapter`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_adapters.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_adapters.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'toolfit.run.adapters'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/toolfit/run/adapters.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_adapters.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/run/adapters.py tests/test_adapters.py
git commit -m "spike: run/adapters wraps Anthropic as the first model-under-test"
```

---

### Task 5: grade/grader.py — structural grading

**Files:**
- Create: `src/toolfit/grade/grader.py`
- Test: `tests/test_grader.py`

**Interfaces:**
- Consumes: `GeneratedTask` (Task 3), `ToolCall` (Task 4).
- Produces: `GradeResult` (fields: `correct_tool: bool`, `correct_args: bool`, `hallucinated: bool`, `no_call: bool`; property `passed: bool`), `grade(task, call, *, catalog_tool_names: list[str]) -> GradeResult`. Task 6 (mutator) and the e2e task consume this.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_grader.py
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.grader import grade
from toolfit.run.adapters import ToolCall

TASK = GeneratedTask(
    text="Add a task called Write report with high priority",
    tool_name="create_task",
    arguments={"title": "Write report", "priority": "high"},
)
CATALOG_NAMES = ["create_task", "update_task", "list_tasks"]


def test_grade_passes_on_exact_match():
    call = ToolCall(tool_name="create_task", arguments={"title": "Write report", "priority": "high"})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert result.passed


def test_grade_fails_on_wrong_tool():
    call = ToolCall(tool_name="update_task", arguments={"title": "Write report", "priority": "high"})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert not result.passed
    assert not result.correct_tool


def test_grade_fails_on_wrong_arguments():
    call = ToolCall(tool_name="create_task", arguments={"title": "Wrong title", "priority": "high"})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert not result.passed
    assert result.correct_tool
    assert not result.correct_args


def test_grade_flags_hallucinated_tool_call():
    call = ToolCall(tool_name="delete_everything", arguments={})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert result.hallucinated
    assert not result.passed


def test_grade_flags_no_call():
    call = ToolCall(tool_name=None, arguments={})
    result = grade(TASK, call, catalog_tool_names=CATALOG_NAMES)
    assert result.no_call
    assert not result.passed
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_grader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'toolfit.grade.grader'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/toolfit/grade/grader.py
"""Structural grading: does the model-under-test's tool call match the sampled ground-truth
tuple? Never asks another model's opinion (design doc / source doc S4's whole point)."""

from __future__ import annotations

from dataclasses import dataclass

from toolfit.gen.taskgen import GeneratedTask
from toolfit.run.adapters import ToolCall


@dataclass
class GradeResult:
    correct_tool: bool
    correct_args: bool
    hallucinated: bool  # model called a tool name not in the catalog at all (design doc Failure Modes)
    no_call: bool  # model made no tool call

    @property
    def passed(self) -> bool:
        return self.correct_tool and self.correct_args


def grade(task: GeneratedTask, call: ToolCall, *, catalog_tool_names: list[str]) -> GradeResult:
    if call.tool_name is None:
        return GradeResult(correct_tool=False, correct_args=False, hallucinated=False, no_call=True)
    if call.tool_name not in catalog_tool_names:
        # Failure Mode (design doc): hallucinated/nonexistent tool call — scored as a miss,
        # never a crash, never silently dropped.
        return GradeResult(correct_tool=False, correct_args=False, hallucinated=True, no_call=False)
    correct_tool = call.tool_name == task.tool_name
    correct_args = correct_tool and call.arguments == task.arguments
    return GradeResult(correct_tool=correct_tool, correct_args=correct_args, hallucinated=False, no_call=False)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_grader.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/grade/grader.py tests/test_grader.py
git commit -m "spike: grade/grader does structural comparison against ground truth"
```

---

### Task 6: grade/mutator.py — mutation testing

**Files:**
- Create: `src/toolfit/grade/mutator.py`
- Test: `tests/test_mutator.py`

**Interfaces:**
- Consumes: `ToolCatalog` (Task 1), `GeneratedTask` (Task 3), `ModelAdapter`/`ToolCall` (Task 4), `grade`/`GradeResult` (Task 5).
- Produces: `MutationResult` (fields: `before: GradeResult`, `after: GradeResult`; property `improved: bool`), `patch_description(catalog, *, tool_name, new_description) -> ToolCatalog`, `run_mutation_test(adapter, task, *, original_catalog, tool_name, new_description) -> MutationResult`. Task 11 (e2e/CLI) consumes this. This is the mutation harness — the grader run twice, not a separate mechanism (design doc Next Steps #4).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_mutator.py
from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.mutator import patch_description, run_mutation_test
from toolfit.run.adapters import ToolCall

CATALOG = ToolCatalog(
    tools=[
        Tool(
            name="create_task",
            description="Add a new task.",
            input_schema={"type": "object", "properties": {"title": {"type": "string"}, "priority": {"type": "string"}}},
        ),
        Tool(
            name="update_task",
            description="Add a new task.",
            input_schema={"type": "object", "properties": {"task_id": {"type": "string"}, "title": {"type": "string"}}},
        ),
    ]
)


def test_patch_description_replaces_only_the_named_tool():
    patched = patch_description(CATALOG, tool_name="update_task", new_description="Modify an existing task's title given its task_id.")
    assert patched.get("create_task").description == "Add a new task."
    assert patched.get("update_task").description == "Modify an existing task's title given its task_id."


def test_patch_description_does_not_mutate_the_original_catalog():
    patch_description(CATALOG, tool_name="update_task", new_description="Something else.")
    assert CATALOG.get("update_task").description == "Add a new task."


class _FakeAdapter:
    """Deterministic stand-in for a real model adapter — the mutator's own logic (re-running the
    same task before/after a patch, computing improved) is tested in isolation from real model
    behavior, which the e2e test (Task 11) covers separately with a live model."""

    def __init__(self, before_call: ToolCall, after_call: ToolCall):
        self._calls = [before_call, after_call]

    def call_with_tools(self, *, task_text, tools):
        return self._calls.pop(0)


def test_run_mutation_test_detects_improvement():
    task = GeneratedTask(text="rename task t1 to Buy milk", tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    adapter = _FakeAdapter(
        before_call=ToolCall(tool_name="create_task", arguments={"title": "Buy milk", "priority": "t1"}),  # confused with create_task
        after_call=ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"}),  # correct after the patch
    )
    result = run_mutation_test(
        adapter, task, original_catalog=CATALOG, tool_name="update_task", new_description="Modify an existing task's title given its task_id."
    )
    assert result.improved
    assert not result.before.passed
    assert result.after.passed


def test_run_mutation_test_reports_no_improvement_honestly():
    task = GeneratedTask(text="rename task t1 to Buy milk", tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    adapter = _FakeAdapter(
        before_call=ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"}),  # already correct
        after_call=ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"}),  # still correct, no delta to claim
    )
    result = run_mutation_test(
        adapter, task, original_catalog=CATALOG, tool_name="update_task", new_description="Modify an existing task's title given its task_id."
    )
    assert not result.improved  # was already passing — never suppress this into a false "improved"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_mutator.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'toolfit.grade.mutator'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/toolfit/grade/mutator.py
"""Mutation testing: re-run the SAME sampled task against a catalog whose one tool has a patched
description, and compute the before/after delta. This is grade/grader.py run twice, not a
separate grading mechanism (design doc Next Steps #4)."""

from __future__ import annotations

from dataclasses import dataclass

from toolfit.connect.client import ToolCatalog
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.grader import GradeResult, grade
from toolfit.run.adapters import ModelAdapter


@dataclass
class MutationResult:
    before: GradeResult
    after: GradeResult

    @property
    def improved(self) -> bool:
        return (not self.before.passed) and self.after.passed


def patch_description(catalog: ToolCatalog, *, tool_name: str, new_description: str) -> ToolCatalog:
    """Return a NEW catalog with one tool's description replaced — never mutates the original,
    and never touches the target server's source (design doc Premise 1: protocol-level diff only).
    """
    patched = [
        t.model_copy(update={"description": new_description}) if t.name == tool_name else t
        for t in catalog.tools
    ]
    return ToolCatalog(tools=patched)


def run_mutation_test(
    adapter: ModelAdapter,
    task: GeneratedTask,
    *,
    original_catalog: ToolCatalog,
    tool_name: str,
    new_description: str,
) -> MutationResult:
    before_call = adapter.call_with_tools(task_text=task.text, tools=original_catalog.tools)
    before = grade(task, before_call, catalog_tool_names=original_catalog.names())

    patched_catalog = patch_description(original_catalog, tool_name=tool_name, new_description=new_description)
    after_call = adapter.call_with_tools(task_text=task.text, tools=patched_catalog.tools)
    after = grade(task, after_call, catalog_tool_names=patched_catalog.names())

    return MutationResult(before=before, after=after)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_mutator.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/grade/mutator.py tests/test_mutator.py
git commit -m "spike: grade/mutator computes before/after delta from a description patch"
```

---

### Task 7: fix/fixer.py — proposing and validating a rewrite

**Files:**
- Create: `src/toolfit/fix/fixer.py`
- Test: `tests/test_fixer.py`

**Interfaces:**
- Consumes: nothing structurally (plain strings in, like Task 3).
- Produces: `ProposedFix` (fields: `tool_name: str`, `original_description: str`, `new_description: str`, `rejected: bool`, `rejection_reason: str | None`), `propose_fix(client, *, tool_name, current_description, other_tool_names) -> ProposedFix`. Task 11 (e2e/CLI) consumes this.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_fixer.py
"""Deterministic rejection-rule tests (pure function, no API key needed) plus one eval-style
quality test (Global Constraints: fix/ needs an eval suite) that requires ANTHROPIC_API_KEY."""

import os

import anthropic
import pytest

from toolfit.fix.fixer import _validate, propose_fix


def test_validate_rejects_empty_rewrite():
    result = _validate("update_task", "Add a new task.", "")
    assert result.rejected
    assert result.rejection_reason == "empty rewrite"


def test_validate_rejects_identical_rewrite():
    result = _validate("update_task", "Add a new task.", "Add a new task.")
    assert result.rejected
    assert result.rejection_reason == "identical to original"


def test_validate_rejects_too_short_rewrite():
    result = _validate("update_task", "Add a new task.", "Task.")
    assert result.rejected
    assert result.rejection_reason == "too short to be a real description"


def test_validate_accepts_a_real_rewrite():
    result = _validate("update_task", "Add a new task.", "Modify an existing task's title given its task_id.")
    assert not result.rejected
    assert result.rejection_reason is None


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY")
def test_propose_fix_produces_a_meaningfully_different_description():
    client = anthropic.Anthropic()
    fix = propose_fix(client, tool_name="update_task", current_description="Add a new task.", other_tool_names=["create_task", "list_tasks"])
    assert not fix.rejected
    assert fix.new_description.strip().lower() != "add a new task."
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_fixer.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'toolfit.fix.fixer'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/toolfit/fix/fixer.py
"""Propose a rewritten tool description; reject degenerate rewrites before they're even
re-measured (design doc Failure Mode: "Fix-generation failure")."""

from __future__ import annotations

from dataclasses import dataclass

import anthropic

FIXER_MODEL = "claude-sonnet-5"

_PROMPT_TEMPLATE = """This tool's description is causing an AI assistant to confuse it with a \
similar tool:

Tool name: {tool_name}
Current description: {current_description}
Other tools in the same catalog: {other_tool_names}

Write a replacement description (one sentence) that clearly distinguishes this tool from the \
others, states what it does and what arguments it needs. Reply with just the new description \
text, nothing else."""


@dataclass
class ProposedFix:
    tool_name: str
    original_description: str
    new_description: str
    rejected: bool
    rejection_reason: str | None


def propose_fix(
    client: anthropic.Anthropic, *, tool_name: str, current_description: str, other_tool_names: list[str]
) -> ProposedFix:
    prompt = _PROMPT_TEMPLATE.format(
        tool_name=tool_name,
        current_description=current_description,
        other_tool_names=", ".join(other_tool_names),
    )
    response = client.messages.create(
        model=FIXER_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    new_description = response.content[0].text.strip()
    return _validate(tool_name, current_description, new_description)


def _validate(tool_name: str, current_description: str, new_description: str) -> ProposedFix:
    """Failure Mode (design doc): reject empty, identical, or clearly-unrelated rewrites before
    they're re-measured — same spirit as the noise-threshold rejection for mutation deltas."""
    if not new_description.strip():
        return ProposedFix(tool_name, current_description, new_description, rejected=True, rejection_reason="empty rewrite")
    if new_description.strip() == current_description.strip():
        return ProposedFix(tool_name, current_description, new_description, rejected=True, rejection_reason="identical to original")
    if len(new_description.strip()) < 10:
        return ProposedFix(
            tool_name, current_description, new_description, rejected=True, rejection_reason="too short to be a real description"
        )
    return ProposedFix(tool_name, current_description, new_description, rejected=False, rejection_reason=None)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `ANTHROPIC_API_KEY=<key> uv run pytest tests/test_fixer.py -v`
Expected: PASS (5 passed; 4 pass without a key, the 5th skips)

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/fix/fixer.py tests/test_fixer.py
git commit -m "spike: fix/fixer proposes rewrites and rejects degenerate ones before re-measurement"
```

---

### Task 8: report/render.py — markdown report

**Files:**
- Create: `src/toolfit/report/render.py`
- Test: `tests/test_render.py`

**Interfaces:**
- Consumes: `GeneratedTask` (Task 3), `ToolCall` (Task 4), `MutationResult` (Task 6), `ProposedFix` (Task 7).
- Produces: `render_spike_report(*, task, call, mutation, fix) -> str`. Task 11 (CLI) consumes this.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_render.py
from toolfit.fix.fixer import ProposedFix
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.grader import GradeResult
from toolfit.grade.mutator import MutationResult
from toolfit.report.render import render_spike_report
from toolfit.run.adapters import ToolCall


def test_render_spike_report_includes_task_call_and_mutation_delta():
    task = GeneratedTask(text="rename task t1 to Buy milk", tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    call = ToolCall(tool_name="update_task", arguments={"task_id": "t1", "title": "Buy milk"})
    mutation = MutationResult(
        before=GradeResult(correct_tool=False, correct_args=False, hallucinated=False, no_call=False),
        after=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
    )
    fix = ProposedFix(
        tool_name="update_task",
        original_description="Add a new task.",
        new_description="Modify an existing task's title given its task_id.",
        rejected=False,
        rejection_reason=None,
    )
    report = render_spike_report(task=task, call=call, mutation=mutation, fix=fix)
    assert "rename task t1 to Buy milk" in report
    assert "update_task" in report
    assert "Improved: True" in report
    assert "Modify an existing task's title given its task_id." in report


def test_render_spike_report_handles_no_fix():
    task = GeneratedTask(text="x", tool_name="create_task", arguments={})
    call = ToolCall(tool_name="create_task", arguments={})
    mutation = MutationResult(
        before=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
        after=GradeResult(correct_tool=True, correct_args=True, hallucinated=False, no_call=False),
    )
    report = render_spike_report(task=task, call=call, mutation=mutation, fix=None)
    assert "Proposed fix" not in report
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_render.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'toolfit.report.render'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/toolfit/report/render.py
"""Markdown-only report for the spike (design doc Next Steps #1: "Markdown output only")."""

from __future__ import annotations

from toolfit.fix.fixer import ProposedFix
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.mutator import MutationResult
from toolfit.run.adapters import ToolCall


def render_spike_report(
    *,
    task: GeneratedTask,
    call: ToolCall,
    mutation: MutationResult,
    fix: ProposedFix | None,
) -> str:
    lines = [
        "# toolfit spike report",
        "",
        "## Task",
        f"- Generated request: {task.text!r}",
        f"- Ground truth: `{task.tool_name}({task.arguments})`",
        f"- Model called: `{call.tool_name}({call.arguments})`",
        "",
        "## Mutation test",
        f"- Before: correct_tool={mutation.before.correct_tool}, correct_args={mutation.before.correct_args}, hallucinated={mutation.before.hallucinated}",
        f"- After:  correct_tool={mutation.after.correct_tool}, correct_args={mutation.after.correct_args}, hallucinated={mutation.after.hallucinated}",
        f"- Improved: {mutation.improved}",
    ]
    if fix is not None:
        lines += [
            "",
            "## Proposed fix",
            f"- Tool: {fix.tool_name}",
            f"- Original: {fix.original_description!r}",
            f"- Proposed: {fix.new_description!r}",
            f"- Rejected: {fix.rejected}" + (f" ({fix.rejection_reason})" if fix.rejected else ""),
        ]
    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_render.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/report/render.py tests/test_render.py
git commit -m "spike: report/render produces the markdown spike report"
```

---

### Task 9: run/adapters.py — OpenRouter compatibility check

**Files:**
- Modify: `src/toolfit/run/adapters.py` (append `OpenRouterAdapter`)
- Create: `scripts/openrouter_check.py`
- Test: `tests/test_adapters.py` (append)

**Interfaces:**
- Consumes: `mcp.types.Tool` list, `ToolCall` (both already defined in Task 4).
- Produces: `OpenRouterAdapter(client, model: str)` implementing the same `ModelAdapter` protocol as `AnthropicAdapter`. This validates OpenRouter's tool-call/JSON-strictness behavior before M2 commits to it as a third adapter (design doc Next Steps #1) — it is NOT wired into the main spike report; it's a standalone check script.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_adapters.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_adapters.py -v`
Expected: FAIL — `ImportError: cannot import name 'OpenRouterAdapter'`

- [ ] **Step 3: Append the implementation**

```python
# append to src/toolfit/run/adapters.py
import json


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_adapters.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Write the standalone check script**

```python
# scripts/openrouter_check.py
"""Validates an OpenRouter model's tool-call/JSON-strictness behavior before M2 commits to it
as a third adapter (design doc Next Steps #1, TODO 4).
Run: ANTHROPIC_API_KEY=... OPENROUTER_API_KEY=... uv run python scripts/openrouter_check.py
"""

from __future__ import annotations

import asyncio
import os

import anthropic
import openai

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.gen.schema_sampler import sample_arguments
from toolfit.gen.taskgen import generate_task
from toolfit.run.adapters import OpenRouterAdapter

# Check https://openrouter.ai/models for current tool-calling-capable model IDs — this default
# may drift over time; override via the OPENROUTER_MODEL env var rather than editing this file.
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-5.5")


async def main() -> None:
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)
    target = catalog.get("create_task")
    args = sample_arguments(target.input_schema, seed=1)

    anthropic_client = anthropic.Anthropic()
    task = generate_task(anthropic_client, tool_name="create_task", tool_description=target.description, arguments=args)

    router_client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
    adapter = OpenRouterAdapter(router_client, model=OPENROUTER_MODEL)
    call = adapter.call_with_tools(task_text=task.text, tools=catalog.tools)

    print(f"Task: {task.text!r}")
    print(f"Ground truth: {task.tool_name}({task.arguments})")
    print(f"OpenRouter ({OPENROUTER_MODEL}) called: {call.tool_name}({call.arguments})")
    print()
    print("Record in docs/designs/toolfit-v0-scope.md's Next Steps once run:")
    print("- Did it make a tool call at all, or only text?")
    print("- Did tool_calls[0].function.arguments parse as valid JSON without repair?")
    print("- Did the model name resolve without a 400/404 from OpenRouter?")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 6: Commit**

```bash
git add src/toolfit/run/adapters.py tests/test_adapters.py scripts/openrouter_check.py
git commit -m "spike: add OpenRouter adapter and standalone compatibility check script"
```

---

### Task 10: scripts/circularity_check.py — description-withholding experiment

**Files:**
- Create: `scripts/circularity_check.py`

**Interfaces:**
- Consumes: `fetch_catalog`/`server_params` (Task 1), `sample_arguments` (Task 2), `generate_task` (Task 3).
- Produces: a standalone script, no importable interface — this is an exploratory experiment (design doc "Residual circularity risk"), not TDD-covered code, since its output is a human judgment call, not an assertion.

- [ ] **Step 1: Write the script**

```python
# scripts/circularity_check.py
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
```

- [ ] **Step 2: Run it manually and record the judgment**

Run: `ANTHROPIC_API_KEY=<key> uv run python scripts/circularity_check.py`
Expected: prints both variants; read them and note the judgment call in `docs/designs/toolfit-v0-scope.md`'s "Residual circularity risk" paragraph (default withheld, or keep visible + document the residual risk).

- [ ] **Step 3: Commit**

```bash
git add scripts/circularity_check.py
git commit -m "spike: add the description-withholding circularity experiment"
```

---

### Task 11: End-to-end wiring and proof

**Files:**
- Create: `scripts/run_spike.py`
- Create: `tests/test_e2e_spike.py`

**Interfaces:**
- Consumes: every module from Tasks 1-8.
- Produces: a runnable CLI script that proves the full loop, and the one test that exercises it against the real toy server with a real model.

- [ ] **Step 1: Write the failing e2e test**

```python
# tests/test_e2e_spike.py
"""End-to-end: connect to the real toy server (subprocess), fetch its catalog, run the full
gen -> run -> grade -> mutate loop once against a real model. Requires ANTHROPIC_API_KEY — this
is the test that proves the spike's actual purpose (design doc Premise 5)."""

import os

import anthropic
import pytest

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.gen.schema_sampler import sample_arguments
from toolfit.gen.taskgen import generate_task
from toolfit.grade.mutator import run_mutation_test
from toolfit.run.adapters import AnthropicAdapter

pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY")


@pytest.mark.asyncio
async def test_full_loop_against_the_toy_server():
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)
    assert catalog.names() == ["create_task", "update_task", "list_tasks"]

    target_tool = catalog.get("update_task")
    args = sample_arguments(target_tool.input_schema, seed=1)

    client = anthropic.Anthropic()
    task = generate_task(client, tool_name="update_task", tool_description=target_tool.description, arguments=args)

    adapter = AnthropicAdapter(client)
    result = run_mutation_test(
        adapter,
        task,
        original_catalog=catalog,
        tool_name="update_task",
        new_description="Modify an existing task's title, given its task_id.",
    )
    # Not asserting `improved` as always-true — that's the empirical question this spike exists
    # to answer, not an assumption to bake into the test (design doc: never suppress a result).
    assert result.before is not None
    assert result.after is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_e2e_spike.py -v`
Expected: FAIL if any earlier module is missing; if all Tasks 1-8 are complete, this should already PASS — this step confirms the wiring, not new code.

- [ ] **Step 3: Write the CLI script**

```python
# scripts/run_spike.py
"""CLI entrypoint for the toolfit spike (design doc Next Steps #1).
Run: ANTHROPIC_API_KEY=... uv run python scripts/run_spike.py
"""

from __future__ import annotations

import asyncio

import anthropic

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.fix.fixer import propose_fix
from toolfit.gen.schema_sampler import sample_arguments
from toolfit.gen.taskgen import generate_task
from toolfit.grade.mutator import run_mutation_test
from toolfit.report.render import render_spike_report
from toolfit.run.adapters import AnthropicAdapter


async def main() -> None:
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)

    target = catalog.get("update_task")
    args = sample_arguments(target.input_schema, seed=1)

    anthropic_client = anthropic.Anthropic()
    task = generate_task(anthropic_client, tool_name="update_task", tool_description=target.description, arguments=args)

    adapter = AnthropicAdapter(anthropic_client)
    fix = propose_fix(
        anthropic_client,
        tool_name="update_task",
        current_description=target.description,
        other_tool_names=[t for t in catalog.names() if t != "update_task"],
    )

    new_description = target.description if fix.rejected else fix.new_description
    mutation = run_mutation_test(adapter, task, original_catalog=catalog, tool_name="update_task", new_description=new_description)

    call = adapter.call_with_tools(task_text=task.text, tools=catalog.tools)
    print(render_spike_report(task=task, call=call, mutation=mutation, fix=fix))


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: Run the e2e test to verify it passes**

Run: `ANTHROPIC_API_KEY=<key> uv run pytest tests/test_e2e_spike.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Run the full suite and the CLI script**

Run: `ANTHROPIC_API_KEY=<key> uv run pytest -v`
Expected: all tests pass (some SKIPPED only if `OPENROUTER_API_KEY` is unset — that's fine, OpenRouter is validated by Task 9's standalone script, not the main suite)

Run: `ANTHROPIC_API_KEY=<key> uv run python scripts/run_spike.py`
Expected: prints a full markdown spike report to stdout — this is the artifact that answers the spike's actual question (does the loop produce a clean, believable signal?)

- [ ] **Step 6: Commit**

```bash
git add scripts/run_spike.py tests/test_e2e_spike.py
git commit -m "spike: wire the full loop end-to-end and prove it against the toy server"
```

---

## After This Plan

This plan stops at proving the loop works (Premise 5). It does NOT cover M0-M4 from `docs/designs/toolfit-v0-scope.md` — those get their own plan(s) once the spike's report (Task 11) and the two experiment scripts (Tasks 9-10) produce real findings to act on. Specifically, before writing an M0 plan: read what `run_spike.py`, `circularity_check.py`, and `openrouter_check.py` actually showed, since M0-M1's real JSON Schema handling and M2's OpenRouter adapter scope both depend on what this spike observes.
