"""Offline (no API key needed) tests for gen/taskgen.py's pure logic — the parsing half of
check_solvability, and its truncation-safety behavior via a fake client. The eval-style tests
that hit the real model live in tests/test_taskgen_eval.py; this file covers what doesn't need
one, closing the gap flagged in the final spike review (gen/ had no offline coverage, unlike
run/)."""

from types import SimpleNamespace

from toolfit.gen.taskgen import GeneratedTask, _parse_solvability_response, check_solvability


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
