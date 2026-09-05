"""Eval suite for gen/taskgen.py. The risk here is OUTPUT QUALITY (a generated task that leaks
the tool name, or is unrelated to the sampled arguments), not "did it return a string" — plain
unit tests can't catch that, so this calls the real generator model."""

import os

import anthropic
import pytest

from toolfit.gen.taskgen import GeneratedTask, check_no_leakage, check_solvability, generate_task

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


def test_flags_the_real_ambiguous_task_the_spike_actually_produced(client):
    # Grounded in a real spike run (2026-08-27): the generator produced this exact sentence for
    # update_task({"task_id": "t1", "title": "Book dentist appointment"}) — it reads as a
    # create_task request, and the model-under-test made no tool call at all for it, twice.
    task = GeneratedTask(
        text='Create a new task with ID t1 titled "Book dentist appointment."',
        tool_name="update_task",
        arguments={"task_id": "t1", "title": "Book dentist appointment"},
    )
    result = check_solvability(
        client,
        task,
        catalog_descriptions={
            "create_task": "Add a new task.",
            "update_task": "Add a new task.",
            "list_tasks": "List all tasks, optionally filtered by status (open, done).",
        },
    )
    assert result.solvable is False


def test_passes_a_clearly_solvable_task(client):
    task = GeneratedTask(
        text="Show me all my open tasks.",
        tool_name="list_tasks",
        arguments={"status": "open"},
    )
    result = check_solvability(
        client,
        task,
        catalog_descriptions={
            "create_task": "Add a new task.",
            "update_task": (
                "Modify an existing task's fields (e.g., status, title, due date) by specifying "
                "its task ID and the values to change, rather than creating a new one."
            ),
            "list_tasks": "List all tasks, optionally filtered by status (open, done).",
        },
    )
    assert result.solvable is True


def test_generated_task_for_identifier_shaped_args_uses_modify_language(client):
    # Grounded in the spike's real finding: with a deliberately vague, copy-pasted description,
    # the generator defaulted to "create"/"add" phrasing for update-shaped arguments. This test
    # exercises the fix from Task 3 of the M1 plan.
    task = generate_task(
        client,
        tool_name="update_task",
        tool_description="Add a new task.",
        arguments={"task_id": "t1", "title": "Book dentist appointment"},
    )
    lowered = task.text.lower()
    assert not lowered.startswith("create")
    assert "create a new" not in lowered
