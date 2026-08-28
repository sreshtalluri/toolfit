"""Toy MCP server for the toolfit spike — 5 tools, two intentionally ambiguous pairs plus one schema-complexity fixture.

create_task and update_task share the identical docstring on purpose: the realistic
"copy-pasted description" bug the spike's mutation test (grade/mutator.py) is built to find and,
via fix/fixer.py, propose a fix for. Empirically (spike run, 2026-08-27) that pair turned out to
have a confound: the shared text ("Add a new task.") linguistically favors create_task, and the
generated task text tends to use "create"/"add" phrasing regardless of which tool the sampled
arguments actually target — so a description fix and a task-phrasing bias were both moving at
the same time, muddying the signal.

count_tasks and list_tasks share a second, deliberately NEUTRAL vague description ("Get tasks by
status.") that doesn't linguistically favor either verb ("count" vs. "list/show"), and both tools
take the exact same argument shape (`status: str`) — isolating description ambiguity from
task-phrasing bias, for a cleaner read on whether mutation testing produces a clean signal on
its own.
"""

import datetime
from typing import Literal

from mcp.server import MCPServer

mcp = MCPServer("ToyTasks")

_TASKS: dict[str, dict] = {}
_NEXT_ID = 1
_REMINDERS: list[dict] = []


@mcp.tool()
def create_task(title: str, priority: str) -> str:
    """Add a new task."""
    global _NEXT_ID
    task_id = f"t{_NEXT_ID}"
    _NEXT_ID += 1
    _TASKS[task_id] = {"title": title, "priority": priority, "status": "open"}
    return f"Created task {task_id}: {title} (priority: {priority})"


@mcp.tool()
def update_task(task_id: str, title: str) -> str:
    """Add a new task."""
    if task_id not in _TASKS:
        return f"No such task: {task_id}"
    _TASKS[task_id]["title"] = title
    return f"Updated task {task_id}: {title}"


@mcp.tool()
def list_tasks(status: str) -> str:
    """Get tasks by status."""
    matches = [f"{tid}: {t['title']}" for tid, t in _TASKS.items() if t["status"] == status]
    return "\n".join(matches) if matches else f"No tasks with status {status!r}"


@mcp.tool()
def count_tasks(status: str) -> str:
    """Get tasks by status."""
    n = sum(1 for t in _TASKS.values() if t["status"] == status)
    return f"{n} tasks with status {status!r}"


@mcp.tool()
def create_reminder(
    task_id: str,
    remind_at: datetime.date,
    notify_channels: list[str],
    snooze_minutes: int,
    priority: Literal["low", "medium", "high"],
    notes: str | None = None,
) -> str:
    """Schedule a reminder for an existing task."""
    _REMINDERS.append(
        {
            "task_id": task_id,
            "remind_at": remind_at.isoformat(),
            "notify_channels": notify_channels,
            "snooze_minutes": snooze_minutes,
            "priority": priority,
            "notes": notes,
        }
    )
    return f"Reminder scheduled for task {task_id} on {remind_at.isoformat()}"


if __name__ == "__main__":
    mcp.run()
