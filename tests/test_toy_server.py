"""Confirms the toy server actually starts over stdio and exposes the expected 4 tools with two
intentional description bugs — the fixture every other test in this plan depends on."""

import pytest

from toolfit.connect.client import fetch_catalog, server_params


@pytest.mark.asyncio
async def test_toy_server_exposes_four_tools_with_two_intentional_bugs():
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)
    assert catalog.names() == ["create_task", "update_task", "list_tasks", "count_tasks"]
    assert catalog.get("create_task").description == catalog.get("update_task").description == "Add a new task."
    assert catalog.get("list_tasks").description == catalog.get("count_tasks").description == "Get tasks by status."
