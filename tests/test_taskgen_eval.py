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
