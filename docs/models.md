# Multi-model sweep

`toolfit eval` run across 3 servers x 10 models at `--seeds 10 --workers 4`. Full per-model
reports live in `docs/examples/model-sweep/<server-name>/<model-slug>.md`. **30/30 combinations
completed.**

Task generation always runs on Anthropic (`claude-sonnet-5`) regardless of which model is under
test; only the model-under-test call routes to OpenRouter for the `vendor/model` entries.

## Getting to 30/30

The first pass landed 21/30 and stalled on two external blockers, both since resolved:

1. **`claude-sonnet-5` self-evaluation contention.** When `--model claude-sonnet-5` is the model
   under test, every trial doubles Anthropic call volume (task generation + trial, both
   Anthropic) versus an OpenRouter model under test (task generation only). It failed all 3
   attempts on `toy_server.py` in the first pass, then succeeded on attempt 1 on `crm_server.py`
   and `ops_server.py` in the second — this is real, reproducible contention, but flaky rather
   than a hard wall; a retry loop with cooldowns is enough to ride it out.
2. **Anthropic credit exhaustion mid-`ops_server` sweep**, confirmed directly via a `400: Your
   credit balance is too low` error. Fixed by a billing top-up; every remaining combination
   (including three OpenRouter-model cells that had looked like OpenRouter rate limits) completed
   on the very next attempt, confirming they were queued behind the same Anthropic-side block,
   not actually OpenRouter-limited.

`sweep.sh` (repo root) is what made this resumable: it skips any `<model>.md` that already exists
and is non-empty, and retries a model up to 3 times (30s cooldown) before giving up. It also
survived two unrelated interruptions — the host running low on system memory and killing the
background process outright — by just being re-invoked; nothing was lost or re-run unnecessarily.

## Dominant failure mode: description confusion, not malformed JSON

Across all 30 runs, **zero** malformed/duplicated-argument-JSON trials and zero hallucinated tool
names — confirmed via the Mechanics Floor line in every report generated after the Failure
Attribution feature landed, and by direct inspection of the rest. Every model in this sweep
(70B/32B/24B-class open models through commercial small/mini tiers, plus Claude Sonnet 5 itself)
is capable enough that JSON formation basically isn't the bottleneck — a different regime from the
Llama 3.1 8B duplicated-JSON ceiling on record in `TODOS.md` (18/40 trials on `create_task`). Here
the failures are almost entirely:

- **Wrong tool called** because two tools share an identical or near-identical description.
  `toy_server.py`'s `count_tasks` vs. `list_tasks` (both intentionally described only as "Get
  tasks by status.") is the cleanest example in the whole sweep: **every single model, 0/10 pass
  rate on `count_tasks`, 100% of the time**, because the confusion matrix always resolves those
  trials as `list_tasks` calls instead. This is model-capability-independent — even the best
  overall `toy_server.py` performer (`claude-sonnet-5`, 74%) still hits 0% on `count_tasks`
  specifically. It's the single clearest "no description, no chance" ceiling observed.
- **Wrong/missing argument values** once the right tool is picked, especially on `ops_server.py`
  where descriptions don't spell out enough about parameter shape.

## Surprising result: bigger/newer model != better tool selection

`openai/gpt-4.1-mini` had the single worst `crm_server.py` pass rate in the sweep (47/80, 59%),
worse than `mistralai/mistral-nemo` (80%) and `google/gemma-3-27b-it` (85%) — both smaller/older
models. Its failures cluster on `add_note`, `create_contact`, `list_contacts`,
`search_contacts`, and `send_email` (all 40-50% pass), which reads as over-eager tool substitution
within the CRM catalog rather than a capability gap. Meanwhile on `toy_server.py` it had one of
the *best* pass rates (70%). Tool-selection accuracy doesn't track cleanly with general model
quality or recency — it's sensitive to how a specific catalog's descriptions read to that specific
model.

## Second surprising result: a model can be too cautious, not just too confused

`google/gemini-2.5-flash` posted the single lowest score anywhere in the sweep — 21/50 (42%) on
`toy_server.py`, well below every other model on that server. It's not description confusion or
JSON mechanics (0 mechanics failures, per its own Mechanics Floor line): 8 of its 10
`create_reminder` failures are `(no call)` replies where it asked a clarifying question instead of
guessing a time — *"Can you please specify the exact time for the reminder?"* — because
`create_reminder`'s description doesn't state a default. Every other model in the sweep either
had a default behavior for this or guessed; this one asked, every time. A catalog author reading
only the pass-rate column would misdiagnose this as a routing problem; the No-Call Replies section
is what actually explains it — and it's arguably *correct* behavior for a required-but-unstated
argument, which the description could fix by stating what happens when time is omitted.

## Aggregate pass rates (sum of per-tool trials / total trials)

| Model | toy_server (50 trials) | crm_server (80 trials) | ops_server (490 trials) |
|---|---|---|---|
| meta-llama/llama-3.3-70b-instruct | 32/50 (64%) | 55/80 (69%) | 317/490 (65%) |
| qwen/qwen3-32b | 29/50 (58%) | 61/80 (76%) | 418/490 (85%) |
| mistralai/mistral-small-3.2-24b-instruct | 33/50 (66%) | 72/80 (90%) | 427/490 (87%) |
| mistralai/mistral-nemo | 31/50 (62%) | 64/80 (80%) | 407/490 (83%) |
| google/gemma-3-27b-it | 34/50 (68%) | 68/80 (85%) | 373/490 (76%) |
| openai/gpt-4o-mini | 32/50 (64%) | 72/80 (90%) | 430/490 (88%) |
| openai/gpt-4.1-mini | 35/50 (70%) | 47/80 (59%) | 334/490 (68%) |
| deepseek/deepseek-chat-v3-0324 | 33/50 (66%) | 65/80 (81%) | 391/490 (80%) |
| google/gemini-2.5-flash | 21/50 (42%) | 67/80 (84%) | 404/490 (82%) |
| claude-sonnet-5 | 37/50 (74%) | 68/80 (85%) | 397/490 (81%) |

## The P1 demo tool, picked here and since run to completion

`TODOS.md` asked for the tool with the highest wrong/missing count and lowest unparseable count on
a mid-tier model, to demo `--only TOOL --fix-tool TOOL --seeds 40`. From the `ops_server.py` x
`google/gemma-3-27b-it` run (a genuine mid-tier model, not the biggest or smallest in the sweep):

**`set_flag`** — 0/10 pass rate, 0 unparseable, and two parameters failing almost every trial:
`environment_id wrong 10/10`, `enabled missing 10/10`, `rollout_percent missing 7/10` (27 failure
counts across 3 params, the single largest defect signature in the sweep). Its description
("Turn a flag on or off in one environment, optionally for a percentage of users.") never says
`environment_id` and `enabled` are both required, non-optional inputs.

That pick has since been run at `--seeds 40`: **0/40 → 5/40, p=0.0312, ACCEPTED** — the first fix
this project has measured all the way through. Full report:
[`docs/examples/ops-server/report-only-set_flag.md`](examples/ops-server/report-only-set_flag.md).

## Reproducing the sweep

```
bash sweep.sh examples/toy_server.py toy-server
bash sweep.sh examples/crm_server.py crm-server
bash sweep.sh examples/ops_server.py ops-server
```

Each invocation skips any `<model>.md` that already exists and is non-empty, so re-running after
an interruption (rate limit, credit exhaustion, an unrelated process crash) picks up exactly where
it left off.
