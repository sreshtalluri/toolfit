## Confusion Matrix

| Intended \ Called | acknowledge_alert | add_ticket_note | archive_doc | close_ticket | comment_on_ticket | create_doc | create_flag | create_incident_legacy | create_ticket | deactivate_user | delete_flag | deploy_release | get_config | get_deployment | get_doc | get_flags | get_oncall_schedule | get_secret_v1 | get_ticket | get_user | invite_user | list_alerts | list_deployments | list_environments | list_flags | list_shifts | list_teams | list_tickets | list_users | lookup_user | mute_alert | open_incident | override_oncall | page_oncall | promote_release | read_secret | redeploy_service | resolve_incident | restart_service | rollback_deployment | rotate_secret | search_docs | search_tickets | set_config | set_flag | snooze_alert | update_doc | update_ticket | validate_release | (no call) | (hallucinated) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| acknowledge_alert | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| add_ticket_note | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| archive_doc | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| close_ticket | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| comment_on_ticket | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| create_doc | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_flag | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| create_incident_legacy | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| create_ticket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| deactivate_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| delete_flag | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| deploy_release | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_config | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| get_deployment | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| get_doc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| get_flags | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| get_oncall_schedule | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| get_secret_v1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_ticket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| get_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| invite_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| list_alerts | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 4 |
| list_deployments | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| list_environments | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| list_flags | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 1 |
| list_shifts | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| list_teams | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| list_tickets | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 1 |
| list_users | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 2 |
| lookup_user | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| mute_alert | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| open_incident | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 |
| override_oncall | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| page_oncall | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| promote_release | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 2 | 0 |
| read_secret | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| redeploy_service | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| resolve_incident | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| restart_service | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rollback_deployment | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rotate_secret | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| search_docs | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 |
| search_tickets | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 4 |
| set_config | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| set_flag | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| snooze_alert | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 |
| update_doc | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 1 | 0 |
| update_ticket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 1 | 1 |
| validate_release | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 |

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
- acknowledge_alert: 8/10 (80%), 95% CI [49%, 94%]
- add_ticket_note: 10/10 (100%), 95% CI [72%, 100%]
- archive_doc: 10/10 (100%), 95% CI [72%, 100%]
- close_ticket: 7/10 (70%), 95% CI [40%, 89%]
- comment_on_ticket: 3/10 (30%), 95% CI [11%, 60%]
- create_doc: 10/10 (100%), 95% CI [72%, 100%]
- create_flag: 3/10 (30%), 95% CI [11%, 60%]
- create_incident_legacy: 0/10 (0%), 95% CI [0%, 28%]
- create_ticket: 9/10 (90%), 95% CI [60%, 98%]
- deactivate_user: 8/10 (80%), 95% CI [49%, 94%]
- delete_flag: 7/10 (70%), 95% CI [40%, 89%]
- deploy_release: 9/10 (90%), 95% CI [60%, 98%]
- get_config: 9/10 (90%), 95% CI [60%, 98%]
- get_deployment: 9/10 (90%), 95% CI [60%, 98%]
- get_doc: 5/10 (50%), 95% CI [24%, 76%]
- get_flags: 9/10 (90%), 95% CI [60%, 98%]
- get_oncall_schedule: 8/10 (80%), 95% CI [49%, 94%]
- get_secret_v1: 2/10 (20%), 95% CI [6%, 51%]
- get_ticket: 4/10 (40%), 95% CI [17%, 69%]
- get_user: 1/10 (10%), 95% CI [2%, 40%]
- invite_user: 7/10 (70%), 95% CI [40%, 89%]
- list_alerts: 2/10 (20%), 95% CI [6%, 51%]
- list_deployments: 5/10 (50%), 95% CI [24%, 76%]
- list_environments: 8/10 (80%), 95% CI [49%, 94%]
- list_flags: 2/10 (20%), 95% CI [6%, 51%]
- list_shifts: 9/10 (90%), 95% CI [60%, 98%]
- list_teams: 3/10 (30%), 95% CI [11%, 60%]
- list_tickets: 0/10 (0%), 95% CI [0%, 28%]
- list_users: 0/10 (0%), 95% CI [0%, 28%]
- lookup_user: 9/10 (90%), 95% CI [60%, 98%]
- mute_alert: 9/10 (90%), 95% CI [60%, 98%]
- open_incident: 7/10 (70%), 95% CI [40%, 89%]
- override_oncall: 4/10 (40%), 95% CI [17%, 69%]
- page_oncall: 6/10 (60%), 95% CI [31%, 83%]
- promote_release: 8/10 (80%), 95% CI [49%, 94%]
- read_secret: 10/10 (100%), 95% CI [72%, 100%]
- redeploy_service: 10/10 (100%), 95% CI [72%, 100%]
- resolve_incident: 7/10 (70%), 95% CI [40%, 89%]
- restart_service: 10/10 (100%), 95% CI [72%, 100%]
- rollback_deployment: 10/10 (100%), 95% CI [72%, 100%]
- rotate_secret: 7/10 (70%), 95% CI [40%, 89%]
- search_docs: 3/10 (30%), 95% CI [11%, 60%]
- search_tickets: 3/10 (30%), 95% CI [11%, 60%]
- set_config: 10/10 (100%), 95% CI [72%, 100%]
- set_flag: 8/10 (80%), 95% CI [49%, 94%]
- snooze_alert: 4/10 (40%), 95% CI [17%, 69%]
- update_doc: 9/10 (90%), 95% CI [60%, 98%]
- update_ticket: 6/10 (60%), 95% CI [31%, 83%]
- validate_release: 10/10 (100%), 95% CI [72%, 100%]

## Preconditions (observed)

Tools the model called *before* correctly calling the intended one, per trial:

- validate_release → promote_release: 4/10 trials

```mermaid
graph LR
  t0["validate_release"]
  t1["promote_release"]
  t0 -->|4/10| t1
```

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- acknowledge_alert: note extra 1/10
- close_ticket: duplicate_of extra 2/10; resolution wrong 1/10
- comment_on_ticket: notify_assignee extra 5/10
- create_flag: project_id wrong 3/10; default_on extra 2/10; default_on wrong 1/10
- deploy_release: window wrong 1/10
- get_doc: version extra 3/10
- invite_user: role extra 2/10
- list_alerts: page missing 1/10; limit extra 1/10
- list_deployments: page extra 3/10
- list_teams: include_members wrong 1/10
- list_tickets: page wrong 1/10; status extra 1/10; page extra 1/10
- list_users: page extra 1/10
- override_oncall: window wrong 6/10
- page_oncall: urgency extra 3/10
- resolve_incident: postmortem_required extra 1/10
- rotate_secret: notify_owner extra 3/10
- search_docs: page extra 2/10; page missing 1/10; limit extra 1/10; space extra 1/10
- set_flag: enabled wrong 2/10; rollout_percent wrong 2/10
- snooze_alert: minutes extra 6/10
- update_ticket: ticket_id wrong 1/10; title extra 1/10

## No-Call Replies

- delete_flag (seed 2, refused): I cannot perform this task as it requires a function that is not available in the given list of functions.
- delete_flag (seed 6, refused): I am unable to fulfill this request as the necessary tools are not present in this environment.
- delete_flag (seed 7, refused): I am not able to execute this task as it requires a function that is not available in the given library.
- resolve_incident (seed 9, other): <function(resolve_incident){"incident_id": "sample-incident_id-475", "summary": "sample-summary-628", "postmortem_required": true}}</function>
- update_doc (seed 6, other): <function:update_doc>{"doc_id": "sample-doc_id-813", "body_markdown": "sample-body_markdown-588"}</function>

## Solvability Warnings
- get_user (seed 1, failed, after 2 regeneration(s)): 
- get_user (seed 2, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — both `get_user` and `lookup_user` are described identically as returning a user record, so it's unclear which tool should be used to fetch the details for sample-user_id-979.
- get_user (seed 4, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: This request is **AMBIGUOUS**: multiple tools (get_user, lookup_user) could return the account details, and it's unclear which one should be used since both appear to serve the same purpose.
- get_user (seed 5, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — both `get_user` and `lookup_user` return a user record for a given ID, and nothing in the request indicates which of the two identical-purpose tools should be used.
- get_user (seed 8, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: This request is **SOLVABLE**.

The user wants to retrieve a user record by ID ("sample-user_id-233"), which directly matches the available `get_user` tool (or alternatively `lookup_user`), designed to "Return user record" given a user ID — no ambiguity in intent or tool selection.
- get_user (seed 10, failed, after 2 regeneration(s)): 
- lookup_user (seed 1, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — Two tools (`get_user` and `lookup_user`) have identical descriptions ("Return user record"), giving no basis to determine which one is intended for looking up a user by email.
- lookup_user (seed 4, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 5, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — both `get_user` and `lookup_user` are described identically as returning a user record, so it's unclear which tool should be used to pull up user638@example.com.
- lookup_user (seed 7, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — the tool list contains two functionally identical tools (`get_user` and `lookup_user`, both described as "Return user record"), so it's unclear which one should be used to pull up the record for user332@example.com.
- lookup_user (seed 8, passed anyway, after 2 regeneration(s)): 
- lookup_user (seed 9, passed anyway, after 2 regeneration(s)): Both `get_user` and `lookup_user` are described identically as returning a user record, so it's unclear which single tool should be called to fetch the account for user475@example.com.
- lookup_user (seed 10, passed anyway, after 2 regeneration(s)): 
- list_teams (seed 1, failed, after 2 regeneration(s)): 
- list_teams (seed 3, passed anyway, after 2 regeneration(s)): 
- list_teams (seed 4, passed anyway, after 2 regeneration(s)): 
- list_teams (seed 7, failed, after 2 regeneration(s)): 
- update_ticket (seed 5, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — `update_ticket` can set the title field on ticket sample-ticket_id-638 to an empty string.
- update_ticket (seed 7, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — The request provides a specific ticket ID (sample-ticket_id-332) and a clear target priority value (P0), which maps directly to the `update_ticket` tool's capability to modify a ticket's priority field.
- list_tickets (seed 2, failed, after 2 regeneration(s)): 
- list_tickets (seed 5, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: This request is **AMBIGUOUS**: `list_tickets` requires filters to be specified and is paginated, so an unbounded "full list, no filters" request cannot be executed as a single unambiguous call without clarifying pagination/scope.
- close_ticket (seed 4, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: I can't fulfill this exact request as specified. The `close_ticket` tool requires that when resolution is set to **duplicate**, you must provide the original ticket ID being referenced — there's no option to close with resolution "duplicate" while leaving that reference blank.

A few ways to proceed:

1. **Provide the original ticket ID** — if you can tell me which ticket sample-ticket_id-242 duplicates, I'll close it with that reference.
2. **Use a different resolution** — if there's no original ticket to link, I could close it with a resolution like "resolved," "invalid," or "won't fix" instead, and optionally note in a comment that it was a duplicate without a formal link.

Let me know which you'd prefer.
- close_ticket (seed 5, failed, after 2 regeneration(s)): 
- close_ticket (seed 8, failed, after 2 regeneration(s)): A ticket cannot be a duplicate of itself—the request specifies sample-ticket_id-233 as both the ticket to close and its own original, which is logically invalid and needs clarification on the correct original ticket ID.
- get_deployment (seed 1, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — the request maps directly to `get_deployment`, which fetches status and commit timing for a specific deployment ID, and the ID ("sample-deployment_id-138") is already provided in the request.
- get_deployment (seed 2, failed, after 2 regeneration(s)): 
- get_deployment (seed 3, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 4, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — the identifier "sample-deployment_id-242" looks like a placeholder/example rather than an actual deployment ID, so `get_deployment` can't be reliably invoked without confirming the real deployment ID (and its environment) to query.
- get_deployment (seed 5, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** – `get_deployment` directly returns status, commit, and timing for a given deployment ID, matching exactly what the user requested for `sample-deployment_id-638`.
- get_deployment (seed 6, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — `get_deployment` needs a specific deployment ID, but it's unclear which environment/project the deployment belongs to (deployments are scoped per environment via `list_deployments`), and "sample-deployment_id-813" appears to be a placeholder rather than a real ID, so the target environment/project must be clarified first.
- get_deployment (seed 9, passed anyway, after 2 regeneration(s)): 
- get_deployment (seed 10, passed anyway, after 2 regeneration(s)): 
- rollback_deployment (seed 7, passed anyway, after 2 regeneration(s)): 
- rollback_deployment (seed 8, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE**: The request provides a specific deployment ID and a rollback reason, which directly maps to the `rollback_deployment` tool's required parameters—no missing information prevents execution.
- promote_release (seed 7, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: I'll start by validating the release as requested.
- list_alerts (seed 1, failed, after 2 regeneration(s)): 
- list_alerts (seed 2, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **UNSOLVABLE**: No available tool retrieves or lists currently firing alerts (only alert-action tools like mute_alert/snooze_alert exist, which require an alert ID rather than listing them).
- list_alerts (seed 4, failed, after 2 regeneration(s)): 
- list_alerts (seed 7, failed, after 2 regeneration(s)): 
- list_alerts (seed 9, failed, after 2 regeneration(s)): 
- acknowledge_alert (seed 1, passed anyway, after 2 regeneration(s)): 
- acknowledge_alert (seed 2, passed anyway, after 2 regeneration(s)): 
- acknowledge_alert (seed 6, passed anyway, after 2 regeneration(s)): 
- acknowledge_alert (seed 8, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **AMBIGUOUS** — the tool list has no explicit "acknowledge alert" action (only "silence" or "snooze"), so it's unclear which tool should be used to stop paging without resolving.
- snooze_alert (seed 2, failed, after 2 regeneration(s)): 
- snooze_alert (seed 6, failed, after 2 regeneration(s)): 
- snooze_alert (seed 9, failed, after 2 regeneration(s)): 
- open_incident (seed 1, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — the `open_incident` tool directly supports declaring an incident with a specified title and severity level, both of which are provided in the request.
- create_incident_legacy (seed 2, failed, after 2 regeneration(s)): 
- create_incident_legacy (seed 4, failed, after 2 regeneration(s)): 
- create_incident_legacy (seed 8, failed, after 2 regeneration(s)): 
- update_doc (seed 2, passed anyway, after 2 regeneration(s)): 
- update_doc (seed 8, passed anyway, after 2 regeneration(s)): 
- list_flags (seed 7, failed, after 2 regeneration(s)): 
- list_flags (seed 9, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: **SOLVABLE** — the request can be directly fulfilled using the `list_flags` (or `get_flags`) tool by specifying the project "sample-project_id-475" to return all its configured feature flags.
- get_flags (seed 3, passed anyway, after 2 regeneration(s)): 
- set_flag (seed 4, passed anyway, after 2 regeneration(s)): Turning a flag off and simultaneously setting a rollout percentage are contradictory since a disabled flag serves no users regardless of the percentage, so the intended end state is unclear.
- set_flag (seed 9, failed, after 2 regeneration(s)): Turning the flag off and setting an 86% rollout are contradictory, since a rollout percentage only has effect when the flag is on, so it's unclear which final state the user actually wants.
- delete_flag (seed 2, failed, after 2 regeneration(s)): The available tools don't include any function to delete an environment key/secret (only read_secret, rotate_secret, and environment-level tools exist, but no delete_secret/delete_key operation), so this request cannot be mapped to an available action.
- delete_flag (seed 6, failed, after 2 regeneration(s)): The available tools include ways to read/rotate secrets and manage feature flags/config, but there is no tool listed for deleting an environment key/secret (only delete_flag exists for feature flags), so this request cannot be mapped to any available action.
- delete_flag (seed 7, failed, after 2 regeneration(s)): unparseable response, treated as ambiguous: UNSOLVABLE: The available tools include no function to delete an environment or environment key (only secret/flag/config management and environment listing/deployment tools exist), so this request cannot be fulfilled with the provided toolset.
- delete_flag (seed 8, passed anyway, after 2 regeneration(s)): The only deletion tool, delete_flag, permanently removes a feature flag from every environment with no option to target or exclude a single environment, so the request to delete it from only one environment while leaving it intact elsewhere cannot be fulfilled with a single call.
- delete_flag (seed 9, passed anyway, after 2 regeneration(s)): The available tools include `delete_flag` (which permanently deletes an entire feature flag) but no tool to delete a specific "environment key" within a flag's settings, so this request doesn't map cleanly to any available action.
- get_secret_v1 (seed 4, passed anyway, after 2 regeneration(s)): unparseable response, treated as ambiguous: 
- rotate_secret (seed 5, passed anyway, after 2 regeneration(s)): rotate_secret has one parameter available, but there's no tool to identify which services use the secret or who its "owner" is for notification, making the redeploy/notify steps unactionable.

## Metadata
- Model under test: meta-llama/llama-3.3-70b-instruct
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3
