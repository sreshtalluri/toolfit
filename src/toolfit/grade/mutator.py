"""Mutation testing: re-run the SAME sampled task against a catalog whose one tool has a patched
description, and compute the before/after delta. This is grade/grader.py run twice, not a
separate grading mechanism (design doc Next Steps #4)."""

from __future__ import annotations

from dataclasses import dataclass

from toolfit.connect.client import ToolCatalog
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.grader import GradeResult, grade
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
