## Failure Attribution

40/40 trials failed.
- Description confusion: 0 (0%)
- Author-clarifiable arguments: 40 (100%)
- Model output mechanics: 0 (0%)

## Mechanics Floor

0/40 trial(s) failed for reasons no description edit can change: 0 malformed/duplicated argument JSON, 0 called a tool name that isn't in the catalog.

## Confusion Matrix

| Intended \ Called | set_flag |
|---|---|
| set_flag | 40 |

## Trial Diversity
- set_flag: 40/40 distinct

## Pass Rates
- set_flag: 0/40 (0%), 95% CI [0%, 9%]

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- set_flag: enabled missing 40/40; environment_id wrong 36/40; rollout_percent missing 25/40; environment_id missing 4/40; key wrong 3/40; project_id wrong 1/40; key missing 1/40

## Solvability Warnings
- set_flag (seed 12, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: 

## Metadata
- Model under test: google/gemma-3-27b-it
- Generator model: claude-sonnet-5
- Seeds per tool: 40
- Max steps per task: 3
- Tools evaluated (--only): set_flag — the model was offered the whole catalog (49 tools) on every call

## Proposed Fixes

### set_flag — ACCEPTED
- Before: 'Turn a flag on or off in one environment, optionally for a percentage of users.'
- After:  "Toggle an existing feature flag's enabled state in a specific environment for a project, optionally rolling out to a percentage of users. Distinct from create_flag (makes a new flag) and set_config (sets non-flag service configuration)."
- Pass rate: 0/40 → 5/40, p-value 0.0312
- Reached via an earlier call: 0/40 → 0/40 (two-sided p=1.0000)
- Reason: accepted
