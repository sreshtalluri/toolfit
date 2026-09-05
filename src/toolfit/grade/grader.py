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

from dataclasses import dataclass, field
from datetime import datetime

from toolfit.gen.taskgen import GeneratedTask
from toolfit.run.adapters import ToolCall


@dataclass
class GradeResult:
    correct_tool: bool
    correct_args: bool
    hallucinated: bool  # model called a tool name not in the catalog at all (design doc Failure Modes)
    no_call: bool  # model made no tool call
    steps_to_correct: int | None = None  # 1-based index of the passing call in a multi-step trial
    preceding: list[str] = field(default_factory=list)  # tools called before the passing call

    @property
    def passed(self) -> bool:
        return self.correct_tool and self.correct_args

    @property
    def via_precondition(self) -> bool:
        return self.passed and bool(self.preceding)


_DATE_ONLY_FORMATS = ("%Y-%m-%d", "%m/%d/%Y")
_DATETIME_FORMATS = ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ")


def _try_parse_date(value: str) -> str | None:
    # Date-only and datetime formats are kept in separate passes, on purpose: collapsing a
    # datetime input down to `.date().isoformat()` (as a single shared loop used to do) discards
    # the time component, so two arguments on the same date but different times (14:00 vs. 09:30)
    # would canonicalize to the identical string and register as a false pass. Only genuinely
    # date-only input collapses to a bare date; datetime input canonicalizes to the full ISO
    # datetime instead.
    for fmt in _DATE_ONLY_FORMATS:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt).isoformat()
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
    # A sampled `None` (nullable optional field) and an omitted key mean the same thing to the
    # server; the model-under-test almost always omits rather than sending an explicit null.
    return {k: _canonicalize(v) for k, v in arguments.items() if v is not None}


def grade(task: GeneratedTask, call: ToolCall, *, catalog_tool_names: list[str]) -> GradeResult:
    return grade_sequence(task, [call], catalog_tool_names=catalog_tool_names)


def grade_sequence(task: GeneratedTask, calls: list[ToolCall], *, catalog_tool_names: list[str]) -> GradeResult:
    """Multi-step grading (design doc M5): the trial passes if the intended tool is called with
    matching arguments *anywhere* in the sequence; the tools called before that are recorded as
    the precondition path. With a single call this is exactly the 0.1.x rule."""
    named = [c for c in calls if c.tool_name is not None]
    if not named:
        return GradeResult(correct_tool=False, correct_args=False, hallucinated=False, no_call=True)
    expected = _canonicalize_args(task.arguments)
    for i, call in enumerate(named):
        if call.tool_name == task.tool_name and _canonicalize_args(call.arguments) == expected:
            return GradeResult(
                correct_tool=True,
                correct_args=True,
                hallucinated=False,
                no_call=False,
                steps_to_correct=i + 1,
                preceding=[c.tool_name for c in named[:i] if c.tool_name is not None],
            )
    correct_tool = any(c.tool_name == task.tool_name for c in named)
    # Failure Mode (design doc): a hallucinated/nonexistent tool name is scored as a miss, never
    # a crash, never silently dropped. Attributed to the first call, which is what the matrix shows.
    hallucinated = named[0].tool_name not in catalog_tool_names
    return GradeResult(correct_tool=correct_tool, correct_args=False, hallucinated=hallucinated, no_call=False)
