## Failure Attribution

13/50 trials failed.
- Description confusion: 10 (77%)
- Author-clarifiable arguments: 3 (23%)
- Model output mechanics: 0 (0%)

## Mechanics Floor

0/50 trial(s) failed for reasons no description edit can change: 0 malformed/duplicated argument JSON, 0 called a tool name that isn't in the catalog.

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
- create_task: 9/10 (90%), 95% CI [60%, 98%]
- list_tasks: 10/10 (100%), 95% CI [72%, 100%]
- update_task: 9/10 (90%), 95% CI [60%, 98%]

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- create_reminder: notes wrong 1/10
- create_task: title wrong 1/10
- update_task: title wrong 1/10

## Solvability Warnings
- create_task (seed 2, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically ("Add a new task"), so it's unclear which one the assistant should call.
- create_task (seed 5, passed anyway, after 2 regeneration(s)): create_task and update_task share the identical description "Add a new task," so it isn't clear which single tool actually creates the task versus sets its priority.
- create_task (seed 6, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one is intended for adding a new task.
- create_task (seed 10, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one is intended for adding a new task.
- update_task (seed 4, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," making it unclear which one actually performs an update operation on an existing task.
- update_task (seed 6, passed anyway, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one actually performs an update operation.
- update_task (seed 7, passed anyway, after 2 regeneration(s)): Both "update_task" and "create_task" are described identically ("Add a new task"), so it's unclear which tool actually performs an update to an existing task's title.
- update_task (seed 8, failed, after 2 regeneration(s)): Both "create_task" and "update_task" are described identically as "Add a new task," so it's unclear which one actually performs the update operation needed to change task t2's title.

## Metadata
- Model under test: claude-sonnet-5
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3
