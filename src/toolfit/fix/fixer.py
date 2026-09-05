"""Propose a rewritten tool description; reject degenerate rewrites before they're even
re-measured (design doc Failure Mode: "Fix-generation failure")."""

from __future__ import annotations

from dataclasses import dataclass

import anthropic

from toolfit.connect.client import ToolCatalog
from toolfit.grade.confusion import ConfusionMatrix
from toolfit.grade.mutator import MutationTrialResult, run_mutation_trials
from toolfit.run.adapters import ModelAdapter

FIXER_MODEL = "claude-sonnet-5"

_PROMPT_TEMPLATE = """This tool's description is causing an AI assistant to confuse it with a \
similar tool:

Tool name: {tool_name}
Current description: {current_description}
Parameters: {parameters}
Other tools in the same catalog:
{other_tools}

Write a replacement description (one sentence) that clearly distinguishes this tool from the \
others, states what it does and what arguments it needs. Mention only the parameters and values \
listed above — do not invent optional fields, defaults, or example values. Reply with just the new \
description text, nothing else."""


def _describe_parameters(input_schema: dict | None) -> str:
    if not input_schema or not input_schema.get("properties"):
        return "(none)"
    required = set(input_schema.get("required", []))
    parts = []
    for name, prop in input_schema["properties"].items():
        kind = prop.get("type") or ("one of " + "/".join(str(b.get("type")) for b in prop.get("anyOf", [])))
        detail = f", values: {', '.join(map(str, prop['enum']))}" if "enum" in prop else ""
        parts.append(f"{name} ({kind}{', required' if name in required else ', optional'}{detail})")
    return "; ".join(parts)


@dataclass
class ProposedFix:
    tool_name: str
    original_description: str
    new_description: str
    rejected: bool
    rejection_reason: str | None


def propose_fix(
    client: anthropic.Anthropic,
    *,
    tool_name: str,
    current_description: str,
    other_tool_names: list[str],
    input_schema: dict | None = None,
    other_descriptions: dict[str, str] | None = None,
) -> ProposedFix:
    # The rewriter has to see the real parameters and the neighbours' real wording: without them
    # (first live run, 2026-09-05) it invented "optional description, due date" and enum values
    # that don't exist, and the rewrite measured worse than the original.
    other_descriptions = other_descriptions or {}
    prompt = _PROMPT_TEMPLATE.format(
        tool_name=tool_name,
        current_description=current_description,
        parameters=_describe_parameters(input_schema),
        other_tools="\n".join(f"- {n}: {other_descriptions.get(n, '(no description)')}" for n in other_tool_names),
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
    new_description = next((block.text for block in response.content if block.type == "text"), "").strip()
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


@dataclass
class FixVerdict:
    proposal: ProposedFix
    trial: MutationTrialResult | None  # None when the proposal was rejected before re-measurement

    @property
    def accepted(self) -> bool:
        # Significance alone isn't enough — the test is one-sided for improvement, but "significant
        # and worse" can't happen; the explicit after > before check keeps that invariant readable.
        return (
            self.trial is not None
            and self.trial.significant
            and sum(self.trial.after_passes) > sum(self.trial.before_passes)
        )

    @property
    def reason(self) -> str:
        if self.trial is None:
            return f"rejected before re-measurement: {self.proposal.rejection_reason}"
        before, after = sum(self.trial.before_passes), sum(self.trial.after_passes)
        if self.accepted:
            return "accepted"
        if after < before:
            return "rejected: made things worse"
        if after == before:
            return "rejected: no change"
        return "rejected: improvement not significant after correction"


def run_fix_loop(
    matrix: ConfusionMatrix,
    catalog: ToolCatalog,
    adapter: ModelAdapter,
    client: anthropic.Anthropic,
) -> list[FixVerdict]:
    """M4 fix loop (design doc Pipeline: mutation output -> fix/ -> re-verify). For every tool with
    at least one failed trial: propose a rewrite, then re-run that tool's OWN base tasks against a
    catalog with only that description patched (protocol-level, Premise 1). Tools the model
    actually confused it with are listed first in the rewrite prompt. `significant` on each trial is
    left for the caller to set after Bonferroni-correcting across everything tested in the run.
    """
    verdicts: list[FixVerdict] = []
    for tool_name, trials in matrix.trials_by_tool.items():
        if all(t.passed for t in trials):
            continue
        tool = catalog.get(tool_name)
        if tool is None:
            continue
        confused_with = [
            called
            for called, n in matrix.counts.get(tool_name, {}).items()
            if n > 0 and called != tool_name and catalog.get(called) is not None
        ]
        others = confused_with + [n for n in catalog.names() if n != tool_name and n not in confused_with]
        proposal = propose_fix(
            client,
            tool_name=tool_name,
            current_description=tool.description or "",
            other_tool_names=others,
            input_schema=tool.input_schema,
            other_descriptions={t.name: t.description or "" for t in catalog.tools},
        )
        if proposal.rejected:
            verdicts.append(FixVerdict(proposal, None))
            continue
        trial = run_mutation_trials(
            matrix, catalog, adapter, tool_name=tool_name, new_description=proposal.new_description
        )
        verdicts.append(FixVerdict(proposal, trial))
    return verdicts
