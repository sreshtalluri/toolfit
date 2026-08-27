"""Inverted task generation (design doc "The Core Technique").

Samples a ground-truth (tool, arguments) tuple FIRST (schema_sampler.py), then asks a generator
model to write the natural-language request that leads to exactly those arguments, without
naming the tool. Grading (grade/grader.py) compares the model-under-test's actual call against
this sampled tuple — never against the generator's opinion.
"""

from __future__ import annotations

from dataclasses import dataclass

import anthropic

GENERATOR_MODEL = "claude-sonnet-5"

_PROMPT_TEMPLATE = """A user wants to trigger this action:
{description_line}It requires exactly these arguments: {arguments}

Write ONE short, natural sentence a real user would type to a task-management assistant that \
would require calling that action with exactly those arguments. Do not name or hint at any \
internal function/tool/method name — describe only what the user wants, in plain language. \
Reply with just the sentence, nothing else."""


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
    response = client.messages.create(
        model=GENERATOR_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    return GeneratedTask(text=text, tool_name=tool_name, arguments=arguments)


def check_no_leakage(task: GeneratedTask, *, catalog_tool_names: list[str]) -> bool:
    """Guardrail (design doc / source doc S4): reject a generated task if it leaks any tool's
    literal name. Returns True if clean. Checked against ALL catalog tool names, not just the
    target — a task that accidentally names a *different* tool is just as invalid.
    """
    lowered = task.text.lower()
    return not any(name.lower() in lowered for name in catalog_tool_names)
