## Confusion Matrix

| Intended \ Called | count_tasks | create_reminder | create_task | list_tasks | update_task | (no call) |
|---|---|---|---|---|---|---|
| count_tasks | 0 | 0 | 0 | 10 | 0 | 0 |
| create_reminder | 0 | 10 | 0 | 0 | 0 | 0 |
| create_task | 0 | 0 | 10 | 0 | 0 | 0 |
| list_tasks | 0 | 0 | 0 | 10 | 0 | 0 |
| update_task | 0 | 0 | 0 | 0 | 9 | 1 |

## Trial Diversity
- count_tasks: 3/10 distinct (some seeds sampled identical arguments)
- create_reminder: 10/10 distinct
- create_task: 7/10 distinct (some seeds sampled identical arguments)
- list_tasks: 3/10 distinct (some seeds sampled identical arguments)
- update_task: 7/10 distinct (some seeds sampled identical arguments)

## Pass Rates
- count_tasks: 0/10 (0%), 95% CI [0%, 28%]
- create_reminder: 9/10 (90%), 95% CI [60%, 98%]
- create_task: 5/10 (50%), 95% CI [24%, 76%]
- list_tasks: 8/10 (80%), 95% CI [49%, 94%]
- update_task: 8/10 (80%), 95% CI [49%, 94%]

## Solvability Warnings
- create_task (seed 2, failed, after 2 regeneration(s)): The request asks to create a task with priority set in one step, but there's no single tool that both creates a task and sets its priority simultaneously—create_task and update_task are separate tools, making it unclear which one call would fulfill the request as stated.
- create_task (seed 7, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one is the correct tool to call.
- create_task (seed 9, passed anyway, after 2 regeneration(s)): Both create_task and update_task are described identically as "Add a new task," so it's unclear which single tool should be invoked to create the task with a low priority from the start.
- update_task (seed 7, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically ("Add a new task"), so it's unclear which one actually performs the update operation needed to change task t2's title.
- update_task (seed 9, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically ("Add a new task"), so it's unclear which one actually performs the update operation needed to modify task t2's title.

## Metadata
- Model under test: meta-llama/llama-3.1-8b-instruct
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3

## Proposed Fixes

### create_task — REJECTED
- Before: 'Add a new task.'
- After:  'Creates a brand-new task with a given title and priority, distinct from updating, listing, counting, or reminding existing tasks.'
- Pass rate: 5/10 → 8/10, p-value 0.1875
- Reached via an earlier call: 0/10 → 0/10 (two-sided p=1.0000)
- Reason: rejected: improvement not significant after correction (p=0.188 vs corrected α=0.0100)

### update_task — REJECTED
- Before: 'Add a new task.'
- After:  'Modify the title of an existing task identified by task_id, requiring both task_id and the new title as arguments.'
- Pass rate: 8/10 → 8/10, p-value 0.7500
- Reached via an earlier call: 0/10 → 0/10 (two-sided p=1.0000)
- Reason: rejected: no net change

### list_tasks — REJECTED
- Before: 'Get tasks by status.'
- After:  'Retrieves and lists the full task records matching a given status, unlike count_tasks which only returns a numeric count; requires status.'
- Pass rate: 8/10 → 10/10, p-value 0.2500
- Reached via an earlier call: 0/10 → 0/10 (two-sided p=1.0000)
- Reason: rejected: improvement not significant after correction (p=0.250 vs corrected α=0.0100)

### count_tasks — REJECTED
- Before: 'Get tasks by status.'
- After:  'Return the number of tasks matching a given status, without listing task details; requires the status parameter.'
- Pass rate: 0/10 → 0/10, p-value 1.0000
- Reached via an earlier call: 0/10 → 0/10 (two-sided p=1.0000)
- Reason: rejected: no net change

### create_reminder — REJECTED
- Before: 'Schedule a reminder for an existing task.'
- After:  'Schedules a reminder for an existing task by ID, specifying when to notify, which channels to use, snooze duration, priority, and optional notes.'
- Pass rate: 9/10 → 9/10, p-value 0.7500
- Reached via an earlier call: 0/10 → 0/10 (two-sided p=1.0000)
- Reason: rejected: no net change
