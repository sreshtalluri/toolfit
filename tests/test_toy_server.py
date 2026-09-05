"""Confirms the toy server actually starts over stdio and exposes the expected 5 tools — the
fixture every other test in this plan depends on. create_reminder's schema is the one this M1
plan's schema-sampler hardening (Task 1) is built to actually exercise, not just unit-test
against synthetic dicts."""

import pytest
from mcp import StdioServerParameters

from toolfit.connect.client import fetch_catalog, server_params


def test_server_params_runs_py_scripts_via_uv():
    params = server_params("examples/toy_server.py")
    assert isinstance(params, StdioServerParameters)
    assert (params.command, params.args) == ("uv", ["run", "examples/toy_server.py"])


def test_server_params_passes_http_urls_through():
    assert server_params("https://mcp.example.com/mcp") == "https://mcp.example.com/mcp"


def test_server_params_shell_splits_a_command_line():
    params = server_params("npx -y @modelcontextprotocol/server-github")
    assert isinstance(params, StdioServerParameters)
    assert (params.command, params.args) == ("npx", ["-y", "@modelcontextprotocol/server-github"])


@pytest.mark.asyncio
async def test_fetch_catalog_works_with_an_explicit_command_line():
    catalog = await fetch_catalog(server_params("uv run examples/toy_server.py"))
    assert "create_task" in catalog.names()


@pytest.mark.asyncio
async def test_toy_server_exposes_five_tools_with_two_intentional_bugs():
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)
    assert catalog.names() == ["create_task", "update_task", "list_tasks", "count_tasks", "create_reminder"]
    assert catalog.get("create_task").description == catalog.get("update_task").description == "Add a new task."
    assert catalog.get("list_tasks").description == catalog.get("count_tasks").description == "Get tasks by status."


@pytest.mark.asyncio
async def test_create_reminder_schema_has_real_complexity():
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)
    schema = catalog.get("create_reminder").input_schema
    props = schema["properties"]
    assert props["remind_at"]["type"] == "string"
    assert props["remind_at"]["format"] == "date"
    assert props["notify_channels"]["type"] == "array"
    assert props["notify_channels"]["items"]["type"] == "string"
    assert props["snooze_minutes"]["type"] == "integer"
    assert set(props["priority"]["enum"]) == {"low", "medium", "high"}
    notes_types = {branch["type"] for branch in props["notes"]["anyOf"]}
    assert notes_types == {"string", "null"}
