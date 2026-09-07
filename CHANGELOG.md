# Changelog

## 0.2.1 (2026-09-07)

- **Failure Attribution** section, new at the top of the eval report: splits total failure mass
  into four buckets validated against real trial data — description confusion (off-diagonal
  confusion-matrix mass), author-clarifiable arguments (right tool, wrong args), model output
  mechanics (hallucinated tool name, malformed/duplicated argument JSON, garbled no-call), and
  correct deprecated-tool avoidance (excluded from the failure count, not a bug). Counts and
  percentages, report-layer aggregation over existing per-trial data — no new instrumentation.
- **Mechanics Floor** section, printed alongside Failure Attribution: malformed/duplicated
  argument JSON plus hallucinated tool-name calls, tallied as one baseline metric a catalog
  author cannot move by editing a description, so they don't spend time chasing it.
- `deprecated_tool` (from `scan`'s lint rules) is now wired into `eval`: `build_confusion_matrix`
  runs the static scan once and records which tools self-declare deprecated, feeding Failure
  Attribution's fourth bucket.
- `--workers N` (default 4): tools are evaluated concurrently; each tool's own calls stay
  sequential and outcomes are committed in catalog order, so the report is unchanged for a given
  set of answers. Design doc Eng Req #1, finally.
- **Multi-model sweep** (`docs/models.md`): 10 models across `toy_server.py`/`crm_server.py`/
  `ops_server.py` at 10 seeds. Confirms the pass-rate ceiling isn't JSON formation on any of these
  models (zero malformed/duplicated-JSON trials across 21 completed combinations) — failures are
  almost entirely wrong-tool-called or wrong-argument. `toy_server`'s `count_tasks`/`list_tasks`
  pair (identical descriptions) fails 0/10 on every model tested, independent of model strength.
- **Argument Failures** section: per-parameter `missing` / `extra` / `wrong` / `* malformed/duplicated argument JSON`
  counts for trials that reached the right tool. Structural, no model opinion. This is the answer
  to "strong models don't fail for description reasons, so what do they fail on": the field.
- No-call replies are tagged `asked` / `refused` / `other`.
- Unparseable argument JSON is classified: `duplicated argument JSON` (`{...}{...}`, a valid
  object followed by another) vs `malformed argument JSON`. Found by the first Argument Failures
  section on a 40-seed Llama 3.1 8B run (`docs/examples/toy-server-llama/report-create_task-40seeds.md`):
  18 of 25 `create_task` failures were the object emitted twice. The fixer's rewrite still went
  15/40 → 20/40 (p=0.11, rejected), and now the report says why it can't do better: a description
  cannot fix a model that emits its arguments twice.
- Sampler example pools widened (12 titles, 8 notes, 6 ids): `create_task` could only produce
  nine distinct argument sets, so seeds past nine were correlated repeats (9/20 distinct measured).

First run with a model that actually gets confused (Llama 3.1 8B via OpenRouter, toy server,
64%) changed three things:

- **Ambiguous tasks are regenerated.** The generator never sees the tool's name, so a vague
  description ("Get tasks by status." on a count tool) yields a vague request ("show me the open
  tasks") that no rewrite can rescue, because mutation/fix trials reuse the task. When the
  solvability check says AMBIGUOUS, the task is regenerated up to 2 times with the reason as a
  hint. The last attempt is kept and flagged either way: on a catalog with duplicate
  descriptions the ambiguity is the finding.
- **`(error)` column.** Truncated or empty provider responses are tallied as `(error)`, not
  `(no call)`. Unparseable argument JSON keeps the tool the model named and scores as an argument
  failure — 6 of 50 Llama calls did this and read as the model ignoring the tool.
- **Fixer proposals are capped at 25 words.** Two of four rewrites made Llama worse (4→3, 9→7);
  both were long parameter enumerations.
- Same run again on this code (`docs/examples/toy-server-llama/`): solvability warnings 31 → 5
  (all on the identical-description pair, after 2 regenerations), no proposal made things worse,
  `create_task` 5/10 → 8/10 on its proposal (rejected only because five proposals share one
  correction at n=10). `count_tasks` stayed 0/10 even under "Return the number of tasks…", which
  settles it as model weakness rather than description — the honest verdict is "no net change".
- New example: `examples/ops_server.py`, 49 tools across users/tickets/deployments/alerts/
  on-call/docs/flags/config, with planted static and behavioural problems (docstring lists
  them; scan findings pinned by test). Sonnet 5 baseline in `docs/examples/ops-server/`: 84%,
  48 min, no exclusions.
- **No-Call Replies section.** 20 of the 38 ops failures were `(no call)` and the report could
  not say why. Adapters now keep the model's reply text on a no-call and the report lists it
  per failed trial.

- `--only NAME` (repeatable): generate tasks only for the named tools while still offering the
  model the whole catalog. This is the iterate loop the fix flow was missing — measured on
  mcp-server-git, the full 12-tool run at 20 seeds took 2551 s and `--only git_commit` with one
  `--mutate` took 17 s. Tools named in `--mutate`/`--fix-tool` must be in `--only`; the CLI
  exits 1 before any call otherwise. The report's Metadata says which tools were evaluated.
- The precondition delta in `--mutate`/`--fix` output now carries its own two-sided exact
  p-value (`reached via an earlier call: 5/10 → 0/10 (two-sided p=0.0625)`). Informational only:
  the acceptance rule stays one-sided on the pass rate, because a description can legitimately
  move the precondition rate either way. Evidence in `docs/examples/mcp-server-git-precondition/`:
  stating the `git_add` dependency in `git_commit` moved it 13/20 → 19/20; claiming
  self-sufficiency moved it 13/20 → 0/20; pass rate 20/20 both ways, so the old output read
  "not significant" for a change that was anything but.
- Solvability warnings now carry the trial's outcome (`seed 4, failed` / `seed 2, passed anyway`),
  so a reader can tell whether a tool's failures sit on tasks the sampler couldn't express (e.g.
  `head` and `tail` together) or on solvable ones. Unsolvable tasks are still graded on purpose:
  on a catalog with duplicate tools the ambiguity is the finding.

## 0.2.0 (2026-09-05)

**Pass rates change meaning — and go up on servers with precondition tools.** Trials are now
multi-step: the model may make up to `--max-steps` calls (default 3), each answered with a
synthetic result, and a task passes if the intended tool is called correctly at any step.
`--max-steps 1` restores 0.1.x grading exactly.

- New report sections: **Preconditions (observed)** — the tools the model called before the
  correct one, as a list and a mermaid graph — and **Undeclared Preconditions**: dependencies
  the model follows in ≥30% of trials that the target tool's description never mentions.
- `--mutate` / `--fix` verdicts show precondition counts before → after alongside pass rates.
- Roughly 2× wall time on servers where the model chains (measured: mcp-server-git 1177 s vs ~500 s).
- Synthetic results come from the tool's `outputSchema` when declared, else `{"ok": true}`;
  never from a model.
- The confusion matrix is still *intended × first call*, so 0.1.x matrices remain comparable.

## 0.1.1 (2026-09-05)

- `AGENTS.md`: operating manual for agents installing/running toolfit on a user's behalf, verified against the published wheel in a fresh venv.
- `examples/crm_server.py`: production-shaped example (formats, enums, nested object, bounds) with four planted description problems; reference eval output under `docs/examples/crm-server/`.
- `eval` checks API keys before launching the server.
- Bundled examples carry PEP 723 inline metadata so `uv run` works from any directory.

## 0.1.0 (2026-09-05)

First release.

- `toolfit scan <server>`: free static lint over `tools/list` — missing, too-short, duplicated, and self-declared-deprecated descriptions. No model calls.
- `toolfit eval <server>`: inverted task generation (sample schema-valid arguments first, then ask a generator to write the request), structural grading with canonicalisation, confusion matrix, per-tool pass rates with Wilson 95% intervals, leakage and solvability guardrails reported as warnings.
- `--mutate 'tool:new description'`: paired re-run of that tool's own tasks against a catalog with one description patched; exact one-sided McNemar p-value; one Bonferroni correction across everything re-measured in the run.
- `--fix` / `--fix-tool NAME`: propose a rewrite per failing tool (rewriter sees the real parameters and neighbour descriptions), re-measure, report accepted and rejected alike; `toolfit-fixes.json` with description text only.
- `--badge`: SVG coloured by pass rate with model, generator, seeds, and task-suite hash embedded. `--strict` / `--strict-threshold`: exit codes for CI.
- Servers as a `.py` script (`uv run`), any command line (`npx -y …`), or an `http(s)://` URL; subprocess inherits the environment.
- Adapters for Anthropic, OpenAI, and OpenRouter, inferred from `--model`; retry with backoff on 429/5xx for every model call.
- Composite GitHub Action (`action.yml`); repo CI on 3.10/3.13; PyPI publish on `v*` tags via trusted publishing.
- Evidence: toy server and three public servers evaluated end-to-end (`docs/examples/`), twenty public servers scanned (`docs/corpus.md`).
