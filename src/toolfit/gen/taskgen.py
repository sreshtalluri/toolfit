"""Inverted task generation (design doc "The Core Technique").

Samples a ground-truth (tool, arguments) tuple FIRST (schema_sampler.py), then asks a generator
model to write the natural-language request that leads to exactly those arguments, without
naming the tool. Grading (grade/grader.py) compares the model-under-test's actual call against
this sampled tuple — never against the generator's opinion.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

import anthropic

GENERATOR_MODEL = "claude-sonnet-5"

_PROMPT_TEMPLATE = """A user wants to trigger this action:
{description_line}It requires exactly these arguments: {arguments}

Write ONE short, natural sentence a real user would type to a task-management assistant that \
would require calling that action with exactly those arguments. Do not name or hint at any \
internal function/tool/method name — describe only what the user wants, in plain language. \
Reply with just the sentence, nothing else."""

_SOLVABILITY_PROMPT_TEMPLATE = """A user sent this request to an assistant that can only act \
through the tools listed below:

Request: "{task_text}"

Available tools:
{tool_list}

Based ONLY on the request and this tool list — not on any other context — is it clear which \
ONE tool the assistant should call? Reply with exactly one line: either "SOLVABLE" or \
"AMBIGUOUS", followed by a colon and a one-sentence reason."""


_CREATION_VERBS = ("create", "add", "new", "schedule", "insert", "make")


def _has_identifier_argument(arguments: dict, tool_name: str = "") -> bool:
    """Heuristic: does this argument set look like it references an EXISTING item (an id-like
    field alongside other values), rather than fully specifying a brand new one? Informs the
    create-vs-modify prompt guidance below — grounded in the spike's real create/update
    phrasing-confound finding (design doc Open Questions, finding 1).

    Skipped entirely when the tool's own name indicates a creation operation (create_reminder,
    add_x, schedule_x, ...) — such tools can legitimately take a foreign-key id (e.g. task_id)
    while still creating something new, and injecting "phrase as modifying an existing item"
    guidance would corrupt the generated task in exactly the way this heuristic exists to prevent
    for genuine update-shaped tools. `tool_name` is never sent to the model here — it's used only
    for this internal branch decision."""
    if any(tool_name.lower().startswith(verb) for verb in _CREATION_VERBS):
        return False
    return any(key == "id" or key.endswith("_id") for key in arguments)


_IDENTIFIER_GUIDANCE = (
    "\n\nNote: these arguments include an identifier for an EXISTING item, alongside other "
    "values to apply to it — phrase the request as modifying/updating that existing item "
    "(e.g. \"change task t1's title to X\"), not as creating a brand new one."
)


@dataclass
class GeneratedTask:
    text: str
    tool_name: str
    arguments: dict[str, str]


def generate_task(
    client: anthropic.Anthropic,
    *,
    tool_name: str,
    tool_description: str,
    arguments: dict[str, str],
    withhold_description: bool = False,
) -> GeneratedTask:
    """Generate the natural-language request for a sampled (tool, arguments) tuple.

    `withhold_description` is the spike's circularity check (scripts/circularity_check.py,
    design doc "Residual circularity risk"): when True, the prompt never sees the tool's own
    description text, only the sampled arguments.
    """
    description_line = "" if withhold_description else f"Action description: {tool_description}\n"
    prompt = _PROMPT_TEMPLATE.format(description_line=description_line, arguments=arguments)
    if _has_identifier_argument(arguments, tool_name=tool_name):
        prompt += _IDENTIFIER_GUIDANCE
    response = client.messages.create(
        model=GENERATOR_MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = next(block.text for block in response.content if block.type == "text").strip()
    return GeneratedTask(text=text, tool_name=tool_name, arguments=arguments)


def check_no_leakage(task: GeneratedTask, *, catalog_tool_names: list[str]) -> bool:
    """Guardrail (design doc / source doc S4): reject a generated task if it leaks any tool's
    literal name. Returns True if clean. Checked against ALL catalog tool names, not just the
    target — a task that accidentally names a *different* tool is just as invalid.
    """
    lowered = task.text.lower()
    return not any(name.lower() in lowered for name in catalog_tool_names)


@dataclass
class SolvabilityResult:
    solvable: bool
    reasoning: str


def _parse_solvability_response(text: str) -> tuple[bool, str]:
    stripped = text.strip()
    lowered = stripped.lower()
    if lowered.startswith("solvable"):
        _, _, reason = stripped.partition(":")
        return True, reason.strip()
    if lowered.startswith("ambiguous"):
        _, _, reason = stripped.partition(":")
        return False, reason.strip()
    return False, f"unparseable response, treated as ambiguous: {stripped}"


def check_solvability(
    client: anthropic.Anthropic,
    task: GeneratedTask,
    *,
    catalog_descriptions: dict[str, str],
) -> SolvabilityResult:
    """Guardrail (source doc S4): a second model reviews the generated task against the exact
    catalog a model-under-test would see (names + descriptions, no argument info) and judges
    whether it's clear which single tool should be called. Catches ambiguity in the GENERATED
    TASK itself — e.g. wording that reads like "create" for what should be an update — independent
    of any target tool's description quality. Scoped to a single reviewer model for the spike;
    the source doc's "3 of 3 cheap models agree" cross-check is M1 work, not built here.
    """
    tool_list = "\n".join(f"- {name}: {desc}" for name, desc in catalog_descriptions.items())
    prompt = _SOLVABILITY_PROMPT_TEMPLATE.format(task_text=task.text, tool_list=tool_list)
    response = client.messages.create(
        model=GENERATOR_MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "max_tokens":
        print("WARNING: solvability check response truncated at max_tokens", file=sys.stderr)
    text = next(block.text for block in response.content if block.type == "text").strip()
    solvable, reasoning = _parse_solvability_response(text)
    return SolvabilityResult(solvable=solvable, reasoning=reasoning)
