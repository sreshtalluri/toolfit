## Failure Attribution

73/490 trials failed.
- Description confusion: 1 (1%)
- Author-clarifiable arguments: 48 (66%)
- Model output mechanics: 24 (33%)
- Correct deprecated-tool avoidance: 20 (excluded above — the model routed away from a tool the catalog itself says not to use)

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
| create_incident_legacy | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_ticket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| deactivate_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| delete_flag | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| deploy_release | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| get_config | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_deployment | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_doc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_flags | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_oncall_schedule | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_secret_v1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 |
| get_ticket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| invite_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| list_alerts | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_deployments | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_environments | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| list_flags | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_shifts | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_teams | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| list_tickets | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 |
| list_users | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| lookup_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| mute_alert | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| open_incident | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| override_oncall | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| page_oncall | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| promote_release | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| read_secret | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| redeploy_service | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| resolve_incident | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| restart_service | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rollback_deployment | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rotate_secret | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| search_docs | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| search_tickets | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| set_config | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 1 |
| set_flag | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 |
| snooze_alert | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 6 |
| update_doc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| update_ticket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 3 |
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
- add_ticket_note: 8/10 (80%), 95% CI [49%, 94%]
- archive_doc: 10/10 (100%), 95% CI [72%, 100%]
- close_ticket: 6/10 (60%), 95% CI [31%, 83%]
- comment_on_ticket: 10/10 (100%), 95% CI [72%, 100%]
- create_doc: 9/10 (90%), 95% CI [60%, 98%]
- create_flag: 7/10 (70%), 95% CI [40%, 89%]
- create_incident_legacy: 0/10 (0%), 95% CI [0%, 28%]
- create_ticket: 8/10 (80%), 95% CI [49%, 94%]
- deactivate_user: 10/10 (100%), 95% CI [72%, 100%]
- delete_flag: 6/10 (60%), 95% CI [31%, 83%]
- deploy_release: 7/10 (70%), 95% CI [40%, 89%]
- get_config: 10/10 (100%), 95% CI [72%, 100%]
- get_deployment: 10/10 (100%), 95% CI [72%, 100%]
- get_doc: 10/10 (100%), 95% CI [72%, 100%]
- get_flags: 10/10 (100%), 95% CI [72%, 100%]
- get_oncall_schedule: 10/10 (100%), 95% CI [72%, 100%]
- get_secret_v1: 0/10 (0%), 95% CI [0%, 28%]
- get_ticket: 10/10 (100%), 95% CI [72%, 100%]
- get_user: 10/10 (100%), 95% CI [72%, 100%]
- invite_user: 9/10 (90%), 95% CI [60%, 98%]
- list_alerts: 7/10 (70%), 95% CI [40%, 89%]
- list_deployments: 10/10 (100%), 95% CI [72%, 100%]
- list_environments: 9/10 (90%), 95% CI [60%, 98%]
- list_flags: 10/10 (100%), 95% CI [72%, 100%]
- list_shifts: 10/10 (100%), 95% CI [72%, 100%]
- list_teams: 6/10 (60%), 95% CI [31%, 83%]
- list_tickets: 1/10 (10%), 95% CI [2%, 40%]
- list_users: 6/10 (60%), 95% CI [31%, 83%]
- lookup_user: 9/10 (90%), 95% CI [60%, 98%]
- mute_alert: 10/10 (100%), 95% CI [72%, 100%]
- open_incident: 9/10 (90%), 95% CI [60%, 98%]
- override_oncall: 7/10 (70%), 95% CI [40%, 89%]
- page_oncall: 7/10 (70%), 95% CI [40%, 89%]
- promote_release: 10/10 (100%), 95% CI [72%, 100%]
- read_secret: 10/10 (100%), 95% CI [72%, 100%]
- redeploy_service: 10/10 (100%), 95% CI [72%, 100%]
- resolve_incident: 8/10 (80%), 95% CI [49%, 94%]
- restart_service: 10/10 (100%), 95% CI [72%, 100%]
- rollback_deployment: 10/10 (100%), 95% CI [72%, 100%]
- rotate_secret: 10/10 (100%), 95% CI [72%, 100%]
- search_docs: 9/10 (90%), 95% CI [60%, 98%]
- search_tickets: 3/10 (30%), 95% CI [11%, 60%]
- set_config: 9/10 (90%), 95% CI [60%, 98%]
- set_flag: 10/10 (100%), 95% CI [72%, 100%]
- snooze_alert: 0/10 (0%), 95% CI [0%, 28%]
- update_doc: 10/10 (100%), 95% CI [72%, 100%]
- update_ticket: 7/10 (70%), 95% CI [40%, 89%]
- validate_release: 10/10 (100%), 95% CI [72%, 100%]

## Preconditions (observed)

Tools the model called *before* correctly calling the intended one, per trial:

- validate_release → promote_release: 10/10 trials
- get_ticket → update_ticket: 1/10 trials

```mermaid
graph LR
  t0["validate_release"]
  t1["promote_release"]
  t2["get_ticket"]
  t3["update_ticket"]
  t0 -->|10/10| t1
  t2 -->|1/10| t3
```

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- add_ticket_note: body wrong 2/10
- create_doc: title wrong 1/10
- create_flag: default_on extra 3/10
- create_ticket: labels extra 2/10
- deploy_release: window wrong 1/10
- list_alerts: page missing 1/10; page wrong 1/10; page extra 1/10
- list_teams: include_members extra 4/10
- list_tickets: page wrong 1/10
- list_users: page wrong 2/10; page extra 2/10
- open_incident: title wrong 1/10
- override_oncall: window wrong 3/10
- page_oncall: urgency extra 1/10
- resolve_incident: summary wrong 2/10
- search_docs: page missing 1/10
- snooze_alert: minutes extra 3/10

## No-Call Replies

- close_ticket (seed 5, refused): I can't complete this request as stated — you're asking me to close ticket `sample-ticket_id-638` as a duplicate **of itself** (the same ticket ID: `sample-ticket_id-638`). A ticket can't be a duplicate of itself, so this looks like a mist…
- close_ticket (seed 7, refused): I noticed a conflict in your request: the `close_ticket` tool only supports one resolution at a time, and `duplicate_of` is meant to be used specifically with the **"duplicate"** resolution (not "won't fix"). So I can't set both "won't fix…
- close_ticket (seed 8, refused): I want to flag an issue with this request before proceeding: you've asked me to close ticket **sample-ticket_id-233** as a duplicate **of itself** (sample-ticket_id-233). A ticket can't logically be marked as a duplicate of itself — that w…
- close_ticket (seed 10, other): I want to make sure I set this up correctly before closing the ticket — there's a slight conflict in the request. The `close_ticket` tool treats "duplicate" as its own resolution type (paired with a `duplicate_of` reference), separate from…
- delete_flag (seed 1, other): I searched the available tools, and there isn't one designed to delete an "environment key" from a project. Here's what I found instead: - **`delete_flag`** — permanently deletes a *feature flag* from every environment in a project. - **`s…
- delete_flag (seed 2, other): I searched the available tools and could not find a function that deletes an "environment key" specifically. The only deletion-related tool available is `delete_flag`, which permanently deletes a **feature flag** (not an environment key) f…
- delete_flag (seed 5, refused): I don't have a tool to delete an "environment key" (e.g., an SDK/API key for an environment) in a feature flag project. The tools available to me only allow: - Creating/deleting **feature flags** (`create_flag`, `delete_flag`) - Listing fl…
- delete_flag (seed 9, other): No tool exists in this system for deleting an environment (or an environment key) from feature flag settings. The only deletion capability available is `delete_flag`, which permanently removes an entire **feature flag** (across all environ…
- deploy_release (seed 3, refused): I don't have a tool that can look up a specific maintenance window schedule for an environment (only `list_environments`/`list_deployments`, which don't expose window timing, and `deploy_release`, which lets me *specify* a window but doesn…
- deploy_release (seed 5, other): I checked the available tools, and there isn't a way for me to look up or verify a scheduled maintenance window for an environment — the tools I have (`deploy_release`, `list_deployments`, `list_environments`, `get_oncall_schedule`, `list_…
- get_secret_v1 (seed 1, refused): I can retrieve that secret, but I should use the current, audited method (`read_secret`) rather than the deprecated `get_secret_v1` tool, since that one bypasses audit logging. To do that, I need two more pieces of information from you: 1.…
- get_secret_v1 (seed 2, other): I can retrieve that secret for you, but the recommended method (`read_secret`) requires two additional pieces of information that weren't provided: 1. **Environment ID** – which environment (e.g., `production`, `staging`) the secret belong…
- get_secret_v1 (seed 3, other): I can retrieve that using the current recommended `read_secret` tool, but I need two more pieces of information since it requires them (and logs the access for audit purposes): 1. **Environment ID** — which environment is this secret in (e…
- get_secret_v1 (seed 4, refused): I found the right tool for this — but I should use `read_secret` (the current, audited method) rather than the deprecated `get_secret_v1`, which skips audit logging. To fetch the secret, I need two more things: 1. **Environment ID** — whic…
- get_secret_v1 (seed 5, other): I can help retrieve that secret. Since the recommended method (`read_secret`) requires an environment ID and a justification for audit logging purposes, could you please provide: 1. **Environment ID** (e.g., production, staging, or its spe…
- get_secret_v1 (seed 6, other): I can retrieve that secret using the `read_secret` tool, but it requires two more pieces of information that weren't provided: 1. **Environment ID** – which environment (e.g., production, staging) the secret should be read from. 2. **Justi…
- get_secret_v1 (seed 7, refused): I can fetch that for you, but I'll use the current `read_secret` tool rather than the deprecated `get_secret_v1` (which skips audit logging). To do that, I need two more things: 1. **Environment ID** — which environment is this secret in (…
- get_secret_v1 (seed 8, refused): I can retrieve that using the `read_secret` tool, which properly logs the access for auditing purposes (there's also a deprecated `get_secret_v1` that skips logging, but I'll avoid using that). To proceed, I need two more pieces of informa…
- get_secret_v1 (seed 9, other): I can retrieve that secret using the recommended `read_secret` tool, but it requires two additional pieces of information that you haven't provided yet: 1. **environment_id** – which environment (e.g., production, staging) the secret belon…
- get_secret_v1 (seed 10, refused): I can retrieve the secret, but I won't use the no-logging path to skip the audit trail — that's there for security/compliance reasons (e.g., tracking who accessed sensitive credentials and when), and deliberately bypassing it isn't somethi…
- invite_user (seed 2, asked): I found the right tool to send this invitation, but I need a couple more details before I can proceed since the role and team aren't specified in your message: 1. **Role** — should it be `admin`, `engineer`, or `viewer`? (defaults to `engi…
- list_environments (seed 1, other): No tool exists in this system to list or look up environment IDs for a project (e.g., staging/production) by project ID. The available tools (`deploy_release`, `list_deployments`, `get_config`, `get_flags`, `list_alerts`, etc.) all *requir…
- list_tickets (seed 1, other): I checked the available tools, and unfortunately there isn't a tool that lets me list or search across all tickets (e.g., "all open tickets" or "filter by assignee"). The ticket-related tools I have access to are limited to: - **get_ticket…
- list_tickets (seed 2, other): No ticket-search/listing tool exists in the available toolset—only `get_ticket` (fetch by ID), `create_ticket`, `close_ticket`, `comment_on_ticket`, and `add_ticket_note` are available. There's no tool to list/browse tickets by filters, so…
- list_tickets (seed 3, other): I wasn't able to find a tool that lists or searches tickets by status/assignee — the only ticket-related tools available are `get_ticket` (fetch by a specific ID), `create_ticket`, `close_ticket`, `comment_on_ticket`, and `add_ticket_note`…
- list_tickets (seed 5, other): No, there isn't a "list all tickets" tool available. The tools I have access to only let me: - **Fetch a single ticket by ID** (`get_ticket`) - Create, close, comment on, or add notes to tickets There's no bulk search/list tool that return…
- list_tickets (seed 6, asked): I don't have any filters saved from earlier in our conversation — could you tell me what you'd like to filter by? For example: - **Status**: open, in_progress, blocked, or closed (default is "open") - **Assignee**: a specific assignee ID, …
- list_tickets (seed 7, other): No tool exists for listing or searching tickets by assignee/status—I only have access to functions for creating a ticket, fetching a single ticket by ID, adding notes/comments, and closing tickets. There isn't a search/list capability to q…
- list_tickets (seed 9, refused): I don't have a tool that can search or list tickets by status/assignee. The available ticket tools only let me: - Fetch a **specific** ticket by ID (`get_ticket`) - Create, close, or comment on a ticket - Add a private note There's no "lis…
- list_tickets (seed 10, refused): I don't have a tool that can search or list tickets by assignee — the only ticket-related tools available to me are: - `create_ticket` – open a new ticket - `get_ticket` – fetch a single ticket by its specific ticket ID - `comment_on_ticke…
- lookup_user (seed 5, refused): I don't have access to any tools or systems that store user account data, so I'm not able to look up account details for user638@example.com or any other email address. I have no connection to a database, CRM, or authentication system. A f…
- page_oncall (seed 1, other): No tool exists in this system to page an on-call responder directly. The available tools only let me look up on-call schedules (`get_oncall_schedule`, which requires a *team_id*, not a schedule ID) and manage alerts/incidents/tickets/docs …
- page_oncall (seed 10, other): No paging tool exists in the available toolset. I searched thoroughly (for "on-call/schedule/page", "notify/alert/trigger/incident/urgent", and "page" specifically) and the only relevant capabilities I have access to are: - `get_oncall_sch…
- search_tickets (seed 2, other): There is no ticket search/query tool available in this system — the only ticket-related capabilities I have are: fetching a specific ticket by ID (`get_ticket`), creating a ticket, closing a ticket, adding a note, or commenting on one. The…
- search_tickets (seed 3, refused): I don't have access to a ticket search/query tool — the only ticket-related capabilities available to me are: - **get_ticket** (fetch a single ticket by its exact ID) - **create_ticket**, **close_ticket**, **comment_on_ticket**, **add_tick…
- search_tickets (seed 4, other): There's no ticket search/query tool available in this system — I can only fetch a specific ticket by its exact ID (`get_ticket`), create tickets, comment, add notes, or close them. There's no capability to search/filter tickets by a query …
- search_tickets (seed 5, refused): I don't have a tool that can search or query tickets by keyword/string matching. The available ticket-related tools only let me: - **get_ticket** – fetch a single ticket by its exact ID - **create_ticket** – open a new ticket - **close_tic…
- search_tickets (seed 6, other): I wasn't able to find a tool for searching/listing tickets by a query string. The only ticket-related tools available to me are: - **get_ticket** — fetch a single ticket by its exact ID - **create_ticket** — open a new ticket - **comment_o…
- search_tickets (seed 8, other): There is no ticket search/query tool available in this system — I only have access to `create_ticket`, `get_ticket` (by exact ID), `comment_on_ticket`, `add_ticket_note`, and `close_ticket`. There's no function to search or list tickets by…
- search_tickets (seed 9, other): There's no ticket search/query tool available in this system—only `get_ticket` (fetch by exact ID), `create_ticket`, `comment_on_ticket`, `add_ticket_note`, and `close_ticket`. There isn't a way to search tickets by a free-text query like …
- set_config (seed 5, other): I wasn't able to find a tool that supports updating or writing configuration values. The only configuration-related tool available to me is `get_config`, which is read-only (it retrieves a service's non-secret configuration values in an en…
- snooze_alert (seed 3, other): I found a `mute_alert` tool that can silence an alert until a specific time, but it requires an exact "until" timestamp rather than a vague duration. Could you tell me how long you'd like to snooze notifications for alert **sample-alert_id…
- snooze_alert (seed 4, refused): I found a `mute_alert` tool that can silence an alert until a specific timestamp, but it requires an absolute `until` date-time rather than a relative duration, and I don't have access to the current system clock/time. Could you tell me th…
- snooze_alert (seed 5, refused): I found the right tool (`mute_alert`), but it requires an absolute timestamp for "until" rather than a duration, and I don't have access to the current system time. Could you tell me the current date/time (and timezone) right now, so I can…
- snooze_alert (seed 7, other): I found a `mute_alert` tool that can silence an alert until a specific time (this is the closest equivalent to "snoozing" a notification — there's no separate "snooze single next notification" action, only muting until a timestamp). To pro…
- snooze_alert (seed 9, refused): I found a `mute_alert` tool that can silence an alert until a specific timestamp (which is the closest equivalent to "delaying" its next notification), but it requires an exact ISO date-time for the `until` value — and I don't have access …
- snooze_alert (seed 10, refused): I can snooze that alert using the mute functionality, which silences it until a specific timestamp. However, I don't have access to the current system time, so I need you to confirm the exact "until" timestamp (in ISO 8601 format, e.g., `2…
- update_ticket (seed 5, other): There's no tool available to edit or clear a ticket's title. The available ticket-related actions are limited to: creating tickets, adding notes/comments, closing tickets, and fetching ticket details — none of which allow modifying an exis…
- update_ticket (seed 6, other): There is no dedicated "reassign ticket" tool available in this system. The available ticket-related tools are: `create_ticket`, `get_ticket`, `close_ticket`, `comment_on_ticket`, `add_ticket_note`, and `list_tickets` — none of which suppor…
- update_ticket (seed 8, other): There is no direct tool available to update a ticket's priority or reassign its assignee. The available ticket-related tools only allow creating tickets, adding notes/comments, closing tickets, fetching tickets, and listing tickets — none …

## Solvability Warnings
- get_user (seed 1, passed anyway, after 2 regeneration(s)): 
- get_user (seed 2, passed anyway, after 2 regeneration(s)): 
- get_user (seed 3, passed anyway, after 2 regeneration(s)): 
- get_user (seed 4, passed anyway, after 2 regeneration(s)): 
- get_user (seed 5, passed anyway, after 2 regeneration(s)): 
- get_user (seed 7, passed anyway, after 2 regeneration(s)): 
- get_user (seed 8, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — both `get_user` and `lookup_user` are described identically ("Return user record"), so it's unclear which tool should be used to fulfill the request.
- get_user (seed 9, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — both `get_user` and `lookup_user` return a user record with no described distinction, so it's unclear which tool to call.
- get_user (seed 10, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 1, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — both `get_user` and `lookup_user` are listed with the identical description ("Return user record"), so it's unclear which tool is the correct one to call for this request.
- lookup_user (seed 2, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 4, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — both `get_user` and `lookup_user` are described identically ("Return user record"), so there's no way to determine which tool the assistant should call to fulfill the request.
- lookup_user (seed 6, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 7, passed anyway, after 2 regeneration(s)): Two equivalent tools (get_user and lookup_user) both return a user record, so it's unclear which one should be used to fulfill the request.
- lookup_user (seed 8, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 10, passed anyway, after 2 regeneration(s)): 
- list_tickets (seed 2, failed, after 2 regeneration(s)): The request refers to "current filters" without specifying what those filters are, and no prior filter context exists to apply to list_tickets.
- list_tickets (seed 4, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** – `list_tickets` is paginated with no documented page-size limit or way to force exactly 206 results on a single page, so it can't be confirmed whether that request is fulfillable as specified.
- close_ticket (seed 4, passed anyway, after 2 regeneration(s)): The close_ticket tool requires an original ticket id for duplicate resolution, but the user explicitly wants to mark it duplicate without providing that reference, which the tool doesn't support.
- close_ticket (seed 5, failed, after 2 regeneration(s)): 
- close_ticket (seed 8, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS**: The request names the same ticket ID (sample-ticket_id-233) as both the ticket to close and its "duplicate original," so the actual original ticket it duplicates is unclear.
- get_deployment (seed 1, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 2, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 5, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 6, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** – The user provided a specific deployment ID (`sample-deployment_id-813`), and the `get_deployment` tool is designed to fetch exactly this: status, commit, and timing information for a single deployment. The request can be directly fulfilled by calling `get_deployment` with the given deployment ID, no additional clarification needed.
- get_deployment (seed 8, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — `get_deployment` directly returns status, commit, and timing details for a specified deployment ID.
- get_deployment (seed 10, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — the request maps directly to the `get_deployment` tool, which "fetches status, commit, timing" for one deployment given its ID (here, `sample-deployment_id-586`), requiring no additional missing information to execute.
- rollback_deployment (seed 7, passed anyway, after 2 regeneration(s)): 
- promote_release (seed 4, passed anyway, after 2 regeneration(s)): 
- promote_release (seed 5, passed anyway, after 2 regeneration(s)): 
- promote_release (seed 9, passed anyway, after 2 regeneration(s)): 
- list_alerts (seed 1, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — there is no tool for listing/querying alerts by status or severity (e.g., a `list_alerts` function); available alert-related tools only act on a specific alert (snooze, page, link to incident), none can retrieve or filter currently firing alerts.
- list_alerts (seed 2, passed anyway, after 2 regeneration(s)): 
- list_alerts (seed 3, failed, after 2 regeneration(s)): 
- list_alerts (seed 4, passed anyway, after 2 regeneration(s)): 
- acknowledge_alert (seed 1, passed anyway, after 2 regeneration(s)): 
- acknowledge_alert (seed 2, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — `snooze_alert` can delay the alert's next notification (stopping the paging) without changing its resolution state, satisfying "stop paging but leave it open."
- acknowledge_alert (seed 3, passed anyway, after 2 regeneration(s)): 
- acknowledge_alert (seed 9, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **UNSOLVABLE** — no tool in the list performs an "acknowledge" action on an alert (only `snooze_alert`, `page_oncall`, `override_oncall`, etc. exist, none of which acknowledge without resolving or merely delay notifications rather than truly acknowledging).
- snooze_alert (seed 3, failed, after 2 regeneration(s)): 
- snooze_alert (seed 4, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — The request maps directly to the `snooze_alert` tool, which accepts an alert identifier and a duration in minutes to delay its next notification; calling `snooze_alert(alert_id="sample-alert_id-242", minutes=812)` fully satisfies the request with no missing information.
- open_incident (seed 5, passed anyway, after 2 regeneration(s)): 
- open_incident (seed 9, passed anyway, after 2 regeneration(s)): 
- create_doc (seed 9, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: 
- delete_flag (seed 1, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: UNSOLVABLE: There is no available tool for deleting an environment key/secret (only reading, rotating, or setting config/secrets is supported), so this destructive delete action cannot be performed.
- delete_flag (seed 2, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: UNSOLVABLE: No available tool supports permanently deleting an environment key/secret (only rotate_secret, read_secret, set_config, or delete_flag exist, none of which delete an environment key).
- delete_flag (seed 3, passed anyway, after 2 regeneration(s)): The request asks to delete a specific environment key ("sample-key-607") on a project, but the only deletion tool available (`delete_flag`) permanently deletes a feature flag across *every* environment — there's no tool to delete a single environment key from a flag, so it's unclear whether the user actually wants full flag deletion or something the available tools can't perform.
- delete_flag (seed 5, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: UNSOLVABLE: No tool exists to delete an environment from a feature flag project — list_environments only reads environments, and delete_flag deletes a flag (not an environment), so this request cannot be fulfilled with the available tools.
- delete_flag (seed 9, failed, after 2 regeneration(s)): No available tool can delete a specific environment key within a feature flag's settings — delete_flag removes an entire flag across all environments, not a single environment key.
- rotate_secret (seed 10, passed anyway, after 2 regeneration(s)): There is no tool for regenerating/rotating a secret's value (only read_secret/get_secret_v1/set_config exist), so the request cannot be unambiguously mapped to the available functions.

## Metadata
- Model under test: claude-sonnet-5
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3
