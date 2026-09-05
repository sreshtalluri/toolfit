"""Mutation testing: re-run the SAME sampled task against a catalog whose one tool has a patched
description, and compute the before/after delta. This is grade/grader.py run twice, not a
separate grading mechanism (design doc Next Steps #4)."""

from __future__ import annotations

from dataclasses import dataclass

from toolfit.connect.client import ToolCatalog
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.confusion import ConfusionMatrix
from toolfit.grade.grader import GradeResult, grade
from toolfit.grade.significance import paired_exact_pvalue
from toolfit.run.adapters import ModelAdapter


@dataclass
class MutationResult:
    before: GradeResult
    after: GradeResult

    @property
    def improved(self) -> bool:
        return (not self.before.passed) and self.after.passed


def patch_description(catalog: ToolCatalog, *, tool_name: str, new_description: str) -> ToolCatalog:
    """Return a NEW catalog with one tool's description replaced — never mutates the original,
    and never touches the target server's source (design doc Premise 1: protocol-level diff only).
    """
    patched = [
        t.model_copy(update={"description": new_description}) if t.name == tool_name else t
        for t in catalog.tools
    ]
    return ToolCatalog(tools=patched)


def run_mutation_test(
    adapter: ModelAdapter,
    task: GeneratedTask,
    *,
    original_catalog: ToolCatalog,
    tool_name: str,
    new_description: str,
) -> MutationResult:
    before_call = adapter.call_with_tools(task_text=task.text, tools=original_catalog.tools)
    before = grade(task, before_call, catalog_tool_names=original_catalog.names())

    patched_catalog = patch_description(original_catalog, tool_name=tool_name, new_description=new_description)
    after_call = adapter.call_with_tools(task_text=task.text, tools=patched_catalog.tools)
    after = grade(task, after_call, catalog_tool_names=patched_catalog.names())

    return MutationResult(before=before, after=after)


@dataclass
class MutationTrialResult:
    tool_name: str
    new_description: str
    before_passes: list[bool]
    after_passes: list[bool]
    p_value: float
    significant: bool = False  # set by the caller after Bonferroni-correcting across every
    # mutation tested together in one CLI invocation — this dataclass doesn't correct itself,
    # since correction depends on how many other mutations ran alongside it (design doc M2 §1).


def run_mutation_trials(
    matrix: ConfusionMatrix,
    catalog: ToolCatalog,
    adapter: ModelAdapter,
    *,
    tool_name: str,
    new_description: str,
) -> MutationTrialResult:
    """Paired mutation trial (design doc M2 Design §3): reuses the EXACT tasks the confusion
    matrix already ran for `tool_name` as 'before' — no repeat API calls, and a guarantee that
    'before' here is identical to what the base eval report already measured. Only 'after' (the
    patched-description run) makes new calls. Raises KeyError if `tool_name` has no trials in
    `matrix` (e.g. excluded for a schema warning, or never in the catalog) — callers validate this
    against the catalog before dispatching any mutation, per the CLI's error-handling contract.
    """
    trials = matrix.trials_by_tool[tool_name]
    before_passes = [t.passed for t in trials]

    patched_catalog = patch_description(catalog, tool_name=tool_name, new_description=new_description)
    after_passes = []
    for trial in trials:
        call = adapter.call_with_tools(task_text=trial.task.text, tools=patched_catalog.tools)
        result = grade(trial.task, call, catalog_tool_names=patched_catalog.names())
        after_passes.append(result.passed)

    p_value = paired_exact_pvalue(before_passes, after_passes)
    return MutationTrialResult(
        tool_name=tool_name,
        new_description=new_description,
        before_passes=before_passes,
        after_passes=after_passes,
        p_value=p_value,
    )
