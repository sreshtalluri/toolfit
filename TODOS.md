# TODOS

Triaged 2026-09-06 against ~900 live Sonnet 5 trials across seven servers. Each item says what
evidence would promote it; nothing is built on speculation.

## eval

- **Accepted fix on the pass-rate axis.** Still none, and the reason is now precise. With Llama
  3.1 8B on `create_task`, 40 seeds and the wider sampler pools: 15/40 → 20/40, p=0.11. The
  Argument Failures section shows 18/40 trials were `duplicated argument JSON` (the model emits
  `{...}{...}`), a ceiling no description can move. The demo needs a tool whose failures are
  description-shaped: pick it from the multi-model sweep (`docs/models.md`) — the tool with the
  highest `wrong`/`missing` count and the lowest unparseable count on a mid-tier model — then
  `--only TOOL --fix-tool TOOL --seeds 40`. **Priority:** P1
- **Non-Anthropic model under test.** Done 2026-09-06 (Llama 3.1 8B via OpenRouter, toy server,
  `docs/examples/toy-server-llama/`). Next: the same model on `examples/ops_server.py` at 49
  tools — expect malformed-JSON and argument failures to dominate. **Priority:** P2
- ~~**Concurrency across tools (design doc Eng Req #1).**~~ Built 2026-09-07: `--workers` (default 4), outcomes committed in catalog order. Timing comparison pending on the next 49-tool run.
- ~~**Argument-level diagnostics.**~~ Built 2026-09-07: `## Argument Failures` per tool and parameter (`missing` / `extra` / `wrong` / `* duplicated|malformed argument JSON`). First use found the Llama duplicated-JSON ceiling within one run.
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
