# TODOS

Triaged 2026-09-06 against ~900 live Sonnet 5 trials across seven servers. Each item says what
evidence would promote it; nothing is built on speculation.

## eval

- **Accepted fix on a real server (pass-rate axis).** Every `--fix` run so far rejected every
  proposal — correctly, because Sonnet 5 rarely fails for description reasons. The closed loop is
  now shown on the *precondition* axis (`docs/examples/mcp-server-git-precondition/`: 13/20 → 19/20
  and 13/20 → 0/20 with p-values), but no run has yet produced an ACCEPTED pass-rate verdict with
  real numbers. Needs a weaker model (below). **Priority:** P1
- **Non-Anthropic model under test on the corpus.** `OPENROUTER_API_KEY` was empty during every
  scenario run. A 7B model is far likelier to confuse the toy pairs and give `--fix` something to
  accept; it is also the only way to get evidence for the `(error)` column below. **Priority:** P1,
  blocked on a key.
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
