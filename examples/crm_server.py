# /// script
# dependencies = ["mcp>=2.0,<3"]
# ///
"""Production-shaped dummy: a small CRM MCP server, the kind of catalog a SaaS team ships.

Realistic schema features: email/date formats, enums, nested address object, tag arrays,
optional fields, numeric bounds. Planted description problems: search/list share a vague
description, update_contact is too short, get_contact is deprecated, and add_note/send_email
are near-neighbours ("message" vs "note").
"""

import sys
from typing import Literal

from pydantic import BaseModel, Field

from mcp.server import MCPServer

server = MCPServer("crm-dummy")


class Address(BaseModel):
    street: str
    city: str
    country: str = Field(description="ISO 3166-1 alpha-2, e.g. US")


@server.tool()
def create_contact(
    email: str = Field(json_schema_extra={"format": "email"}),
    full_name: str = "",
    company: str | None = None,
    tags: list[str] | None = None,
    address: Address | None = None,
) -> str:
    """Create a new contact record from an email address and optional profile details."""
    return "ok"


@server.tool()
def update_contact(contact_id: str, full_name: str | None = None, company: str | None = None) -> str:
    """Update contact."""
    return "ok"


@server.tool()
def get_contact(contact_id: str) -> str:
    """Fetch one contact by id. DEPRECATED: use search_contacts with the id instead."""
    return "ok"


@server.tool()
def search_contacts(query: str, limit: int = Field(default=20, ge=1, le=100)) -> str:
    """Find contacts."""
    return "[]"


@server.tool()
def list_contacts(
    status: Literal["lead", "customer", "churned"] = "lead",
    limit: int = Field(default=20, ge=1, le=100),
) -> str:
    """Find contacts."""
    return "[]"


@server.tool()
def add_note(contact_id: str, body: str, pinned: bool = False) -> str:
    """Attach an internal note to a contact's timeline. Notes are visible only to your team."""
    return "ok"


@server.tool()
def send_email(
    contact_id: str,
    subject: str,
    body: str,
    send_at: str | None = Field(default=None, json_schema_extra={"format": "date-time"}),
) -> str:
    """Send an email to the contact, optionally scheduled for a later send_at time."""
    return "ok"


@server.tool()
def delete_contact(contact_id: str, reason: Literal["duplicate", "gdpr_request", "spam"]) -> str:
    """Permanently delete a contact and all associated notes. Cannot be undone."""
    return "ok"


if __name__ == "__main__":
    if "--http" in sys.argv:
        server.run(transport="streamable-http", port=8765)
    else:
        server.run()
