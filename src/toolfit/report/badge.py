"""Locally-generated static SVG badge (design doc M3a Design §2) — no hosted badge service, the
user runs `eval --badge` and commits the SVG themselves (Constraints: no web UI). Every badge
embeds enough metadata (model, generator model, seeds, task-suite hash) that the bare percentage
can never be read without its benchmark identity — the integrity requirement from the design
doc's "What Makes This Cool" section.
"""

from __future__ import annotations

import hashlib

from toolfit.grade.confusion import ConfusionMatrix
from toolfit.grade.mutator import MutationTrialResult


def _task_suite_hash(matrix: ConfusionMatrix) -> str:
    pairs = sorted(
        (tool_name, trial.task.text) for tool_name, trials in matrix.trials_by_tool.items() for trial in trials
    )
    digest = hashlib.sha256(repr(pairs).encode("utf-8")).hexdigest()
    return digest[:8]


def _overall_pass_rate(matrix: ConfusionMatrix) -> float:
    all_trials = [trial for trials in matrix.trials_by_tool.values() for trial in trials]
    if not all_trials:
        return 0.0
    return sum(1 for t in all_trials if t.passed) / len(all_trials)


def render_badge(matrix: ConfusionMatrix, mutation_result: MutationTrialResult | None = None) -> str:
    if mutation_result is None:
        rate = _overall_pass_rate(matrix)
        label_text = f"toolfit: {rate:.0%}"
    else:
        before_rate = sum(mutation_result.before_passes) / len(mutation_result.before_passes)
        after_rate = sum(mutation_result.after_passes) / len(mutation_result.after_passes)
        label_text = f"toolfit: {before_rate:.0%} → {after_rate:.0%}"

    task_suite_hash = _task_suite_hash(matrix)
    metadata = (
        f"model={matrix.model} generator={matrix.generator_model} seeds={matrix.seeds} "
        f"task_suite={task_suite_hash}"
    )

    width = 20 + len(label_text) * 7
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" aria-label="{label_text}">\n'
        f"  <title>{label_text}</title>\n"
        f"  <desc>{metadata}</desc>\n"
        f'  <rect width="{width}" height="20" fill="#4c1" rx="3"/>\n'
        f'  <text x="10" y="14" font-family="sans-serif" font-size="11" fill="#fff">{label_text}</text>\n'
        "</svg>"
    )
