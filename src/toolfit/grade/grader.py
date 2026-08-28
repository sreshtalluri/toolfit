"""Structural grading: does the model-under-test's tool call match the sampled ground-truth
tuple? Never asks another model's opinion (design doc / source doc S4's whole point).

M1 adds canonicalization (design doc M1 Design §3) so semantically-equal answers don't register
as false failures: dates/timestamps normalize to a common representation, arrays compare as
order-independent, and strings case/whitespace-fold. This is a real simplification — grade() has
no schema access to know when order or case is semantically load-bearing for a *specific*
argument — applied uniformly and documented here rather than silently assumed. Explicitly NOT
doing semantic synonym matching (e.g. "urgent" ≈ "high"): that needs an LLM judge, which would
contradict the project's core credibility argument.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

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


_DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ")


def _try_parse_date(value: str) -> str | None:
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _canonicalize(value: object) -> object:
    if isinstance(value, str):
        parsed_date = _try_parse_date(value)
        if parsed_date is not None:
            return parsed_date
        return value.strip().casefold()
    if isinstance(value, list):
        canonicalized_items = [_canonicalize(v) for v in value]
        return sorted(canonicalized_items, key=repr)
    return value


def _canonicalize_args(arguments: dict) -> dict:
    return {k: _canonicalize(v) for k, v in arguments.items()}


def grade(task: GeneratedTask, call: ToolCall, *, catalog_tool_names: list[str]) -> GradeResult:
    if call.tool_name is None:
        return GradeResult(correct_tool=False, correct_args=False, hallucinated=False, no_call=True)
    if call.tool_name not in catalog_tool_names:
        # Failure Mode (design doc): hallucinated/nonexistent tool call — scored as a miss,
        # never a crash, never silently dropped.
        return GradeResult(correct_tool=False, correct_args=False, hallucinated=True, no_call=False)
    correct_tool = call.tool_name == task.tool_name
    correct_args = correct_tool and _canonicalize_args(call.arguments) == _canonicalize_args(task.arguments)
    return GradeResult(correct_tool=correct_tool, correct_args=correct_args, hallucinated=False, no_call=False)
