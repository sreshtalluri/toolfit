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
- create_task: 8/10 distinct (some seeds sampled identical arguments)
- list_tasks: 3/10 distinct (some seeds sampled identical arguments)
- update_task: 9/10 distinct (some seeds sampled identical arguments)

## Pass Rates
- count_tasks: 0/10 (0%), 95% CI [0%, 28%]
- create_reminder: 9/10 (90%), 95% CI [60%, 98%]
- create_task: 7/10 (70%), 95% CI [40%, 89%]
- list_tasks: 9/10 (90%), 95% CI [60%, 98%]
- update_task: 8/10 (80%), 95% CI [49%, 94%]

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- create_reminder: notes wrong 1/10
- create_task: title wrong 3/10
- list_tasks: status wrong 1/10
- update_task: title wrong 2/10

## Solvability Warnings
- create_task (seed 2, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," making it unclear which one the assistant should call.
- create_task (seed 3, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" share the identical description "Add a new task," making it unclear which one is meant for adding a new task.
- create_task (seed 5, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear from the tool list which one is meant for creating a brand-new task.
- create_task (seed 6, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as tools to "Add a new task," making it unclear which one the assistant should call.
- create_task (seed 7, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," making it unclear which one to call.
- create_task (seed 10, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as tools to "Add a new task," making it unclear which one the assistant should call.
- update_task (seed 1, passed anyway, after 2 regeneration(s)): There are two tools with identical descriptions ("Add a new task") — create_task and update_task — so it's unclear which one actually performs the update-title functionality being requested.
- update_task (seed 3, passed anyway, after 2 regeneration(s)): There are two tools with identical descriptions ("Add a new task") — create_task and update_task — so it's unclear which one actually performs the update-title functionality being requested.
- update_task (seed 5, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" have identical descriptions ("Add a new task"), so it's unclear which tool actually performs an update to an existing task's title.
- update_task (seed 6, passed anyway, after 2 regeneration(s)): Both "update_task" and "create_task" are described identically as "Add a new task," so it's unclear which tool actually performs an update versus a creation.
- update_task (seed 10, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so based solely on their descriptions it's unclear which tool actually performs an update to an existing task's title.

## Metadata
- Model under test: deepseek/deepseek-chat-v3-0324
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3
