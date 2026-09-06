"""Markdown-only report for the spike (design doc Next Steps #1: "Markdown output only")."""

from __future__ import annotations

from toolfit.connect.client import ToolCatalog
from toolfit.fix.fixer import FixVerdict, ProposedFix
from toolfit.gen.taskgen import GeneratedTask
from toolfit.grade.confusion import HALLUCINATED, NO_CALL, ConfusionMatrix, undeclared_preconditions
from toolfit.grade.mutator import MutationResult, MutationTrialResult
from toolfit.grade.significance import wilson_interval
from toolfit.lint.rules import LintFinding
from toolfit.run.adapters import ToolCall


def render_spike_report(
    *,
    task: GeneratedTask,
    call: ToolCall,
    mutation: MutationResult,
    fix: ProposedFix | None,
    after_description: str,
    model: str = "claude-sonnet-5",
    seed: int,
) -> str:
    # Compute tri-state result label: IMPROVED, WORSENED, or UNCHANGED
    if mutation.improved:
        result_label = "IMPROVED"
    elif mutation.before.passed and not mutation.after.passed:
        result_label = "WORSENED"
    else:
        result_label = "UNCHANGED"

    lines = [
        "# toolfit spike report",
        "",
        "## Task",
        f"- Generated request: {task.text!r}",
        f"- Ground truth: `{task.tool_name}({task.arguments})`",
        f"- Model called: `{call.tool_name}({call.arguments})`",
        "",
        "## Mutation test",
    ]
    if fix is not None and fix.rejected:
        # Without this, a rejected fix (new_description patched back to the original) still
        # produces a guaranteed "Result: UNCHANGED" that reads like "we tried a fix and it
        # didn't help" — when no real fix was ever tested at all.
        lines.append(
            f"- Note: fix was rejected ({fix.rejection_reason}), mutation test below re-measures "
            "the ORIGINAL unchanged description, not a real fix"
        )
    lines += [
        f"- Description used for 'after': {after_description!r}",
        f"- Before: correct_tool={mutation.before.correct_tool}, correct_args={mutation.before.correct_args}, hallucinated={mutation.before.hallucinated}",
        f"- After:  correct_tool={mutation.after.correct_tool}, correct_args={mutation.after.correct_args}, hallucinated={mutation.after.hallucinated}",
        f"- Result: {result_label}",
        f"- Improved: {mutation.improved}",
    ]
    if fix is not None:
        lines += [
            "",
            "## Proposed fix",
            f"- Tool: {fix.tool_name}",
            f"- Original: {fix.original_description!r}",
            f"- Proposed: {fix.new_description!r}",
            f"- Rejected: {fix.rejected}" + (f" ({fix.rejection_reason})" if fix.rejected else ""),
        ]
    lines += [
        "",
        "## Metadata",
        f"- Model: {model}",
        f"- Seed: {seed}",
    ]
    return "\n".join(lines)


def render_confusion_matrix(matrix: ConfusionMatrix) -> str:
    tools = sorted(matrix.counts.keys())
    actual_values = {actual for row in matrix.counts.values() for actual in row}
    ordered_columns = sorted((actual_values | set(tools)) - {NO_CALL, HALLUCINATED})
    for special in (NO_CALL, HALLUCINATED):
        if special in actual_values:
            ordered_columns.append(special)

    lines = ["## Confusion Matrix", "", "| Intended \\ Called | " + " | ".join(ordered_columns) + " |"]
    lines.append("|---" * (len(ordered_columns) + 1) + "|")
    for tool in tools:
        row = [str(matrix.counts[tool].get(col, 0)) for col in ordered_columns]
        lines.append(f"| {tool} | " + " | ".join(row) + " |")

    lines += ["", "## Trial Diversity"]
    for tool in tools:
        distinct = matrix.distinct_trials[tool]
        total = matrix.trials_per_tool[tool]
        note = " (some seeds sampled identical arguments)" if distinct < total else ""
        lines.append(f"- {tool}: {distinct}/{total} distinct{note}")

    pass_rate_lines: list[str] = []
    for tool in tools:
        trials = matrix.trials_by_tool.get(tool, [])
        if not trials:
            continue
        passed = sum(1 for t in trials if t.passed)
        total = len(trials)
        lo, hi = wilson_interval(passed, total)
        pass_rate_lines.append(f"- {tool}: {passed}/{total} ({passed / total:.0%}), 95% CI [{lo:.0%}, {hi:.0%}]")
    if pass_rate_lines:
        lines += ["", "## Pass Rates"] + pass_rate_lines

    if matrix.precondition_edges:
        # Observed precondition graph (design doc M5). Mermaid renders on GitHub, which makes this
        # the shareable "confusion map" — one edge per tool pair, labelled with how often.
        lines += ["", "## Preconditions (observed)", ""]
        lines.append("Tools the model called *before* correctly calling the intended one, per trial:")
        lines.append("")
        for intended in sorted(matrix.precondition_edges):
            n = len(matrix.trials_by_tool.get(intended, []))
            for earlier, count in sorted(matrix.precondition_edges[intended].items(), key=lambda kv: -kv[1]):
                lines.append(f"- {earlier} → {intended}: {count}/{n} trials")
        # Mermaid node ids can't be raw tool names (spaces, dots, keywords like `end`): use
        # sanitised ids with quoted labels.
        node_ids: dict[str, str] = {}

        def node(name: str) -> str:
            if name not in node_ids:
                node_ids[name] = f"t{len(node_ids)}"
            return node_ids[name]

        edge_lines = []
        for intended in sorted(matrix.precondition_edges):
            n = len(matrix.trials_by_tool.get(intended, []))
            for earlier, count in sorted(matrix.precondition_edges[intended].items()):
                edge_lines.append(f"  {node(earlier)} -->|{count}/{n}| {node(intended)}")
        lines += ["", "```mermaid", "graph LR"]
        lines += [f'  {nid}["{name}"]' for name, nid in node_ids.items()]
        lines += edge_lines
        lines.append("```")
        undeclared = undeclared_preconditions(matrix)
        if undeclared:
            lines += ["", "## Undeclared Preconditions", ""]
            lines.append("The model follows these dependencies, but the catalog is silent about them. Either state")
            lines.append("the precondition in the description or make the tool self-sufficient, then re-run:")
            lines.append("")
            lines += [f"- {u}" for u in undeclared]

    if matrix.leakage_warnings:
        lines += ["", "## Leakage Warnings"] + [f"- {w}" for w in matrix.leakage_warnings]
    if matrix.solvability_warnings:
        lines += ["", "## Solvability Warnings"] + [f"- {w}" for w in matrix.solvability_warnings]
    if matrix.schema_warnings:
        lines += ["", "## Schema Warnings"] + [f"- {w}" for w in matrix.schema_warnings]

    lines += [
        "",
        "## Metadata",
        f"- Model under test: {matrix.model}",
        f"- Generator model: {matrix.generator_model}",
        f"- Seeds per tool: {matrix.seeds}",
        f"- Max steps per task: {matrix.max_steps}",
    ]

    return "\n".join(lines)


def render_mutation_results(results: list[MutationTrialResult]) -> str:
    """Mutation-testing section appended to the eval report when --mutate was used (design doc M2
    Design §5). Each mutation's `significant` flag has already been corrected for how many
    mutations ran together in this invocation (cli.py calls bonferroni_correct once, across every
    result, before this function runs) — this function only renders the verdict, it doesn't
    compute the correction itself."""
    lines = ["## Mutation Results"]
    for r in results:
        before_n = len(r.before_passes)
        after_n = len(r.after_passes)
        before_passed = sum(r.before_passes)
        after_passed = sum(r.after_passes)
        before_lo, before_hi = wilson_interval(before_passed, before_n)
        after_lo, after_hi = wilson_interval(after_passed, after_n)
        verdict = "SIGNIFICANT" if r.significant else "not significant"
        lines += [
            "",
            f"### {r.tool_name}",
            f"- New description: {r.new_description!r}",
            f"- Before: {before_passed}/{before_n} ({before_passed / before_n:.0%}), 95% CI [{before_lo:.0%}, {before_hi:.0%}]",
            f"- After:  {after_passed}/{after_n} ({after_passed / after_n:.0%}), 95% CI [{after_lo:.0%}, {after_hi:.0%}]",
            f"- Reached via an earlier call: {r.before_preconditions}/{before_n} → {r.after_preconditions}/{after_n}",
            f"- p-value: {r.p_value:.4f}",
            f"- Verdict (Bonferroni-corrected): {verdict}",
        ]
    return "\n".join(lines)


def render_fix_results(verdicts: list[FixVerdict]) -> str:
    """--fix section (design doc M4 / source doc §7): every proposal, accepted or not — showing the
    rejected ones is what makes the accepted ones believable."""
    lines = ["## Proposed Fixes"]
    if not verdicts:
        lines += ["", "No tool had a failed trial, so nothing to fix."]
        return "\n".join(lines)
    for v in verdicts:
        lines += [
            "",
            f"### {v.proposal.tool_name} — {'ACCEPTED' if v.accepted else 'REJECTED'}",
            f"- Before: {v.proposal.original_description!r}",
            f"- After:  {v.proposal.new_description!r}",
        ]
        if v.trial is not None:
            t = v.trial
            n = len(t.before_passes)
            lines += [
                f"- Pass rate: {sum(t.before_passes)}/{n} → {sum(t.after_passes)}/{n}, p-value {t.p_value:.4f}",
                f"- Reached via an earlier call: {t.before_preconditions}/{n} → {t.after_preconditions}/{n}",
            ]
        lines.append(f"- Reason: {v.reason}")
    return "\n".join(lines)


def render_lint_report(catalog: ToolCatalog, findings: list[LintFinding]) -> str:
    """Markdown report for `scan` (design doc M0 Design) — a findings list with a count, never a
    numeric/letter grade, matching the credibility-first stance already established for `eval`."""
    lines = ["# toolfit scan report", ""]
    if not findings:
        lines.append(f"No findings across {len(catalog.tools)} tool(s).")
        return "\n".join(lines)

    lines.append(f"{len(findings)} finding(s) across {len(catalog.tools)} tool(s).")

    by_rule: dict[str, list[LintFinding]] = {}
    for finding in findings:
        by_rule.setdefault(finding.rule_id, []).append(finding)

    for rule_id in sorted(by_rule):
        lines += ["", f"## {rule_id}"]
        for finding in by_rule[rule_id]:
            lines.append(f"- {finding.message}")

    return "\n".join(lines)
