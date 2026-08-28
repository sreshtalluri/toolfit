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
