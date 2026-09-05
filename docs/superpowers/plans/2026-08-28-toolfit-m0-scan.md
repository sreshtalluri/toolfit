# toolfit M0 Implementation Plan (Static `scan`)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a free, zero-model-call `toolfit scan <server_path>` command that catches duplicate/missing/thin tool descriptions via pure static analysis.

**Architecture:** A new `lint/` package holds three pure rule functions over a `ToolCatalog`, aggregated by `run_lint`. `report/render.py` gains a markdown renderer for the findings. `cli.py` gains a `scan` subcommand that connects (dry-run, no model calls), fetches the catalog, runs the rules, and prints the report — reusing the exact connection/error-handling pattern `eval` already has.

**Tech Stack:** Python 3.10+, `typer`, `pytest` + `pytest-asyncio`. No new dependencies — `scan` never touches `anthropic`/`openai`.

**Spec:** `docs/designs/toolfit-v0-scope.md`, section "## M0 Design (added retroactively during M3 planning, 2026-08-28)". Also read "## M1 Design" for `connect/client.py`'s existing interface, which this plan reuses unchanged.

## Global Constraints

- **No model calls, anywhere in this plan.** `scan` must never construct an `anthropic.Anthropic()` or `openai.OpenAI()` client, never need an API key, and must run in well under a second against a real server.
- **Three lint rules only** (`missing_description`, `short_description`, `duplicate_description`) — no broader rule set. A short-description threshold of ~15 characters, applied only to non-empty descriptions.
- **No numeric/letter grade.** `scan`'s output is a findings list with a count, never a score.
- **HTTP transport stays out of scope.** Only `server_params(script_path)` (stdio) exists; do not add HTTP support in this plan.
- **Reuse `connect/client.py` unchanged.** `ToolCatalog`, `server_params`, `fetch_catalog` (in `src/toolfit/connect/client.py`) are already correct for this plan's needs — do not modify that file.
- **Fail loud, never silently wrong.** An unreachable server must produce the exact same clean CLI error `eval` already has (`"Could not connect to server at {server_path!r}: {e}"`, exit code 1, message on stderr) — never a raw traceback.

---

### Task 1: Lint rules (`lint/rules.py`)

**Files:**
- Create: `src/toolfit/lint/__init__.py` (empty — matches the empty `__init__.py` files already in `src/toolfit/grade/`, `src/toolfit/gen/`, `src/toolfit/run/`)
- Create: `src/toolfit/lint/rules.py`
- Test: `tests/test_lint.py`

**Interfaces:**
- Consumes: `ToolCatalog` (from `toolfit.connect.client` — `ToolCatalog(tools: list[Tool])`, where each `Tool` has `.name: str` and `.description: str | None`, from the `mcp.types` package).
- Produces:
  - `LintFinding(rule_id: str, tool_name: str | None, message: str)` — a dataclass. `tool_name` is `None` for catalog-wide findings (currently only `duplicate_description`).
  - `run_lint(catalog: ToolCatalog) -> list[LintFinding]`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_lint.py`:

```python
"""Offline tests for lint/rules.py — pure functions over a hand-built catalog, no I/O, no model
calls (design doc M0 Design)."""

from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.lint.rules import run_lint

_EMPTY_SCHEMA = {"type": "object", "properties": {}}


def _catalog(*tools: Tool) -> ToolCatalog:
    return ToolCatalog(tools=list(tools))


def test_run_lint_flags_a_missing_description():
    catalog = _catalog(Tool(name="create_task", description=None, input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert any(f.rule_id == "missing_description" and f.tool_name == "create_task" for f in findings)


def test_run_lint_flags_a_whitespace_only_description():
    catalog = _catalog(Tool(name="create_task", description="   ", input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert any(f.rule_id == "missing_description" and f.tool_name == "create_task" for f in findings)


def test_run_lint_does_not_flag_a_present_description_as_missing():
    catalog = _catalog(Tool(name="create_task", description="Add a new task to the list.", input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert not any(f.rule_id == "missing_description" for f in findings)


def test_run_lint_flags_a_short_description():
    catalog = _catalog(Tool(name="create_task", description="Adds one.", input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert any(f.rule_id == "short_description" and f.tool_name == "create_task" for f in findings)


def test_run_lint_does_not_flag_a_missing_description_as_also_short():
    # missing_description already covers the empty case — short_description must not double-report it.
    catalog = _catalog(Tool(name="create_task", description=None, input_schema=_EMPTY_SCHEMA))
    findings = run_lint(catalog)
    assert not any(f.rule_id == "short_description" for f in findings)


def test_run_lint_does_not_flag_a_sufficiently_long_description_as_short():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task to the user's list.", input_schema=_EMPTY_SCHEMA)
    )
    findings = run_lint(catalog)
    assert not any(f.rule_id == "short_description" for f in findings)


def test_run_lint_flags_two_tools_sharing_an_identical_description():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task.", input_schema=_EMPTY_SCHEMA),
        Tool(name="update_task", description="Add a new task.", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    duplicate_findings = [f for f in findings if f.rule_id == "duplicate_description"]
    assert len(duplicate_findings) == 1
    assert duplicate_findings[0].tool_name is None
    assert "create_task" in duplicate_findings[0].message
    assert "update_task" in duplicate_findings[0].message


def test_run_lint_flags_duplicates_case_and_whitespace_insensitively():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task.", input_schema=_EMPTY_SCHEMA),
        Tool(name="update_task", description="  ADD A NEW TASK.  ", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    assert len([f for f in findings if f.rule_id == "duplicate_description"]) == 1


def test_run_lint_does_not_flag_a_single_unique_description_as_duplicate():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task to the list.", input_schema=_EMPTY_SCHEMA),
        Tool(name="delete_task", description="Remove an existing task entirely.", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    assert not any(f.rule_id == "duplicate_description" for f in findings)


def test_run_lint_does_not_flag_two_tools_with_missing_descriptions_as_duplicates():
    # Two empty descriptions are not a meaningful "shared text" duplicate — each already gets its
    # own missing_description finding, and grouping empty strings together would be noise.
    catalog = _catalog(
        Tool(name="create_task", description=None, input_schema=_EMPTY_SCHEMA),
        Tool(name="update_task", description=None, input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    assert not any(f.rule_id == "duplicate_description" for f in findings)


def test_run_lint_groups_three_tools_sharing_one_description_into_a_single_finding():
    catalog = _catalog(
        Tool(name="a", description="Do the thing.", input_schema=_EMPTY_SCHEMA),
        Tool(name="b", description="Do the thing.", input_schema=_EMPTY_SCHEMA),
        Tool(name="c", description="Do the thing.", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    duplicate_findings = [f for f in findings if f.rule_id == "duplicate_description"]
    assert len(duplicate_findings) == 1
    assert all(name in duplicate_findings[0].message for name in ("a", "b", "c"))


def test_run_lint_returns_no_findings_for_a_clean_catalog():
    catalog = _catalog(
        Tool(name="create_task", description="Add a new task to the user's list.", input_schema=_EMPTY_SCHEMA),
        Tool(name="delete_task", description="Remove an existing task from the list entirely.", input_schema=_EMPTY_SCHEMA),
    )
    findings = run_lint(catalog)
    assert findings == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_lint.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'toolfit.lint'`

- [ ] **Step 3: Write the implementation**

Create `src/toolfit/lint/__init__.py` (empty file — zero content, matches the other package `__init__.py` files in this codebase).

Create `src/toolfit/lint/rules.py`:

```python
"""Static lint rules over an MCP tool catalog — no model calls, no cost, runs in well under a
second (design doc M0 Design). Each rule is a pure function over ToolCatalog; run_lint aggregates
all three into one findings list for the `scan` CLI command to render.
"""

from __future__ import annotations

from dataclasses import dataclass

from toolfit.connect.client import ToolCatalog

_SHORT_DESCRIPTION_THRESHOLD = 15


@dataclass
class LintFinding:
    rule_id: str
    tool_name: str | None  # None for catalog-wide findings (e.g. duplicate_description)
    message: str


def _missing_description(catalog: ToolCatalog) -> list[LintFinding]:
    findings = []
    for tool in catalog.tools:
        if not (tool.description or "").strip():
            findings.append(
                LintFinding(
                    rule_id="missing_description", tool_name=tool.name, message=f"{tool.name} has no description"
                )
            )
    return findings


def _short_description(catalog: ToolCatalog) -> list[LintFinding]:
    findings = []
    for tool in catalog.tools:
        description = (tool.description or "").strip()
        if description and len(description) < _SHORT_DESCRIPTION_THRESHOLD:
            findings.append(
                LintFinding(
                    rule_id="short_description",
                    tool_name=tool.name,
                    message=f"{tool.name}'s description is only {len(description)} characters: {description!r}",
                )
            )
    return findings


def _duplicate_description(catalog: ToolCatalog) -> list[LintFinding]:
    # Maps a case/whitespace-normalized description to (original description text, tool names
    # sharing it) — the original text (not the normalized key) is what the finding's message
    # shows, so the report reads naturally regardless of the catalog's own casing choices.
    groups: dict[str, tuple[str, list[str]]] = {}
    for tool in catalog.tools:
        description = (tool.description or "").strip()
        if not description:
            continue
        key = description.casefold()
        if key not in groups:
            groups[key] = (description, [])
        groups[key][1].append(tool.name)

    findings = []
    for original_description, tool_names in groups.values():
        if len(tool_names) < 2:
            continue
        findings.append(
            LintFinding(
                rule_id="duplicate_description",
                tool_name=None,
                message=f"{', '.join(sorted(tool_names))} share the identical description {original_description!r}",
            )
        )
    return findings


_RULES = (_missing_description, _short_description, _duplicate_description)


def run_lint(catalog: ToolCatalog) -> list[LintFinding]:
    findings: list[LintFinding] = []
    for rule in _RULES:
        findings.extend(rule(catalog))
    return findings
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_lint.py -v`
Expected: PASS (12 tests)

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/lint/__init__.py src/toolfit/lint/rules.py tests/test_lint.py
git commit -m "feat: add static lint rules for missing, short, and duplicate descriptions"
```

---

### Task 2: Lint report rendering (`report/render.py`)

**Files:**
- Modify: `src/toolfit/report/render.py`
- Test: `tests/test_render.py` (extend)

**Interfaces:**
- Consumes: `LintFinding` (Task 1), `ToolCatalog` (existing, from `toolfit.connect.client`).
- Produces: `render_lint_report(catalog: ToolCatalog, findings: list[LintFinding]) -> str`

- [ ] **Step 1: Write the failing tests**

Add these two imports to the top of `tests/test_render.py`, alongside the existing imports:

```python
from mcp.types import Tool

from toolfit.connect.client import ToolCatalog
from toolfit.lint.rules import LintFinding
```

Then add these two tests to `tests/test_render.py`:

```python
def test_render_lint_report_shows_no_findings_message_for_a_clean_catalog():
    catalog = ToolCatalog(
        tools=[Tool(name="tool_a", description="Does A.", input_schema={"type": "object", "properties": {}})]
    )
    report = render_lint_report(catalog, [])
    assert "No findings across 1 tool(s)." in report


def test_render_lint_report_groups_findings_by_rule():
    catalog = ToolCatalog(
        tools=[
            Tool(name="tool_a", description=None, input_schema={"type": "object", "properties": {}}),
            Tool(name="tool_b", description="Add a new task.", input_schema={"type": "object", "properties": {}}),
            Tool(name="tool_c", description="Add a new task.", input_schema={"type": "object", "properties": {}}),
        ]
    )
    findings = [
        LintFinding(rule_id="missing_description", tool_name="tool_a", message="tool_a has no description"),
        LintFinding(
            rule_id="duplicate_description",
            tool_name=None,
            message="tool_b, tool_c share the identical description 'Add a new task.'",
        ),
    ]

    report = render_lint_report(catalog, findings)

    assert "2 finding(s) across 3 tool(s)." in report
    assert "## duplicate_description" in report
    assert "## missing_description" in report
    assert "tool_a has no description" in report
    assert "tool_b, tool_c share the identical description" in report
```

Also add `render_lint_report` to the existing `from toolfit.report.render import render_confusion_matrix, render_spike_report` import line at the top of `tests/test_render.py` (check the exact current import line and extend it rather than adding a duplicate import statement).

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_render.py -v -k lint_report`
Expected: FAIL with `ImportError: cannot import name 'render_lint_report' from 'toolfit.report.render'`

- [ ] **Step 3: Write the implementation**

In `src/toolfit/report/render.py`, add this function at the end of the file:

```python
def render_lint_report(catalog: ToolCatalog, findings: list[LintFinding]) -> str:
    """Markdown report for `scan` (design doc M0 Design) — a findings list with a count, never a
    numeric/letter grade, matching the credibility-first stance already established for `eval`."""
    lines = ["# toolfit scan report", ""]
    if not findings:
        lines.append(f"No findings across {len(catalog.tools)} tool(s).")
        return "\n".join(lines)

    lines.append(f"{len(findings)} finding(s) across {len(catalog.tools)} tool(s).")

    by_rule: dict[str, list[LintFinding]] = {}
    for finding in findings:
        by_rule.setdefault(finding.rule_id, []).append(finding)

    for rule_id in sorted(by_rule):
        lines += ["", f"## {rule_id}"]
        for finding in by_rule[rule_id]:
            lines.append(f"- {finding.message}")

    return "\n".join(lines)
```

Add these two imports to the top of `src/toolfit/report/render.py`, alongside the existing imports:

```python
from toolfit.connect.client import ToolCatalog
from toolfit.lint.rules import LintFinding
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_render.py -v`
Expected: PASS (all tests in the file)

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/report/render.py tests/test_render.py
git commit -m "feat: render lint findings as a markdown scan report"
```

---

### Task 3: `scan` CLI command

**Files:**
- Modify: `src/toolfit/cli.py`
- Test: `tests/test_cli.py` (extend)
- Create: `tests/test_scan_toy_server.py`

**Interfaces:**
- Consumes: `run_lint` (Task 1), `render_lint_report` (Task 2), existing `fetch_catalog`/`server_params` (unchanged, from `toolfit.connect.client`).
- Produces: `toolfit scan <server_path>` CLI command. No new Python-level interface — this is the final integration point.

- [ ] **Step 1: Write the failing tests**

Add these four tests to `tests/test_cli.py` (below the existing tests):

```python
def test_scan_help_shows_server_path_argument():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "SERVER_PATH" in result.output or "server_path" in result.output


def test_scan_requires_server_path_argument():
    result = runner.invoke(app, ["scan"])
    assert result.exit_code != 0


def test_scan_reports_a_clear_error_for_an_unreachable_server():
    result = runner.invoke(app, ["scan", "/nonexistent/path/to/server.py"])
    assert result.exit_code != 0
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert "Could not connect to server" in result.output
    assert "/nonexistent/path/to/server.py" in result.output


def test_eval_still_requires_explicit_subcommand_name_alongside_scan():
    # Regression guard for the Typer single-command-collapse quirk this file already hit once
    # (see this file's module docstring): now that TWO commands are registered (eval, scan),
    # `["eval", ...]` must still work as an explicit subcommand name.
    result = runner.invoke(app, ["eval", "--help"])
    assert result.exit_code == 0
    assert "SERVER_PATH" in result.output or "server_path" in result.output
```

Create `tests/test_scan_toy_server.py`:

```python
"""Real, ungated integration test for `scan` against examples/toy_server.py. `scan` makes no
model calls, so — unlike eval's tests — this needs no API key and runs in every test invocation,
proving `run_lint` catches the toy server's two real duplicate-description pairs for real."""

import pytest

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.lint.rules import run_lint


@pytest.mark.asyncio
async def test_scan_flags_the_toy_servers_two_real_duplicate_description_pairs():
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)

    findings = run_lint(catalog)
    duplicate_findings = [f for f in findings if f.rule_id == "duplicate_description"]

    assert len(duplicate_findings) == 2
    messages = " ".join(f.message for f in duplicate_findings)
    assert "create_task" in messages and "update_task" in messages
    assert "list_tasks" in messages and "count_tasks" in messages
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli.py -v -k scan`
Expected: FAIL — no `scan` command registered, so `runner.invoke(app, ["scan", ...])` exits non-zero with a "No such command" error rather than the expected behavior.

Run: `uv run pytest tests/test_scan_toy_server.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'toolfit.lint'` if Task 1 somehow isn't merged yet — but since Tasks 1 and 2 are already complete at this point in the plan, expect instead a pass-through failure only if something in Tasks 1/2 is broken. If Tasks 1 and 2 are correctly in place, this test may already pass before you write any Task 3 code (it only depends on `toolfit.lint.rules.run_lint`, not on the CLI) — that's fine, it's still worth running now to confirm the toy server itself produces the expected findings before you wire the CLI around it.

- [ ] **Step 3: Write the implementation**

In `src/toolfit/cli.py`, add these two imports alongside the existing ones:

```python
from toolfit.lint.rules import run_lint
from toolfit.report.render import render_confusion_matrix, render_lint_report, render_mutation_results
```

(This replaces the existing `from toolfit.report.render import render_confusion_matrix, render_mutation_results` line — add `render_lint_report` into that same import rather than a separate import statement.)

Add the `scan` command and its runner function, placed after the existing `eval` command and before `_parse_mutation`:

```python
@app.command()
def scan(
    server_path: str = typer.Argument(..., help="Path to a local stdio MCP server script."),
) -> None:
    """Run free, static lint checks against the given MCP server's tool catalog. Makes no model
    calls and needs no API key."""
    asyncio.run(_run_scan(server_path))


async def _run_scan(server_path: str) -> None:
    params = server_params(server_path)
    try:
        catalog = await fetch_catalog(params)
    except Exception as e:
        # Same Failure Modes handling as _run_eval (design doc, docs/designs/toolfit-v0-scope.md:102-104).
        typer.echo(f"Could not connect to server at {server_path!r}: {e}", err=True)
        raise typer.Exit(code=1)

    findings = run_lint(catalog)
    print(render_lint_report(catalog, findings))
```

Now verify the existing `@app.callback()`'s docstring claim empirically — it says to "remove once a second command (scan/fix/report) exists — that's the point Typer stops collapsing on its own." Run the full `tests/test_cli.py` suite with the callback still in place first (it should pass, since it hasn't changed). Then, as a separate experiment, comment out the `@app.callback()` decorator and its `_callback` function entirely, and re-run `tests/test_cli.py`. If all tests still pass with the callback removed, delete it permanently and update the module docstring's second sentence (currently "Only the `eval` subcommand exists...") to reflect that `scan` now exists too and that the callback was removed once verified unnecessary. If any test fails with the callback removed, put the callback back exactly as it was, and instead update its docstring to say it was empirically re-verified as still necessary now that a second command exists (remove the "remove once a second command exists" sentence, since that condition is now met and the callback is still needed).

Either way, update the module-level docstring at the top of `cli.py` (currently starting `"""Typer CLI: \`toolfit eval <server_path>\`..."`) to mention that `scan` now exists as a real command (not "come later" per M0's static lint anymore), keeping the rest of the docstring's content about `--mutate` and the fix loop unchanged.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cli.py tests/test_scan_toy_server.py -v`
Expected: PASS (all tests, including all pre-existing `eval` tests)

Run: `uv run pytest -q` (full suite)
Expected: PASS, with the same skip count as before this task (this task adds no API-key-gated tests) and more passing tests than before.

- [ ] **Step 5: Commit**

```bash
git add src/toolfit/cli.py tests/test_cli.py tests/test_scan_toy_server.py
git commit -m "feat: add toolfit scan CLI command for free, static lint checks"
```

---

## Final Verification

After all 3 tasks are complete:

```bash
uv run pytest -q
```

Expected: every existing test still passes, every new M0 test passes, zero skips added (scan needs no API key at all), zero failures.
