"""Structural grading: does the model-under-test's tool call match the sampled ground-truth
tuple? Never asks another model's opinion (design doc / source doc S4's whole point)."""

from __future__ import annotations

from dataclasses import dataclass

from toolfit.gen.taskgen import GeneratedTask
from toolfit.run.adapters import ToolCall


@dataclass
class GradeResult:
    correct_tool: bool
    correct_args: bool
    hallucinated: bool  # model called a tool name not in the catalog at all (design doc Failure Modes)
    no_call: bool  # model made no tool call

    @property
    def passed(self) -> bool:
        return self.correct_tool and self.correct_args


def grade(task: GeneratedTask, call: ToolCall, *, catalog_tool_names: list[str]) -> GradeResult:
    if call.tool_name is None:
        return GradeResult(correct_tool=False, correct_args=False, hallucinated=False, no_call=True)
    if call.tool_name not in catalog_tool_names:
        # Failure Mode (design doc): hallucinated/nonexistent tool call — scored as a miss,
        # never a crash, never silently dropped.
        return GradeResult(correct_tool=False, correct_args=False, hallucinated=True, no_call=False)
    correct_tool = call.tool_name == task.tool_name
    correct_args = correct_tool and call.arguments == task.arguments
    return GradeResult(correct_tool=correct_tool, correct_args=correct_args, hallucinated=False, no_call=False)
