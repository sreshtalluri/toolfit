"""Propose a rewritten tool description; reject degenerate rewrites before they're even
re-measured (design doc Failure Mode: "Fix-generation failure")."""

from __future__ import annotations

from dataclasses import dataclass

import anthropic

FIXER_MODEL = "claude-sonnet-5"

_PROMPT_TEMPLATE = """This tool's description is causing an AI assistant to confuse it with a \
similar tool:

Tool name: {tool_name}
Current description: {current_description}
Other tools in the same catalog: {other_tool_names}

Write a replacement description (one sentence) that clearly distinguishes this tool from the \
others, states what it does and what arguments it needs. Reply with just the new description \
text, nothing else."""


@dataclass
class ProposedFix:
    tool_name: str
    original_description: str
    new_description: str
    rejected: bool
    rejection_reason: str | None


def propose_fix(
    client: anthropic.Anthropic, *, tool_name: str, current_description: str, other_tool_names: list[str]
) -> ProposedFix:
    prompt = _PROMPT_TEMPLATE.format(
        tool_name=tool_name,
        current_description=current_description,
        other_tool_names=", ".join(other_tool_names),
    )
    response = client.messages.create(
        model=FIXER_MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    # Sonnet 5 runs adaptive thinking by default (no `thinking` param needed to trigger it),
    # so response.content[0] is not guaranteed to be the text block — found and fixed as a
    # Task 3 review finding (SDD ledger), applied here preemptively since taskgen.py had the
    # identical bug.
    new_description = next(block.text for block in response.content if block.type == "text").strip()
    return _validate(tool_name, current_description, new_description)


def _validate(tool_name: str, current_description: str, new_description: str) -> ProposedFix:
    """Failure Mode (design doc): reject empty, identical, or clearly-unrelated rewrites before
    they're re-measured — same spirit as the noise-threshold rejection for mutation deltas."""
    if not new_description.strip():
        return ProposedFix(tool_name, current_description, new_description, rejected=True, rejection_reason="empty rewrite")
    if new_description.strip() == current_description.strip():
        return ProposedFix(tool_name, current_description, new_description, rejected=True, rejection_reason="identical to original")
    if len(new_description.strip()) < 10:
        return ProposedFix(
            tool_name, current_description, new_description, rejected=True, rejection_reason="too short to be a real description"
        )
    return ProposedFix(tool_name, current_description, new_description, rejected=False, rejection_reason=None)
