"""End-to-end: build a real confusion matrix against the toy server, then run a paired mutation
trial reusing its own tasks — the M2 pipeline's actual purpose (design doc M2 Design). Requires
ANTHROPIC_API_KEY. Reuses examples/toy_server.py's existing create_task/update_task ambiguity
(identical "Add a new task." descriptions) as the mutation target, same as the M1 spike found."""

import os

import anthropic
import pytest

from toolfit.connect.client import fetch_catalog, server_params
from toolfit.grade.confusion import build_confusion_matrix
from toolfit.grade.mutator import run_mutation_trials
from toolfit.grade.significance import bonferroni_correct
from toolfit.report.render import render_confusion_matrix, render_mutation_results
from toolfit.run.adapters import AnthropicAdapter

pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="requires ANTHROPIC_API_KEY")


@pytest.mark.asyncio
async def test_full_m2_pipeline_against_the_toy_server():
    params = server_params("examples/toy_server.py")
    catalog = await fetch_catalog(params)

    client = anthropic.Anthropic()
    adapter = AnthropicAdapter(client)

    matrix = build_confusion_matrix(catalog, adapter, client, seeds=3)
    report = render_confusion_matrix(matrix)
    assert "## Pass Rates" in report
    assert "update_task" in matrix.trials_by_tool

    result = run_mutation_trials(
        matrix,
        catalog,
        adapter,
        tool_name="update_task",
        new_description="Modify an existing task's title, given its task_id.",
    )
    # Not asserting `result.significant` as always-true — that's the empirical question this
    # pipeline exists to answer, not an assumption to bake into the test (design doc: never
    # suppress a result). We only assert the pipeline produced a well-formed, usable result.
    assert len(result.before_passes) == 3
    assert len(result.after_passes) == 3
    assert 0.0 <= result.p_value <= 1.0

    significances = bonferroni_correct([result.p_value])
    result.significant = significances[0]
    mutation_report = render_mutation_results([result])
    assert "update_task" in mutation_report
    assert "Verdict (Bonferroni-corrected):" in mutation_report
