# /// script
# dependencies = ["mcp>=2.0,<3"]
# ///
"""Production-shaped dummy at the size teams actually ship: an internal ops platform with 48
tools across users, tickets, deployments, alerts, on-call, docs, feature flags and config.

Nothing here talks to a real system — every tool returns a stub — but the catalog is what an
LLM sees, and that's all toolfit evaluates. Planted problems, so a run has known answers:

Static (scan finds these):
  - duplicate descriptions: get_user / lookup_user; list_flags / get_flags
  - too short: update_ticket, set_config
  - deprecated: create_incident_legacy, get_secret_v1

Behavioural (only eval can find these):
  - near-neighbours: comment_on_ticket vs add_ticket_note; restart_service vs redeploy_service;
    mute_alert vs snooze_alert; list_tickets vs search_tickets
  - undeclared preconditions: rollback_deployment needs a deployment id that only
    list_deployments returns; page_oncall needs a schedule id from get_oncall_schedule;
    acknowledge_alert needs an alert id from list_alerts
  - one DECLARED precondition for contrast: promote_release says to run validate_release first

What the first Sonnet 5 baseline showed (docs/examples/ops-server/, 5 seeds, 84%): the declared
precondition was observed 5/5 and correctly not flagged. The three id-lookup plants did NOT fire:
generated tasks carry the sampled id in the text, so the model has no reason to look it up.
Precondition findings detect STATE dependencies (stage before commit), not id lookups. The real
failures were argument-level (create_flag 2/5 with all five calls routed right) and no-calls
(snooze_alert 4/5 asked a question instead), not near-neighbour confusion.
"""

import sys
from typing import Literal

from pydantic import BaseModel, Field

from mcp.server import MCPServer

server = MCPServer("ops-dummy")


class MaintenanceWindow(BaseModel):
    starts_at: str = Field(json_schema_extra={"format": "date-time"})
    ends_at: str = Field(json_schema_extra={"format": "date-time"})
    timezone: str = Field(default="UTC", description="IANA zone, e.g. Europe/Berlin")


class Pagination(BaseModel):
    limit: int = Field(default=50, ge=1, le=500)
    cursor: str | None = None


# ---- users & teams -------------------------------------------------------------------------


@server.tool()
def get_user(user_id: str) -> str:
    """Return a user record."""
    return "{}"


@server.tool()
def lookup_user(email: str = Field(json_schema_extra={"format": "email"})) -> str:
    """Return a user record."""
    return "{}"


@server.tool()
def list_users(team_id: str | None = None, role: Literal["admin", "engineer", "viewer"] | None = None, page: Pagination | None = None) -> str:
    """List users in the organisation, optionally filtered by team or role. Paginated."""
    return "[]"


@server.tool()
def invite_user(email: str = Field(json_schema_extra={"format": "email"}), role: Literal["admin", "engineer", "viewer"] = "engineer", team_ids: list[str] | None = None) -> str:
    """Send an invitation email to a new user and pre-assign a role and teams."""
    return "ok"


@server.tool()
def deactivate_user(user_id: str, reason: Literal["left_company", "security", "inactive"]) -> str:
    """Deactivate a user account, revoking sessions and API tokens. Reversible by an admin."""
    return "ok"


@server.tool()
def list_teams(include_members: bool = False) -> str:
    """List teams, optionally with their member user ids."""
    return "[]"


# ---- tickets ----------------------------------------------------------------------------------


@server.tool()
def create_ticket(
    title: str,
    body: str,
    priority: Literal["p0", "p1", "p2", "p3"] = "p2",
    assignee_id: str | None = None,
    labels: list[str] | None = None,
) -> str:
    """Open a new ticket with a title, description body, priority and optional assignee/labels."""
    return "TCK-1"


@server.tool()
def update_ticket(ticket_id: str, title: str | None = None, priority: Literal["p0", "p1", "p2", "p3"] | None = None, assignee_id: str | None = None) -> str:
    """Update ticket."""
    return "ok"


@server.tool()
def get_ticket(ticket_id: str) -> str:
    """Fetch one ticket by id, including comments and status history."""
    return "{}"


@server.tool()
def list_tickets(status: Literal["open", "in_progress", "blocked", "closed"] = "open", assignee_id: str | None = None, page: Pagination | None = None) -> str:
    """Tickets matching the given filters."""
    return "[]"


@server.tool()
def search_tickets(query: str, page: Pagination | None = None) -> str:
    """Tickets matching the given query."""
    return "[]"


@server.tool()
def comment_on_ticket(ticket_id: str, body: str, notify_assignee: bool = True) -> str:
    """Post a comment on a ticket, visible to everyone who can see the ticket."""
    return "ok"


@server.tool()
def add_ticket_note(ticket_id: str, body: str) -> str:
    """Attach a private note to a ticket, visible only to the author and admins."""
    return "ok"


@server.tool()
def close_ticket(ticket_id: str, resolution: Literal["fixed", "wont_fix", "duplicate", "cannot_reproduce"], duplicate_of: str | None = None) -> str:
    """Close a ticket with a resolution. When the resolution is duplicate, pass the original ticket id."""
    return "ok"


# ---- deployments & environments --------------------------------------------------------------


@server.tool()
def list_environments(project_id: str) -> str:
    """List deployable environments for a project (e.g. staging, production) with their ids."""
    return "[]"


@server.tool()
def list_deployments(environment_id: str, page: Pagination | None = None) -> str:
    """List past and current deployments in an environment, newest first, with deployment ids."""
    return "[]"


@server.tool()
def get_deployment(deployment_id: str) -> str:
    """Fetch the status, commit and timing of one deployment."""
    return "{}"


@server.tool()
def deploy_release(release_id: str, environment_id: str, window: MaintenanceWindow | None = None) -> str:
    """Deploy a built release to an environment, optionally inside a maintenance window."""
    return "ok"


@server.tool()
def rollback_deployment(deployment_id: str, reason: str) -> str:
    """Roll an environment back to the state before the given deployment."""
    return "ok"


@server.tool()
def validate_release(release_id: str) -> str:
    """Run the release's smoke tests and security checks; returns a validation report."""
    return "{}"


@server.tool()
def promote_release(release_id: str, to_env: Literal["staging", "production"]) -> str:
    """Promote a release to the next environment. Only validated releases can be promoted: run validate_release first."""
    return "ok"


@server.tool()
def restart_service(service_id: str, environment_id: str) -> str:
    """Restart the running instances of a service without changing the deployed version."""
    return "ok"


@server.tool()
def redeploy_service(service_id: str, environment_id: str) -> str:
    """Rebuild and redeploy a service at its currently deployed version."""
    return "ok"


# ---- alerts & incidents ---------------------------------------------------------------------


@server.tool()
def list_alerts(severity: Literal["critical", "warning", "info"] | None = None, service_id: str | None = None, page: Pagination | None = None) -> str:
    """List firing alerts with their ids, optionally filtered by severity or service."""
    return "[]"


@server.tool()
def acknowledge_alert(alert_id: str, note: str | None = None) -> str:
    """Acknowledge an alert so it stops paging, without resolving it."""
    return "ok"


@server.tool()
def mute_alert(alert_id: str, until: str = Field(json_schema_extra={"format": "date-time"})) -> str:
    """Silence an alert until the given time; it will not page or notify."""
    return "ok"


@server.tool()
def snooze_alert(alert_id: str, minutes: int = Field(default=30, ge=1, le=1440)) -> str:
    """Delay an alert's next notification by a number of minutes."""
    return "ok"


@server.tool()
def open_incident(title: str, severity: Literal["sev1", "sev2", "sev3"], commander_id: str | None = None, alert_ids: list[str] | None = None) -> str:
    """Declare an incident, optionally linking the alerts that triggered it and naming a commander."""
    return "INC-1"


@server.tool()
def create_incident_legacy(title: str, severity: Literal["sev1", "sev2", "sev3"]) -> str:
    """DEPRECATED: use open_incident. Creates an incident without commander or alert links."""
    return "INC-1"


@server.tool()
def resolve_incident(incident_id: str, summary: str, postmortem_required: bool = True) -> str:
    """Mark an incident resolved with a summary; optionally require a postmortem document."""
    return "ok"


# ---- on-call ---------------------------------------------------------------------------------


@server.tool()
def get_oncall_schedule(team_id: str) -> str:
    """Return a team's on-call schedule id and the current and next responders."""
    return "{}"


@server.tool()
def page_oncall(schedule_id: str, message: str, urgency: Literal["high", "low"] = "high") -> str:
    """Page the current responder on a schedule with a message."""
    return "ok"


@server.tool()
def override_oncall(schedule_id: str, user_id: str, window: MaintenanceWindow) -> str:
    """Temporarily replace the scheduled responder with a specific user for a time window."""
    return "ok"


@server.tool()
def list_shifts(schedule_id: str, days_ahead: int = Field(default=7, ge=1, le=90)) -> str:
    """List upcoming on-call shifts for a schedule."""
    return "[]"


# ---- docs ------------------------------------------------------------------------------------


@server.tool()
def search_docs(query: str, space: str | None = None, page: Pagination | None = None) -> str:
    """Full-text search across wiki pages, optionally within one space."""
    return "[]"


@server.tool()
def get_doc(doc_id: str, version: int | None = None) -> str:
    """Fetch a wiki page's content, optionally at a specific version."""
    return "{}"


@server.tool()
def create_doc(space: str, title: str, body_markdown: str, parent_id: str | None = None) -> str:
    """Create a wiki page in a space, optionally nested under a parent page."""
    return "DOC-1"


@server.tool()
def update_doc(doc_id: str, body_markdown: str, change_note: str | None = None) -> str:
    """Replace a wiki page's content, creating a new version with an optional change note."""
    return "ok"


@server.tool()
def archive_doc(doc_id: str) -> str:
    """Archive a wiki page so it no longer appears in search; it can be restored later."""
    return "ok"


# ---- feature flags ---------------------------------------------------------------------------


@server.tool()
def list_flags(project_id: str) -> str:
    """List feature flags for a project."""
    return "[]"


@server.tool()
def get_flags(project_id: str, environment_id: str) -> str:
    """List feature flags for a project."""
    return "[]"


@server.tool()
def create_flag(project_id: str, key: str, description: str, default_on: bool = False) -> str:
    """Create a feature flag with a key and description; off by default unless default_on is set."""
    return "ok"


@server.tool()
def set_flag(project_id: str, key: str, environment_id: str, enabled: bool, rollout_percent: int = Field(default=100, ge=0, le=100)) -> str:
    """Turn a flag on or off in one environment, optionally for a percentage of users."""
    return "ok"


@server.tool()
def delete_flag(project_id: str, key: str) -> str:
    """Permanently delete a feature flag from every environment. Cannot be undone."""
    return "ok"


# ---- config & secrets ------------------------------------------------------------------------


@server.tool()
def get_config(service_id: str, environment_id: str) -> str:
    """Return a service's non-secret configuration values in an environment."""
    return "{}"


@server.tool()
def set_config(service_id: str, environment_id: str, key: str, value: str) -> str:
    """Set config."""
    return "ok"


@server.tool()
def get_secret_v1(service_id: str, name: str) -> str:
    """DEPRECATED: use read_secret. Returns a secret value without audit logging."""
    return "***"


@server.tool()
def read_secret(service_id: str, environment_id: str, name: str, justification: str) -> str:
    """Return a secret value; the justification is written to the audit log."""
    return "***"


@server.tool()
def rotate_secret(service_id: str, environment_id: str, name: str, notify_owner: bool = True) -> str:
    """Generate a new value for a secret and redeploy the services that use it."""
    return "ok"


if __name__ == "__main__":
    if "--http" in sys.argv:
        server.run(transport="streamable-http", port=8766)
    else:
        server.run()
