"""Offline tests for report/badge.py — hand-built ConfusionMatrix/MutationTrialResult fixtures,
no I/O, no model calls (design doc M3a Design §2)."""

from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.confusion import ConfusionMatrix, TrialRecord
from toolfit.grade.mutator import MutationTrialResult
from toolfit.report.badge import render_badge


def _matrix_with_trials() -> ConfusionMatrix:
    matrix = ConfusionMatrix()
    matrix.model = "claude-sonnet-5"
    matrix.generator_model = "claude-sonnet-5"
    matrix.seeds = 5
    matrix.trials_by_tool = {
        "tool_a": [
            TrialRecord(task=GeneratedTask(text="do a", tool_name="tool_a", arguments={}), passed=True),
            TrialRecord(task=GeneratedTask(text="do a again", tool_name="tool_a", arguments={}), passed=False),
        ],
        "tool_b": [
            TrialRecord(task=GeneratedTask(text="do b", tool_name="tool_b", arguments={}), passed=True),
        ],
    }
    return matrix


def test_render_badge_shows_overall_pass_rate_without_a_mutation_result():
    matrix = _matrix_with_trials()
    svg = render_badge(matrix)
    assert "toolfit: 67%" in svg  # 2/3 trials passed overall


def test_render_badge_shows_a_before_after_delta_with_a_mutation_result():
    matrix = _matrix_with_trials()
    mutation_result = MutationTrialResult(
        tool_name="tool_a",
        new_description="Better description.",
        before_passes=[False, False],
        after_passes=[True, True],
        p_value=0.01,
        significant=True,
    )
    svg = render_badge(matrix, mutation_result)
    assert "toolfit: 0% → 100%" in svg
    assert 'fill="#4c1"' in svg  # coloured by the after-rate


def test_render_badge_colour_tracks_pass_rate():
    matrix = _matrix_with_trials()  # 2/3 = 67% -> red
    assert 'fill="#e05d44"' in render_badge(matrix)
    for trial in matrix.trials_by_tool["tool_a"]:
        trial.passed = True
    for trial in matrix.trials_by_tool["tool_b"]:
        trial.passed = True
    assert 'fill="#4c1"' in render_badge(matrix)


def test_render_badge_embeds_model_and_seed_metadata():
    matrix = _matrix_with_trials()
    svg = render_badge(matrix)
    assert "model=claude-sonnet-5" in svg
    assert "generator=claude-sonnet-5" in svg
    assert "seeds=5" in svg


def test_render_badge_embeds_a_deterministic_task_suite_hash():
    matrix = _matrix_with_trials()
    svg1 = render_badge(matrix)
    svg2 = render_badge(matrix)
    assert "task_suite=" in svg1
    hash1 = svg1.split("task_suite=")[1].split("<")[0].strip()
    hash2 = svg2.split("task_suite=")[1].split("<")[0].strip()
    assert hash1 == hash2
    assert len(hash1) == 8


def test_render_badge_produces_well_formed_svg():
    matrix = _matrix_with_trials()
    svg = render_badge(matrix)
    assert svg.startswith("<svg")
    assert svg.strip().endswith("</svg>")


def test_render_badge_returns_zero_percent_for_an_empty_matrix():
    matrix = ConfusionMatrix()
    matrix.model = "claude-sonnet-5"
    matrix.generator_model = "claude-sonnet-5"
    matrix.seeds = 5
    svg = render_badge(matrix)
    assert "toolfit: 0%" in svg


def test_render_badge_escapes_xml_special_characters_in_model_name():
    matrix = _matrix_with_trials()
    matrix.model = "vendor/<model> & co"
    svg = render_badge(matrix)
    assert "<model>" not in svg
    assert "&lt;model&gt; &amp; co" in svg
