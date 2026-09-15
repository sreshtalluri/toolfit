## Failure Attribution

75/490 trials failed.
- Description confusion: 2 (3%)
- Author-clarifiable arguments: 68 (91%)
- Model output mechanics: 5 (7%)
- Correct deprecated-tool avoidance: 11 (excluded above — the model routed away from a tool the catalog itself says not to use)

## Mechanics Floor

0/490 trial(s) failed for reasons no description edit can change: 0 malformed/duplicated argument JSON, 0 called a tool name that isn't in the catalog.

## Confusion Matrix

| Intended \ Called | acknowledge_alert | add_ticket_note | archive_doc | close_ticket | comment_on_ticket | create_doc | create_flag | create_incident_legacy | create_ticket | deactivate_user | delete_flag | deploy_release | get_config | get_deployment | get_doc | get_flags | get_oncall_schedule | get_secret_v1 | get_ticket | get_user | invite_user | list_alerts | list_deployments | list_environments | list_flags | list_shifts | list_teams | list_tickets | list_users | lookup_user | mute_alert | open_incident | override_oncall | page_oncall | promote_release | read_secret | redeploy_service | resolve_incident | restart_service | rollback_deployment | rotate_secret | search_docs | search_tickets | set_config | set_flag | snooze_alert | update_doc | update_ticket | validate_release | (no call) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| acknowledge_alert | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| add_ticket_note | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| archive_doc | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| close_ticket | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| comment_on_ticket | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_doc | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_flag | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_incident_legacy | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_ticket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| deactivate_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| delete_flag | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| deploy_release | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| get_config | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_deployment | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_doc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| get_flags | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_oncall_schedule | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_secret_v1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| get_ticket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| invite_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| list_alerts | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_deployments | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_environments | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_flags | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_shifts | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_teams | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_tickets | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| list_users | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lookup_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| mute_alert | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| open_incident | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| override_oncall | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| page_oncall | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| promote_release | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| read_secret | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| redeploy_service | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| resolve_incident | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| restart_service | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rollback_deployment | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rotate_secret | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| search_docs | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| search_tickets | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| set_config | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| set_flag | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 1 |
| snooze_alert | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 2 |
| update_doc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| update_ticket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 3 |
| validate_release | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |

## Trial Diversity
- acknowledge_alert: 10/10 distinct
- add_ticket_note: 10/10 distinct
- archive_doc: 10/10 distinct
- close_ticket: 10/10 distinct
- comment_on_ticket: 10/10 distinct
- create_doc: 10/10 distinct
- create_flag: 10/10 distinct
- create_incident_legacy: 8/10 distinct (some seeds sampled identical arguments)
- create_ticket: 10/10 distinct
- deactivate_user: 10/10 distinct
- delete_flag: 10/10 distinct
- deploy_release: 10/10 distinct
- get_config: 10/10 distinct
- get_deployment: 10/10 distinct
- get_doc: 10/10 distinct
- get_flags: 10/10 distinct
- get_oncall_schedule: 10/10 distinct
- get_secret_v1: 10/10 distinct
- get_ticket: 10/10 distinct
- get_user: 10/10 distinct
- invite_user: 10/10 distinct
- list_alerts: 10/10 distinct
- list_deployments: 10/10 distinct
- list_environments: 10/10 distinct
- list_flags: 10/10 distinct
- list_shifts: 10/10 distinct
- list_teams: 3/10 distinct (some seeds sampled identical arguments)
- list_tickets: 10/10 distinct
- list_users: 10/10 distinct
- lookup_user: 10/10 distinct
- mute_alert: 10/10 distinct
- open_incident: 10/10 distinct
- override_oncall: 10/10 distinct
- page_oncall: 10/10 distinct
- promote_release: 10/10 distinct
- read_secret: 10/10 distinct
- redeploy_service: 10/10 distinct
- resolve_incident: 10/10 distinct
- restart_service: 10/10 distinct
- rollback_deployment: 10/10 distinct
- rotate_secret: 10/10 distinct
- search_docs: 10/10 distinct
- search_tickets: 10/10 distinct
- set_config: 10/10 distinct
- set_flag: 10/10 distinct
- snooze_alert: 10/10 distinct
- update_doc: 10/10 distinct
- update_ticket: 10/10 distinct
- validate_release: 10/10 distinct

## Pass Rates
- acknowledge_alert: 10/10 (100%), 95% CI [72%, 100%]
- add_ticket_note: 9/10 (90%), 95% CI [60%, 98%]
- archive_doc: 10/10 (100%), 95% CI [72%, 100%]
- close_ticket: 6/10 (60%), 95% CI [31%, 83%]
- comment_on_ticket: 10/10 (100%), 95% CI [72%, 100%]
- create_doc: 10/10 (100%), 95% CI [72%, 100%]
- create_flag: 8/10 (80%), 95% CI [49%, 94%]
- create_incident_legacy: 7/10 (70%), 95% CI [40%, 89%]
- create_ticket: 10/10 (100%), 95% CI [72%, 100%]
- deactivate_user: 10/10 (100%), 95% CI [72%, 100%]
- delete_flag: 7/10 (70%), 95% CI [40%, 89%]
- deploy_release: 4/10 (40%), 95% CI [17%, 69%]
- get_config: 10/10 (100%), 95% CI [72%, 100%]
- get_deployment: 10/10 (100%), 95% CI [72%, 100%]
- get_doc: 9/10 (90%), 95% CI [60%, 98%]
- get_flags: 10/10 (100%), 95% CI [72%, 100%]
- get_oncall_schedule: 10/10 (100%), 95% CI [72%, 100%]
- get_secret_v1: 1/10 (10%), 95% CI [2%, 40%]
- get_ticket: 10/10 (100%), 95% CI [72%, 100%]
- get_user: 10/10 (100%), 95% CI [72%, 100%]
- invite_user: 8/10 (80%), 95% CI [49%, 94%]
- list_alerts: 5/10 (50%), 95% CI [24%, 76%]
- list_deployments: 10/10 (100%), 95% CI [72%, 100%]
- list_environments: 10/10 (100%), 95% CI [72%, 100%]
- list_flags: 10/10 (100%), 95% CI [72%, 100%]
- list_shifts: 10/10 (100%), 95% CI [72%, 100%]
- list_teams: 6/10 (60%), 95% CI [31%, 83%]
- list_tickets: 3/10 (30%), 95% CI [11%, 60%]
- list_users: 5/10 (50%), 95% CI [24%, 76%]
- lookup_user: 10/10 (100%), 95% CI [72%, 100%]
- mute_alert: 8/10 (80%), 95% CI [49%, 94%]
- open_incident: 6/10 (60%), 95% CI [31%, 83%]
- override_oncall: 0/10 (0%), 95% CI [0%, 28%]
- page_oncall: 10/10 (100%), 95% CI [72%, 100%]
- promote_release: 10/10 (100%), 95% CI [72%, 100%]
- read_secret: 10/10 (100%), 95% CI [72%, 100%]
- redeploy_service: 10/10 (100%), 95% CI [72%, 100%]
- resolve_incident: 10/10 (100%), 95% CI [72%, 100%]
- restart_service: 10/10 (100%), 95% CI [72%, 100%]
- rollback_deployment: 10/10 (100%), 95% CI [72%, 100%]
- rotate_secret: 10/10 (100%), 95% CI [72%, 100%]
- search_docs: 4/10 (40%), 95% CI [17%, 69%]
- search_tickets: 10/10 (100%), 95% CI [72%, 100%]
- set_config: 10/10 (100%), 95% CI [72%, 100%]
- set_flag: 9/10 (90%), 95% CI [60%, 98%]
- snooze_alert: 4/10 (40%), 95% CI [17%, 69%]
- update_doc: 10/10 (100%), 95% CI [72%, 100%]
- update_ticket: 5/10 (50%), 95% CI [24%, 76%]
- validate_release: 10/10 (100%), 95% CI [72%, 100%]

## Preconditions (observed)

Tools the model called *before* correctly calling the intended one, per trial:

- validate_release → promote_release: 10/10 trials

```mermaid
graph LR
  t0["validate_release"]
  t1["promote_release"]
  t0 -->|10/10| t1
```

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- add_ticket_note: body wrong 1/10
- create_flag: default_on extra 2/10
- create_incident_legacy: title wrong 1/10
- deploy_release: window wrong 3/10; window extra 2/10
- invite_user: team_ids wrong 1/10
- list_alerts: page wrong 4/10; page extra 1/10
- list_teams: include_members extra 4/10
- list_tickets: assignee_id extra 1/10; page wrong 1/10; status extra 1/10
- list_users: page wrong 4/10; page extra 1/10
- mute_alert: until wrong 1/10
- open_incident: title wrong 1/10
- override_oncall: window wrong 9/10
- search_docs: page wrong 2/10; query wrong 1/10
- snooze_alert: minutes extra 4/10
- update_ticket: assignee_id extra 2/10

## No-Call Replies

- close_ticket (seed 4, refused): I can't close the ticket as a duplicate without a ticket ID to link it to. Please provide the original ticket ID if you want to close it as a duplicate. Otherwise, I can close it with a different resolution.
- close_ticket (seed 5, asked): What is the ID of the original ticket?
- close_ticket (seed 8, asked): I can do that. What is the ticket ID of the original ticket?
- close_ticket (seed 10, other): I can close ticket `sample-ticket_id-586` as a duplicate of `sample-duplicate_of-212`, but the resolution 'fixed' does not seem appropriate for a duplicate ticket. The available resolutions are: `fixed`, `wont_fix`, `duplicate`, `cannot_re…
- delete_flag (seed 2, refused): I can delete a feature flag, but I can't delete an environment.
- delete_flag (seed 4, refused): I can delete the feature flag entirely, but I can't delete an environment for a feature flag. I can only turn the flag on or off in a given environment.
- delete_flag (seed 5, refused): I am sorry, I cannot fulfill this request. The available tool does not have a function to delete an environment. I can only delete a feature flag from every environment.
- deploy_release (seed 3, asked): What is the maintenance window?
- get_doc (seed 6, asked): I need the document ID of the "Onboarding Checklist" wiki page. Can you please provide it?
- get_secret_v1 (seed 2, asked): Which environment is this for? And what is your justification for accessing it?
- get_secret_v1 (seed 3, refused): I'm sorry, but I cannot fulfill this request. The available tool `get_secret_v1` is deprecated and should not be used. The recommended tool `read_secret` requires a `justification` argument, which means that all secret lookups are logged i…
- get_secret_v1 (seed 4, asked): I need to know the environment ID and a justification for accessing the secret. Can you please provide these?
- get_secret_v1 (seed 5, asked): I need to know the environment the secret is stored in and a justification for audit logging. Can you please provide these?
- get_secret_v1 (seed 6, other): I need to know the environment the secret is stored in and a justification for audit logging.
- get_secret_v1 (seed 7, other): I need to know the environment_id and justification to get the secret.
- get_secret_v1 (seed 8, other): I need to know the environment for which you want the secret, and a justification for accessing it.
- get_secret_v1 (seed 9, asked): I need to know the environment ID and a justification for accessing the secret. Could you please provide these?
- get_secret_v1 (seed 10, refused): I'm sorry, I cannot fulfill this request. The available tool `get_secret_v1` is deprecated and should not be used. The recommended tool `read_secret` requires a `justification` parameter, which means the lookup will always be logged for au…
- invite_user (seed 2, asked): What role should I assign to the new user? What is the team ID?
- list_tickets (seed 2, asked): I can help you with that, but I need more information. What filters are you referring to? Also, there is no option to set the limit of results per page.
- list_tickets (seed 3, refused): I can only list tickets that are 'open', 'in_progress', 'blocked', or 'closed'. I cannot filter by tickets that are unassigned.
- list_tickets (seed 4, other): You can only request up to 100 tickets at a time. Please ask for 100 tickets or less.
- list_tickets (seed 6, asked): What are your current filters?
- mute_alert (seed 10, refused): I cannot snooze an alert until a specific date and time. I can only snooze an alert for a number of minutes from the current time.
- open_incident (seed 8, other): To declare an incident, I need to know the severity. You mentioned "sev2", which is helpful. However, you also mentioned "sample-alert_ids-141" as an alert to link. This doesn't look like a valid alert ID. Alert IDs are typically a string …
- override_oncall (seed 2, asked): I can not set the timezone. The timezone has to be set by the user's client. I can override the on-call for sample-schedule_id-979 by user sample-user_id-884 from 2026-01-29T12:00:00 to 2026-02-16T12:00:00. Would you like me to do that?
- search_docs (seed 4, asked): I can only return up to 100 pages at a time. Would you like me to return 100 pages?
- search_docs (seed 5, other): I can only search for a query within a specific space, not across all of them.
- search_docs (seed 7, asked): I can only return up to 100 results at a time. Do you want to continue with 100 results?
- set_flag (seed 8, refused): I cannot set the rollout percentage for a disabled feature flag. The `rollout_percent` parameter only applies when the `enabled` parameter is set to `true`.
- snooze_alert (seed 2, asked): By "a few minutes", could you please specify the exact number of minutes you'd like to snooze the alert for?
- snooze_alert (seed 6, asked): A few minutes could be 2, 3, or 5. Can you please be more specific?
- update_ticket (seed 3, other): The API does not allow clearing the priority field. It can only be updated with a new value.
- update_ticket (seed 5, asked): I can't clear the title, but I can update it. What would you like to change the title to?
- update_ticket (seed 10, refused): I cannot set the title and assignee to be blank. I can update them, but they need to be provided with a value.

## Solvability Warnings
- get_user (seed 1, passed anyway, after 2 regeneration(s)): 
- get_user (seed 4, passed anyway, after 2 regeneration(s)): 
- get_user (seed 5, passed anyway, after 2 regeneration(s)): 
- get_user (seed 7, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — both `get_user` and `lookup_user` are listed with the identical description "Return user record," giving no basis to determine which one should be used to fetch the "full profile details" for sample-user_id-332.
- get_user (seed 8, passed anyway, after 2 regeneration(s)): 
- get_user (seed 9, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **Classification: AMBIGUOUS**

**Reason:** Both `get_user` and `lookup_user` are described identically ("Return user record") and either could fulfill the request to pull up details for user ID sample-user_id-475, so there's no unambiguous way to determine which single tool the assistant should invoke.
- get_user (seed 10, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 1, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 2, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 3, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 6, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: This request is **SOLVABLE**: The user wants to look up an account by email address, and there are two tools that can directly accomplish this — `get_user` and `lookup_user`, either of which returns a user record given an identifier like an email. Since the user explicitly says "using email address find it," `lookup_user` (or `get_user` with the email as the identifier) can be called with `user813@example.com` to retrieve the account details.
- lookup_user (seed 7, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — both `get_user` and `lookup_user` are described identically as returning a user record, so it's unclear which tool should be called to fulfill the request.
- lookup_user (seed 8, passed anyway, after 2 regeneration(s)): The request itself (look up a user by email) is straightforward, but the toolset provides two functions with identical descriptions—`get_user` ("Return user record") and `lookup_user` ("Return user record")—with no distinguishing information (e.g., one taking an ID vs. an email) to indicate which is the correct one to call for an email-based lookup.
- lookup_user (seed 10, passed anyway, after 2 regeneration(s)): 
- invite_user (seed 10, passed anyway, after 2 regeneration(s)): 
- list_tickets (seed 4, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — `list_tickets` can filter by status=open and be paged through (accumulating results across calls) to return the first 206 matching tickets.
- close_ticket (seed 4, failed, after 2 regeneration(s)): The close_ticket tool requires an original ticket id for duplicate resolutions, but the user explicitly has no such ticket number to provide, creating a conflict between the tool's requirement and the request's constraint.
- close_ticket (seed 5, failed, after 2 regeneration(s)): 
- close_ticket (seed 8, failed, after 2 regeneration(s)): 
- list_deployments (seed 5, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 1, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — the request directly maps to the `get_deployment` tool, which is described as fetching "status, commit, timing" for one deployment given its ID, and the user has supplied that exact deployment ID (`sample-deployment_id-138`).
- get_deployment (seed 2, passed anyway, after 2 regeneration(s)): The request doesn't specify which project (only "our production project"), so there's no way to resolve the correct project/environment ID needed before calling get_deployment on "sample-deployment_id-979".
- get_deployment (seed 4, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 5, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 6, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 7, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 9, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — The request directly maps to the `get_deployment` tool, which is described as fetching "status, commit, timing" for one deployment given its ID; here we simply call `get_deployment` with `deployment_id="sample-deployment_id-475"`.
- get_deployment (seed 10, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — The request can be directly fulfilled with a single call to `get_deployment`, passing the deployment ID `sample-deployment_id-586`, since that tool explicitly returns "status, commit, timing" for one deployment.
- rollback_deployment (seed 2, passed anyway, after 2 regeneration(s)): 
- rollback_deployment (seed 6, passed anyway, after 2 regeneration(s)): 
- list_alerts (seed 4, passed anyway, after 2 regeneration(s)): 
- list_alerts (seed 5, passed anyway, after 2 regeneration(s)): 
- list_alerts (seed 10, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** – None of the available tools can retrieve or list alert IDs for a service; there's no `list_alerts`/`get_alerts` (or similar) function, only `snooze_alert`, which requires an existing alert ID rather than providing one.
- acknowledge_alert (seed 2, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: 
- acknowledge_alert (seed 3, passed anyway, after 2 regeneration(s)): 
- acknowledge_alert (seed 5, passed anyway, after 2 regeneration(s)): 
- snooze_alert (seed 6, failed, after 2 regeneration(s)): 
- open_incident (seed 1, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — the request maps directly onto the `open_incident` tool, which can declare an incident with a given title and severity (sev3), regardless of how unusual or joke-like the title itself is.
- open_incident (seed 3, failed, after 2 regeneration(s)): 
- open_incident (seed 5, passed anyway, after 2 regeneration(s)): 
- open_incident (seed 8, failed, after 2 regeneration(s)): 
- open_incident (seed 9, passed anyway, after 2 regeneration(s)): 
- create_incident_legacy (seed 2, failed, after 2 regeneration(s)): 
- create_incident_legacy (seed 3, passed anyway, after 2 regeneration(s)): 
- create_incident_legacy (seed 9, passed anyway, after 2 regeneration(s)): Neither open_incident nor create_incident_legacy exposes a documented "severity" parameter, so there's no clear way to explicitly set the incident's severity to sev3 as requested.
- search_docs (seed 8, failed, after 2 regeneration(s)): 
- update_doc (seed 3, passed anyway, after 2 regeneration(s)): 
- delete_flag (seed 2, failed, after 2 regeneration(s)): There is no listed tool for deleting an environment key/secret (only read_secret, rotate_secret, and delete_flag for feature flags exist), so the requested "permanent deletion" action cannot be mapped to any available tool.
- delete_flag (seed 4, failed, after 2 regeneration(s)): No available tool deletes a single environment key from a feature flag—delete_flag removes the entire flag across all environments, which is a different, broader action than what was requested.
- delete_flag (seed 5, failed, after 2 regeneration(s)): No available tool supports permanently deleting an environment key/secret/config value — only rotate_secret, set_config, or delete_flag exist, none of which match "delete environment key," leaving the correct action unclear.
- get_secret_v1 (seed 10, failed, after 2 regeneration(s)): The only way to fetch a secret without an audit-log entry would be the deprecated `get_secret_v1`, but deliberately bypassing the audit trail conflicts with security policy, so I can't honor the "without logging" condition — I can retrieve it via `read_secret` (which will record a justified audit entry) if that's acceptable.
- rotate_secret (seed 3, passed anyway, after 2 regeneration(s)): There is no tool to determine which services depend on the given secret/service, so the "redeploy dependent services" step cannot be resolved with the available tools.
- rotate_secret (seed 9, passed anyway, after 2 regeneration(s)): The request requires identifying which services use the secret and who its "owner" is, but no tool exists to look up secret ownership or dependent services for redeployment/notification.
- rotate_secret (seed 10, passed anyway, after 2 regeneration(s)): Fulfilling this requires multiple discrete actions (rotating/generating the secret, identifying and redeploying dependent services, then notifying the owner), and there's no single tool that performs secret rotation or owner notification, so it can't be done with one call.

## Metadata
- Model under test: google/gemini-2.5-flash
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3
