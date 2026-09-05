## Confusion Matrix

| Intended \ Called | add_observations | create_entities | create_relations | delete_entities | delete_observations | delete_relations | open_nodes | read_graph | search_nodes |
|---|---|---|---|---|---|---|---|---|---|
| add_observations | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_entities | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_relations | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| delete_entities | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 |
| delete_observations | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 |
| delete_relations | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| open_nodes | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 |
| read_graph | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| search_nodes | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 |

## Trial Diversity
- add_observations: 10/10 distinct
- create_entities: 10/10 distinct
- create_relations: 10/10 distinct
- delete_entities: 10/10 distinct
- delete_observations: 10/10 distinct
- delete_relations: 10/10 distinct
- open_nodes: 10/10 distinct
- read_graph: 1/10 distinct (some seeds sampled identical arguments)
- search_nodes: 10/10 distinct

## Pass Rates
- add_observations: 10/10 (100%), 95% CI [72%, 100%]
- create_entities: 10/10 (100%), 95% CI [72%, 100%]
- create_relations: 10/10 (100%), 95% CI [72%, 100%]
- delete_entities: 10/10 (100%), 95% CI [72%, 100%]
- delete_observations: 10/10 (100%), 95% CI [72%, 100%]
- delete_relations: 10/10 (100%), 95% CI [72%, 100%]
- open_nodes: 10/10 (100%), 95% CI [72%, 100%]
- read_graph: 10/10 (100%), 95% CI [72%, 100%]
- search_nodes: 10/10 (100%), 95% CI [72%, 100%]

## Metadata
- Model under test: claude-sonnet-5
- Generator model: claude-sonnet-5
- Seeds per tool: 10

## Proposed Fixes

No tool had a failed trial, so nothing to fix.
