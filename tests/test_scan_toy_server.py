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


@pytest.mark.asyncio
async def test_scan_flags_the_crm_examples_four_planted_problems():
    # examples/crm_server.py is the "production-shaped" example AGENTS.md walks through; keep its
    # planted findings stable so the manual's sample output stays true.
    catalog = await fetch_catalog(server_params("examples/crm_server.py"))
    findings = run_lint(catalog)
    assert sorted((f.rule_id, f.tool_name or "") for f in findings) == [
        ("deprecated_tool", "get_contact"),
        ("duplicate_description", ""),
        ("short_description", "list_contacts"),
        ("short_description", "search_contacts"),
    ]
    assert len(catalog.tools) == 8
