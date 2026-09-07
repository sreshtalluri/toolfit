# Multi-model sweep

`toolfit eval` run across 3 servers x 10 models at `--seeds 10 --workers 4`. Full per-model
reports live in `docs/examples/model-sweep/<server-name>/<model-slug>.md`. 21/30 combinations
completed; the other 9 are missing for reasons documented below (not description-confusion
findings — flagged so nobody mistakes a blank cell for a clean run).

Task generation always runs on Anthropic (`claude-sonnet-5`) regardless of which model is under
test; only the model-under-test call routes to OpenRouter for the `vendor/model` entries.

## Coverage

| Server (tools) | Completed | Missing |
|---|---|---|
| `toy_server.py` (5 tools) | 8/10 | `google/gemini-2.5-flash`, `claude-sonnet-5` |
| `crm_server.py` (8 tools) | 9/10 | `claude-sonnet-5` |
| `ops_server.py` (49 tools) | 4/10 | `mistralai/mistral-small-3.2-24b-instruct`, `openai/gpt-4o-mini`, `openai/gpt-4.1-mini`, `deepseek/deepseek-chat-v3-0324`, `google/gemini-2.5-flash`, `claude-sonnet-5` |

Two distinct causes for the gaps, both external and not fixable by retrying:

1. **`claude-sonnet-5` self-evaluation contention.** When `--model claude-sonnet-5` is the model
   under test, every trial doubles Anthropic call volume (task generation + trial, both
   Anthropic) versus an OpenRouter model under test (task generation only). `claude-sonnet-5`
   failed all 3 sequential-run attempts (with 30s cooldowns) on both `toy_server.py` and
   `crm_server.py` with sustained `429`s; the built-in retry (5 attempts, backoff to ~16s) isn't
   enough to ride out a sustained-not-bursty rate-limit window. This is a real, reproducible
   gap in the CLI's self-test story, not a fluke — worth a follow-up (e.g. a documented warning,
   or spacing self-eval trials further apart) but out of scope for this data-collection pass.
2. **Anthropic account ran out of credit mid-`ops_server` sweep** (confirmed directly: a fresh
   minimal `--seeds 1` call returned `400: Your credit balance is too low to access the
   Anthropic API`). Since task generation always needs Anthropic, this blocked every remaining
   combination regardless of which model was under test — it's why 6 of `ops_server.py`'s 10
   models are missing, not just the two Anthropic-heavy ones. This needs a billing top-up before
   the remaining `ops_server.py` combos (and the 3 `claude-sonnet-5` cells) can be collected.

Concurrency note: the sweep started at 4 models concurrent (`xargs -P 4`, matching the brief's
suggested ceiling) and that immediately produced 6/10 failures on `toy_server.py` from stacked
OpenRouter rate limits (16 concurrent requests: 4 models x `--workers 4`). Switched to fully
sequential across models (still `--workers 4` within a single model's own trials) for the rest of
the sweep, which is why `crm_server.py` and `ops_server.py` took much longer wall-clock but were
far more reliable.

## Dominant failure mode: description confusion, not malformed JSON

Across all 21 successful runs, **zero** malformed/duplicated-argument-JSON trials and only one
stray `(error)` (unparseable-response) trial total. Every model in this sweep (70B/32B/24B-class
open models and the commercial small/mini tiers) is capable enough that JSON formation basically
isn't the bottleneck — this is a different regime from the Llama 3.1 8B duplicated-JSON ceiling
already on record in `TODOS.md` (18/40 trials on `create_task`). Here the failures are almost
entirely:

- **Wrong tool called** because two tools share an identical or near-identical description.
  `toy_server.py`'s `count_tasks` vs. `list_tasks` (both intentionally described only as "Get
  tasks by status.") is the cleanest example in the whole sweep: **every single model, 0/10 pass
  rate on `count_tasks`, 100% of the time**, because the confusion matrix always resolves those
  trials as `list_tasks` calls instead. This is model-capability-independent — even
  `openai/gpt-4.1-mini` (the best overall `toy_server.py` pass rate, 70%) still hits 0% on
  `count_tasks` specifically. It's the single clearest "no description, no chance" ceiling
  observed.
- **Wrong/missing argument values** once the right tool is picked, especially on `ops_server.py`
  where descriptions don't spell out enough about parameter shape.

## Surprising result: bigger/newer model != better tool selection

`openai/gpt-4.1-mini` had the single worst `crm_server.py` pass rate in the sweep (47/80, 59%),
worse than `mistralai/mistral-nemo` (80%) and `google/gemma-3-27b-it` (85%) — both smaller/older
models. Its failures cluster on `add_note`, `create_contact`, `list_contacts`,
`search_contacts`, and `send_email` (all 40-50% pass), which reads as over-eager tool substitution
within the CRM catalog rather than a capability gap. Meanwhile on `toy_server.py` it had the
*best* pass rate (70%). Tool-selection accuracy doesn't track cleanly with general model quality
or recency — it's sensitive to how a specific catalog's descriptions read to that specific model.

## Aggregate pass rates (sum of per-tool trials / total trials, all completed combos)

| Model | toy_server (50 trials) | crm_server (80 trials) | ops_server (490 trials) |
|---|---|---|---|
| meta-llama/llama-3.3-70b-instruct | 32/50 (64%) | 55/80 (69%) | 317/490 (65%) |
| qwen/qwen3-32b | 29/50 (58%) | 61/80 (76%) | 418/490 (85%) |
| mistralai/mistral-small-3.2-24b-instruct | 33/50 (66%) | 72/80 (90%) | — |
| mistralai/mistral-nemo | 31/50 (62%) | 64/80 (80%) | 407/490 (83%) |
| google/gemma-3-27b-it | 34/50 (68%) | 68/80 (85%) | 373/490 (76%) |
| openai/gpt-4o-mini | 32/50 (64%) | 72/80 (90%) | — |
| openai/gpt-4.1-mini | 35/50 (70%) | 47/80 (59%) | — |
| deepseek/deepseek-chat-v3-0324 | 33/50 (66%) | 65/80 (81%) | — |
| google/gemini-2.5-flash | — | 67/80 (84%) | — |
| claude-sonnet-5 | — | — | — |

## Pick for the P1 demo tool (`TODOS.md` "Accepted fix on the pass-rate axis")

`TODOS.md` asks for the tool with the highest wrong/missing count and lowest unparseable count on
a mid-tier model, to demo `--only TOOL --fix-tool TOOL --seeds 40`. From the `ops_server.py` x
`google/gemma-3-27b-it` run (a genuine mid-tier model, not the biggest or smallest in the sweep):

**`set_flag`** — 0/10 pass rate, 0 unparseable, and two parameters failing almost every trial:
`environment_id wrong 10/10`, `enabled missing 10/10`, `rollout_percent missing 7/10` (27 failure
counts across 3 params, the single largest defect signature in the sweep). Its description
("Turn a flag on or off in one environment, optionally for a percentage of users.") never says
`environment_id` and `enabled` are both required, non-optional inputs — exactly the kind of gap a
description fix can plausibly move. Runner-up: `create_flag` on the same model (`description
wrong 10/10`, `default_on missing 7/10`, 17 total) — also 0/10 pass rate, also zero unparseable.
Both are stronger candidates than `create_task` (the previously-tried tool that turned out to have
the duplicated-JSON ceiling on Llama 3.1 8B) because gemma-3-27b-it never produces malformed JSON
here, so a description fix has a clean shot at moving the pass rate rather than being capped by an
unrelated JSON-formation failure.

## Reproducing / finishing the sweep

`sweep.sh` (repo root) re-runs all 10 models sequentially against a given server, skipping any
`<model>.md` that already exists and is non-empty, and retrying a model up to 3 times (30s
cooldown between attempts) before giving up and leaving a `.stderr` file next to the empty
`.md`. Once Anthropic credit is restored: `bash sweep.sh examples/ops_server.py ops-server` picks
up exactly the 6 missing `ops_server.py` combos; same for `toy_server.py` /`crm_server.py` and
`claude-sonnet-5`.
