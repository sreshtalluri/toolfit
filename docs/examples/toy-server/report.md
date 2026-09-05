## Confusion Matrix

| Intended \ Called | count_tasks | create_reminder | create_task | list_tasks | update_task |
|---|---|---|---|---|---|
| count_tasks | 0 | 0 | 0 | 10 | 0 |
| create_reminder | 0 | 10 | 0 | 0 | 0 |
| create_task | 0 | 0 | 10 | 0 | 0 |
| list_tasks | 0 | 0 | 0 | 10 | 0 |
| update_task | 0 | 0 | 0 | 0 | 10 |

## Trial Diversity
- count_tasks: 3/10 distinct (some seeds sampled identical arguments)
- create_reminder: 10/10 distinct
- create_task: 7/10 distinct (some seeds sampled identical arguments)
- list_tasks: 3/10 distinct (some seeds sampled identical arguments)
- update_task: 7/10 distinct (some seeds sampled identical arguments)

## Pass Rates
- count_tasks: 0/10 (0%), 95% CI [0%, 28%]
- create_reminder: 8/10 (80%), 95% CI [49%, 94%]
- create_task: 9/10 (90%), 95% CI [60%, 98%]
- list_tasks: 10/10 (100%), 95% CI [72%, 100%]
- update_task: 10/10 (100%), 95% CI [72%, 100%]

## Solvability Warnings
- create_task (seed 1): There are two tools ("create_task" and "update_task") whose descriptions are both "Add a new task," so it's unclear which one is meant for adding this new task.
- create_task (seed 2): Both "create_task" and "update_task" are described identically as "Add a new task," making it unclear which one the assistant should call.
- create_task (seed 3): There are two tools ("create_task" and "update_task") whose descriptions are both "Add a new task," so it's unclear which one is meant for adding this new task.
- create_task (seed 4): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one the assistant should call.
- create_task (seed 5): The request requires two sequential actions (create_task then update_task to set priority), so it's not clear which ONE tool to call.
- create_task (seed 6): Both "create_task" and "update_task" are described identically ("Add a new task"), so it's unclear which one is intended for adding the dentist appointment task.
- create_task (seed 8): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one the assistant should call.
- create_task (seed 9): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one the assistant should call to add the new task.
- create_task (seed 10): Both "create_task" and "update_task" are described identically ("Add a new task"), so it's unclear which one is intended for adding the dentist appointment task.
- update_task (seed 2): Both "update_task" and "create_task" are described identically ("Add a new task"), so it's unclear which tool actually performs the update operation requested.
- update_task (seed 6): Both "create_task" and "update_task" are described identically as "Add a new task," so the tool list itself doesn't clarify which one actually performs an update operation.
- update_task (seed 7): Both "create_task" and "update_task" share the identical description "Add a new task," so there is no clear tool description indicating which one modifies an existing task's title.
- update_task (seed 10): Both "create_task" and "update_task" are described identically as "Add a new task," so the tool list itself doesn't clarify which one actually performs an update operation.
- create_reminder (seed 4): The request asks to both create a reminder (via create_reminder) and add a note about snacks, which isn't supported by create_reminder alone and would require another tool call (e.g., update_task) to record the note, so it's unclear if a single tool call suffices.
- create_reminder (seed 7): The request contains a self-contradiction (priority stated as "high" but note says "Low priority") and includes conflicting/unclear parameters, making it unclear how to correctly populate the single create_reminder call.

## Metadata
- Model under test: claude-sonnet-5
- Generator model: claude-sonnet-5
- Seeds per tool: 10

## Proposed Fixes

### create_task — REJECTED
- Before: 'Add a new task.'
- After:  'Creates a brand-new task by specifying its title and priority, distinct from update_task (which modifies existing tasks) or create_reminder (which schedules reminders for tasks that already exist).'
- Pass rate: 9/10 → 7/10, p-value 1.0000
- Reason: rejected: made things worse

### count_tasks — REJECTED
- Before: 'Get tasks by status.'
- After:  'Return the number of tasks matching a given status, rather than the tasks themselves, by accepting a required status argument.'
- Pass rate: 0/10 → 0/10, p-value 1.0000
- Reason: rejected: no change

### create_reminder — REJECTED
- Before: 'Schedule a reminder for an existing task.'
- After:  'Schedule a reminder (with a required remind_at time, notify_channels list, snooze_minutes, and priority of low/medium/high, plus optional notes) for an already-existing task identified by task_id, rather than creating, updating, listing, or counting tasks themselves.'
- Pass rate: 8/10 → 8/10, p-value 1.0000
- Reason: rejected: no change
