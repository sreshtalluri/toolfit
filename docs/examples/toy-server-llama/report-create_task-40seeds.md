## Confusion Matrix

| Intended \ Called | create_task |
|---|---|
| create_task | 40 |

## Trial Diversity
- create_task: 27/40 distinct (some seeds sampled identical arguments)

## Pass Rates
- create_task: 15/40 (38%), 95% CI [24%, 53%]

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* unparseable` = the argument JSON could not be parsed.

- create_task: * unparseable 18/40; title wrong 7/40

## Solvability Warnings
- create_task (seed 2, passed anyway, after 2 regeneration(s)): The request asks to create a task with priority set in one step, but there's no single tool that both creates a task and sets its priority simultaneously—create_task and update_task are separate tools, making it unclear which one call would fulfill the request as stated.
- create_task (seed 4, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one is meant to be called.
- create_task (seed 6, passed anyway, after 2 regeneration(s)): Both create_task and update_task share the identical description "Add a new task," so it's unclear which single tool call would both create the task and set its priority from the start.
- create_task (seed 7, failed, after 2 regeneration(s)): The request requires both creating a task and setting its priority simultaneously, but create_task and update_task both plausibly handle setting the title with priority, making it unclear whether one call (create_task with priority included) or two calls (create_task then update_task) are needed.
- create_task (seed 8, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one is meant to be called.
- create_task (seed 10, failed, after 2 regeneration(s)): Both create_task and update_task share the identical description "Add a new task," so it's unclear which single tool call would both create the task and set its priority from the start.
- create_task (seed 14, failed, after 2 regeneration(s)): Both create_task and update_task are described identically as "Add a new task," so it's unclear which single tool should be invoked to create the task with a low priority from the start.
- create_task (seed 19, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one the assistant should invoke.
- create_task (seed 20, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one should be used to add the new task.
- create_task (seed 23, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one the assistant should call.
- create_task (seed 24, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," making it unclear which single tool should be called to create the task with a set priority.
- create_task (seed 25, passed anyway, after 2 regeneration(s)): create_task and update_task have the identical description "Add a new task," so it's unclear which one the assistant should call to create the new task.
- create_task (seed 28, passed anyway, after 2 regeneration(s)): Both create_task and update_task are described identically as "Add a new task," so it's unclear which single tool should be invoked to create the task with a low priority from the start.
- create_task (seed 32, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one is the correct tool to call.
- create_task (seed 33, failed, after 2 regeneration(s)): Both create_task and update_task share the identical description "Add a new task," so it's unclear which single tool call would both create the task and set its priority from the start.
- create_task (seed 36, failed, after 2 regeneration(s)): The request requires both creating a task and setting its priority simultaneously, but create_task and update_task both plausibly handle setting the title with priority, making it unclear whether one call (create_task with priority included) or two calls (create_task then update_task) are needed.
- create_task (seed 39, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one is meant to be called.

## Metadata
- Model under test: meta-llama/llama-3.1-8b-instruct
- Generator model: claude-sonnet-5
- Seeds per tool: 40
- Max steps per task: 3
- Tools evaluated (--only): create_task — the model was offered the whole catalog (5 tools) on every call

## Proposed Fixes

### create_task — REJECTED
- Before: 'Add a new task.'
- After:  'Creates a brand-new task with a given title and priority, distinct from updating, listing, counting, or reminding existing tasks.'
- Pass rate: 15/40 → 20/40, p-value 0.1133
- Reached via an earlier call: 0/40 → 0/40 (two-sided p=1.0000)
- Reason: rejected: improvement not significant after correction (p=0.113 vs corrected α=0.0500)
