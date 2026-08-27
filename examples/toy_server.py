"""Toy MCP server for the toolfit spike — 3 tools, one intentionally ambiguous pair.

create_task and update_task share the identical docstring on purpose: this is the realistic
"copy-pasted description" bug the spike's mutation test (grade/mutator.py) is built to find
and, via fix/fixer.py, propose a fix for.
"""

from mcp.server import MCPServer

mcp = MCPServer("ToyTasks")

_TASKS: dict[str, dict] = {}
_NEXT_ID = 1


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
    """List all tasks, optionally filtered by status (open, done)."""
    matches = [f"{tid}: {t['title']}" for tid, t in _TASKS.items() if t["status"] == status]
    return "\n".join(matches) if matches else f"No tasks with status {status!r}"


if __name__ == "__main__":
    mcp.run()
