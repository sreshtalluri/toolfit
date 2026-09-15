## Failure Attribution

29/50 trials failed.
- Description confusion: 10 (34%)
- Author-clarifiable arguments: 19 (66%)
- Model output mechanics: 0 (0%)

## Mechanics Floor

0/50 trial(s) failed for reasons no description edit can change: 0 malformed/duplicated argument JSON, 0 called a tool name that isn't in the catalog.

## Confusion Matrix

| Intended \ Called | count_tasks | create_reminder | create_task | list_tasks | update_task | (no call) |
|---|---|---|---|---|---|---|
| count_tasks | 0 | 0 | 0 | 10 | 0 | 0 |
| create_reminder | 0 | 2 | 0 | 0 | 0 | 8 |
| create_task | 0 | 0 | 10 | 0 | 0 | 0 |
| list_tasks | 0 | 0 | 0 | 9 | 0 | 1 |
| update_task | 0 | 0 | 0 | 0 | 10 | 0 |

## Trial Diversity
- count_tasks: 3/10 distinct (some seeds sampled identical arguments)
- create_reminder: 10/10 distinct
- create_task: 8/10 distinct (some seeds sampled identical arguments)
- list_tasks: 3/10 distinct (some seeds sampled identical arguments)
- update_task: 9/10 distinct (some seeds sampled identical arguments)

## Pass Rates
- count_tasks: 0/10 (0%), 95% CI [0%, 28%]
- create_reminder: 1/10 (10%), 95% CI [2%, 40%]
- create_task: 5/10 (50%), 95% CI [24%, 76%]
- list_tasks: 7/10 (70%), 95% CI [40%, 89%]
- update_task: 8/10 (80%), 95% CI [49%, 94%]

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- create_reminder: notes wrong 1/10
- create_task: title wrong 5/10
- list_tasks: status wrong 2/10
- update_task: title wrong 2/10

## No-Call Replies

- create_reminder (seed 1, asked): I can do that. What time would you like to be reminded?
- create_reminder (seed 2, asked): Can you please specify the time for the reminder?
- create_reminder (seed 3, asked): I can do that. What would you like the reminder message to say?
- create_reminder (seed 4, asked): ToSnooze: 51 minutes is a long snooze. Are you sure you want to snooze for that long?
- create_reminder (seed 5, asked): I can do that. Could you please specify the exact time on 2026-05-11 when you'd like to be reminded?
- create_reminder (seed 8, asked): I can help with that, but I need to know the exact time to set the reminder. Could you please provide the time?
- create_reminder (seed 9, asked): Can you please specify the exact time for the reminder?
- create_reminder (seed 10, asked): I can help with that. What time should I set the reminder for?
- list_tasks (seed 1, refused): I can only provide a list of tasks based on their status. I cannot provide additional details for each task beyond the task ID and title.

## Solvability Warnings
- create_task (seed 2, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," making it impossible to determine which one the assistant should call.
- create_task (seed 6, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one is intended for creating this new task.
- create_task (seed 10, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one is intended for creating this new task.
- update_task (seed 5, passed anyway, after 2 regeneration(s)): There are two tools ("update_task" and "create_task", both described identically as "Add a new task") so it's unclear which one actually performs the update operation requested.
- update_task (seed 6, passed anyway, after 2 regeneration(s)): Both "update_task" and "create_task" are described identically ("Add a new task."), so it's unclear which tool actually performs an update to an existing task's title.
- update_task (seed 7, passed anyway, after 2 regeneration(s)): Both create_task and update_task share the identical description "Add a new task," so despite its name, it's unclear that update_task actually supports modifying an existing task's title.
- update_task (seed 8, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically ("Add a new task"), so it's unclear which tool actually performs the update operation needed to change task t2's title.
- update_task (seed 10, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear from the tool list which one actually performs an update to an existing task's title.

## Metadata
- Model under test: google/gemini-2.5-flash
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3
