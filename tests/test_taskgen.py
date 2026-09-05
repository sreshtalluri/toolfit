"""Offline (no API key needed) tests for gen/taskgen.py's pure logic — the parsing half of
check_solvability, and its truncation-safety behavior via a fake client. The eval-style tests
that hit the real model live in tests/test_taskgen_eval.py; this file covers what doesn't need
one, closing the gap flagged in the final spike review (gen/ had no offline coverage, unlike
run/)."""

from types import SimpleNamespace

import anthropic
import pytest

from toolfit.gen.taskgen import (
    GeneratedTask,
    _has_identifier_argument,
    _parse_solvability_response,
    check_no_leakage,
    check_solvability,
    generate_task,
)


def test_check_no_leakage_matches_whole_words_only():
    task = GeneratedTask(text="Search for open issues and list them", tool_name="find", arguments={})
    assert check_no_leakage(task, catalog_tool_names=["search_issues", "list_issues"])
    assert not check_no_leakage(task, catalog_tool_names=["search"])


def test_parses_a_solvable_response():
    solvable, reason = _parse_solvability_response(
        "SOLVABLE: The request clearly asks to update an existing task."
    )
    assert solvable is True
    assert reason == "The request clearly asks to update an existing task."


def test_parses_an_ambiguous_response():
    solvable, reason = _parse_solvability_response(
        "AMBIGUOUS: Could be create_task or update_task, both plausible."
    )
    assert solvable is False
    assert reason == "Could be create_task or update_task, both plausible."


def test_parses_case_insensitively():
    solvable, _ = _parse_solvability_response("solvable: fine")
    assert solvable is True


def test_unparseable_response_fails_safe_as_ambiguous():
    solvable, reason = _parse_solvability_response("I'm not sure what to say here")
    assert solvable is False
    assert "I'm not sure what to say here" in reason


def test_check_solvability_warns_on_truncation(capsys):
    fake_response = SimpleNamespace(
        stop_reason="max_tokens",
        content=[SimpleNamespace(type="text", text="SOLVABLE: looks fine")],
    )
    fake_client = SimpleNamespace(
        messages=SimpleNamespace(create=lambda **kwargs: fake_response)
    )
    task = GeneratedTask(text="do the thing", tool_name="update_task", arguments={})

    check_solvability(fake_client, task, catalog_descriptions={"update_task": "Modify a task."})

    assert "truncated" in capsys.readouterr().err.lower()


def test_has_identifier_argument_detects_an_id_shaped_field():
    assert _has_identifier_argument({"task_id": "t1", "title": "X"})
    assert _has_identifier_argument({"id": "u1"})


def test_has_identifier_argument_false_when_no_id_shaped_field():
    assert not _has_identifier_argument({"title": "X", "priority": "high"})


def test_has_identifier_argument_false_for_a_creation_tool_with_a_foreign_key():
    assert not _has_identifier_argument({"task_id": "t1", "remind_at": "2026-01-01"}, tool_name="create_reminder")


def test_has_identifier_argument_still_true_for_a_genuine_update_tool():
    assert _has_identifier_argument({"task_id": "t1", "title": "X"}, tool_name="update_task")


def test_creation_verb_skip_matches_whole_words_not_prefixes():
    # "address_book_update" starts with "add" and "newsletter_unsubscribe" starts with "new", but
    # both are genuine modify-shaped tools that must KEEP the identifier guidance. A prefix match
    # on the short creation verbs would wrongly suppress it.
    args = {"id": "x1", "title": "X"}
    assert _has_identifier_argument(args, tool_name="address_book_update")
    assert _has_identifier_argument(args, tool_name="newsletter_unsubscribe")
    assert _has_identifier_argument(args, tool_name="insertion_point_move")


def test_creation_verb_skip_handles_camel_case_and_upper_case_tool_names():
    args = {"task_id": "t1", "remind_at": "2026-01-01"}
    assert not _has_identifier_argument(args, tool_name="createReminder")
    assert not _has_identifier_argument(args, tool_name="CREATE_REMINDER")
    assert not _has_identifier_argument(args, tool_name="schedule-reminder")


def test_generate_task_retries_the_generator_call_on_a_rate_limit(monkeypatch):
    import httpx2

    monkeypatch.setattr("toolfit.run.adapters.time.sleep", lambda s: None)
    attempts = {"n": 0}
    ok = SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="Do the thing.")])

    def create(**kwargs):
        attempts["n"] += 1
        if attempts["n"] == 1:
            resp = httpx2.Response(429, request=httpx2.Request("POST", "https://api.anthropic.com"))
            raise anthropic.RateLimitError("rate limited", response=resp, body=None)
        return ok

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    task = generate_task(client, tool_name="update_task", tool_description="Modify.", arguments={})
    assert task.text == "Do the thing."
    assert attempts["n"] == 2


def _client_returning_no_text_block():
    fake_response = SimpleNamespace(stop_reason="max_tokens", content=[SimpleNamespace(type="thinking")])
    return SimpleNamespace(messages=SimpleNamespace(create=lambda **kwargs: fake_response))


def test_generate_task_raises_clearly_when_response_has_no_text_block():
    with pytest.raises(RuntimeError, match="no text.*max_tokens"):
        generate_task(
            _client_returning_no_text_block(), tool_name="update_task", tool_description="Modify.", arguments={}
        )


def test_check_solvability_with_no_text_block_fails_safe_as_ambiguous():
    task = GeneratedTask(text="do the thing", tool_name="update_task", arguments={})
    result = check_solvability(
        _client_returning_no_text_block(), task, catalog_descriptions={"update_task": "Modify a task."}
    )
    assert result.solvable is False
