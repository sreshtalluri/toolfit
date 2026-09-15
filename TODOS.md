# TODOS

Triaged 2026-09-06 against ~900 live Sonnet 5 trials across seven servers. Each item says what
evidence would promote it; nothing is built on speculation.

## eval

- ~~**Accepted fix on the pass-rate axis.**~~ Done 2026-09-10: `set_flag` on `google/gemma-3-27b-it`
  (`ops_server.py`, `--only set_flag --fix-tool set_flag --seeds 40`), picked from the multi-model
  sweep as the tool with the largest argument-failure signature and zero unparseable JSON.
  0/40 → 5/40, p=0.0312, **ACCEPTED** — the first fix this project has measured all the way
  through. Before: "Turn a flag on or off in one environment, optionally for a percentage of
  users." After: names the two required arguments (`environment_id`, `enabled`) that the model was
  missing 40/40 and 36/40 respectively, and disambiguates from `create_flag`/`set_config`. Full
  report: `docs/examples/ops-server/report-only-set_flag.md`. Still only a 5-point move at n=40 —
  worth a second pass at higher seeds or a still-more-explicit rewrite before calling the ceiling
  found, but the mechanism is now proven end to end, not just designed.
- **Non-Anthropic model under test.** Done 2026-09-06 (Llama 3.1 8B via OpenRouter, toy server,
  `docs/examples/toy-server-llama/`). The broader question — does JSON-mechanics failure dominate
  at scale for non-Anthropic models — is now answered for 9 other OpenRouter models at 49 tools
  by the multi-model sweep (`docs/models.md`): no, zero malformed/duplicated JSON across all of
  them. The original specific ask (Llama 3.1 8B itself, the one model actually shown to hit that
  ceiling, at 49 tools) is still open — it's smaller than anything in the sweep and is the real
  test of whether the ceiling gets worse with more tools to confuse it with. **Priority:** P2
- ~~**Concurrency across tools (design doc Eng Req #1).**~~ Built 2026-09-07: `--workers` (default 4), outcomes committed in catalog order. Timing confirmed on the full 49-tool sweep (`docs/models.md`): 10 sequential models x --workers 4 on ops_server, ~20-33 min each, no failures once run one model at a time.
- ~~**Argument-level diagnostics.**~~ Built 2026-09-07: `## Argument Failures` per tool and parameter (`missing` / `extra` / `wrong` / `* duplicated|malformed argument JSON`). First use found the Llama duplicated-JSON ceiling within one run.
- ~~**Separate `(error)` column.**~~ Built 2026-09-06 once the first Llama 3.1 8B run produced
  6 malformed-JSON calls in 50 tasks. Malformed arguments keep the named tool (argument failure);
  truncation/empty responses land in `(error)`.
- ~~**Failure Attribution summary.**~~ Built 2026-09-07: new `## Failure Attribution` section at
  the top of the eval report splits total failure mass into four buckets — description confusion,
  author-clarifiable arguments, model output mechanics, and (excluded from the failure count)
  correct deprecated-tool avoidance — with counts and percentages. Report-layer aggregation over
  existing `TrialRecord`/`ToolCall` fields, no new instrumentation.
- ~~**Per-model mechanics floor.**~~ Built 2026-09-07: `## Mechanics Floor` section reports
  malformed/duplicated-argument-JSON calls plus hallucinated-tool-name calls as one baseline
  count, separate from the description-fixable buckets, so a catalog author doesn't chase
  failures no description edit can move.
- ~~**Wire `deprecated_tool` into eval.**~~ Built 2026-09-07: `build_confusion_matrix` now runs
  `lint/rules.py::run_lint` once and records `ConfusionMatrix.deprecated_tools`, feeding Failure
  Attribution bucket 4 without duplicating the self-deprecation check.
- **Task regeneration budget.** Now 2 retries with the solvability reason as a hint. Watch the
  `after N regeneration(s)` counts on real servers: if ambiguity persists mostly on tools with
  duplicate descriptions, the budget is right; if it persists elsewhere, the hint prompt needs
  work. **Priority:** P2 (observe)
- **Holm–Bonferroni instead of Bonferroni.** Uniformly more powerful with the same family-wise
  guarantee, ~10 lines in `grade/significance.py`. No run so far would have changed verdict: the
  rejections were "no failures to fix", not "p just above α". Build it when a rejection lands
  within 2× of the corrected α. **Priority:** P3
- **`--strict` on schema-excluded tools.** Warn-only (decided 2026-09-05). Since 0.1.1 resolves
  local `$ref`/`allOf`, exclusions are rare (`pattern`, remote `$ref`). Revisit only if a CI user
  reports a green gate on an unevaluated server. **Priority:** P3

## gen

- **Constraints the schema can't express.** `read_text_file` accepts `head` OR `tail`, not both;
  the schema does not say so, so no sampler rule can. The solvability warning is the mechanism,
  and it now records whether the trial failed. Excluding unsolvable tasks from the pass rate was
  considered and rejected: on `examples/crm_server.py` 33/80 tasks are flagged and that ambiguity
  *is* the planted finding. **Won't fix** beyond the outcome tag.

## Completed

- v0.2.0 (2026-09-05): multi-step trials (`--max-steps`), observed precondition graph, undeclared
  precondition findings, precondition counts in mutation/fix output.
- v0.1.0 (2026-09-05): scan, eval, mutation testing, fix loop, badge, strict, generic launch,
  Action, corpus, three real-server scenarios.
