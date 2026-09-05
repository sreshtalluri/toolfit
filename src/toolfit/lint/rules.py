"""Static lint rules over an MCP tool catalog — no model calls, no cost, runs in well under a
second (design doc M0 Design). Each rule is a pure function over ToolCatalog; run_lint aggregates
all three into one findings list for the `scan` CLI command to render.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from toolfit.connect.client import ToolCatalog

_SHORT_DESCRIPTION_THRESHOLD = 15
_SELF_DEPRECATED = re.compile(r"^\W*deprecated\b|\bdeprecated\s*[:\-—(]|\b(is|are|now|been)\s+deprecated\b", re.I)


@dataclass
class LintFinding:
    rule_id: str
    tool_name: str | None  # None for catalog-wide findings (e.g. duplicate_description)
    message: str


def _missing_description(catalog: ToolCatalog) -> list[LintFinding]:
    findings = []
    for tool in catalog.tools:
        if not (tool.description or "").strip():
            findings.append(
                LintFinding(
                    rule_id="missing_description", tool_name=tool.name, message=f"{tool.name} has no description"
                )
            )
    return findings


def _short_description(catalog: ToolCatalog) -> list[LintFinding]:
    findings = []
    for tool in catalog.tools:
        description = (tool.description or "").strip()
        if description and len(description) < _SHORT_DESCRIPTION_THRESHOLD:
            findings.append(
                LintFinding(
                    rule_id="short_description",
                    tool_name=tool.name,
                    message=f"{tool.name}'s description is only {len(description)} characters: {description!r}",
                )
            )
    return findings


def _duplicate_description(catalog: ToolCatalog) -> list[LintFinding]:
    # Maps a case/whitespace-normalized description to (original description text, tool names
    # sharing it) — the original text (not the normalized key) is what the finding's message
    # shows, so the report reads naturally regardless of the catalog's own casing choices.
    groups: dict[str, tuple[str, list[str]]] = {}
    for tool in catalog.tools:
        description = (tool.description or "").strip()
        if not description:
            continue
        key = " ".join(description.split()).casefold()
        if key not in groups:
            groups[key] = (description, [])
        groups[key][1].append(tool.name)

    findings = []
    for original_description, tool_names in groups.values():
        if len(tool_names) < 2:
            continue
        findings.append(
            LintFinding(
                rule_id="duplicate_description",
                tool_name=None,
                message=f"{', '.join(sorted(tool_names))} share the identical description {original_description!r}",
            )
        )
    return findings


def _deprecated_description(catalog: ToolCatalog) -> list[LintFinding]:
    # Found on @modelcontextprotocol/server-filesystem: `read_file` says "DEPRECATED: Use
    # read_text_file instead" and Sonnet 5 obeys, scoring 0/10. A deprecated tool still in the
    # catalog costs context tokens and shows up as confusion in every eval; drop it or hide it.
    findings = []
    for tool in catalog.tools:
        # Only when the tool says it about itself — "DEPRECATED: …", "is deprecated", or leading —
        # not when deprecation is its subject ("List deprecated packages").
        if _SELF_DEPRECATED.search(tool.description or ""):
            findings.append(
                LintFinding(
                    rule_id="deprecated_tool",
                    tool_name=tool.name,
                    message=f"{tool.name} describes itself as deprecated but is still in the catalog",
                )
            )
    return findings


_RULES = (_missing_description, _short_description, _duplicate_description, _deprecated_description)


def run_lint(catalog: ToolCatalog) -> list[LintFinding]:
    findings: list[LintFinding] = []
    for rule in _RULES:
        findings.extend(rule(catalog))
    return findings
