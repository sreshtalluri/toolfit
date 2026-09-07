# TODOS

Triaged 2026-09-06 against ~900 live Sonnet 5 trials across seven servers. Each item says what
evidence would promote it; nothing is built on speculation.

## eval

- **Accepted fix on the pass-rate axis.** Still none, and now for a measured reason rather than
  a missing model. With Llama 3.1 8B the fixer's rewrite of `create_task` helped every time
  (5/10 → 8/10; then 14/20 → 17/20 alone at 20 seeds, p=0.23 vs α=0.05,
  `docs/examples/toy-server-llama/report-create_task-20seeds.md`) but a +15-point effect needs
  roughly 40+ paired trials to clear 0.05. Two things would change this: (a) `--seeds 40` on one
  tool is now cheap with `--only` (~2 min on Llama) — try it; (b) `create_task` sampled only
  9/20 distinct argument sets, so half the trials are correlated repeats. The sampler's free-text
  pool is too small; widen it before spending on more seeds. **Priority:** P1
- **Non-Anthropic model under test.** Done 2026-09-06 (Llama 3.1 8B via OpenRouter, toy server,
  `docs/examples/toy-server-llama/`). Next: the same model on `examples/ops_server.py` at 49
  tools — expect malformed-JSON and argument failures to dominate. **Priority:** P2
- **Concurrency across tools (design doc Eng Req #1).** Everything is sequential; a 12-tool server
  at 10 seeds × 3 steps is ~20 min. `--only` covers the iterate loop, so this matters mainly for
  first runs and the Action. A `ThreadPoolExecutor` over tools in `build_confusion_matrix` with
  the existing retry/backoff is ~15 lines; needs a live timing comparison and a check that rate
  limits don't turn into `(no call)` inflation. **Priority:** P2
- **Argument-level diagnostics.** Most remaining misses on strong models are arguments
  (`read_multiple_files` 0/5), and the report only says "wrong args". A per-parameter breakdown —
  omitted required, wrong enum, wrong format — tells an author which field to document.
  **Priority:** P2
- ~~**Separate `(error)` column.**~~ Built 2026-09-06 once the first Llama 3.1 8B run produced
  6 malformed-JSON calls in 50 tasks. Malformed arguments keep the named tool (argument failure);
  truncation/empty responses land in `(error)`.
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
