from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import (
    ActivityAction,
    ActivityEvent,
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)

_tasks: dict[str, TaskResponse] = {}
_activity_events: list[ActivityEvent] = []


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a new task in memory.

    Args:
        payload: Task creation data, including title, description, status,
            priority, and optional assignee.

    Returns:
        TaskResponse: The created task with server-generated identifiers and
            timestamps.

    Raises:
        None.
    """
    now = datetime.now(timezone.utc)
    task_id = str(uuid4())
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
) -> list[TaskResponse]:
    """Return all stored tasks, optionally filtered by status or priority.

    Args:
        status: Optional task status filter. When provided, only matching tasks
            are returned.
        priority: Optional task priority filter. When provided, only matching
            tasks are returned.

    Returns:
        list[TaskResponse]: A list of tasks in the current in-memory store after
            optional filtering.

    Raises:
        None.
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Fetch a task by its generated identifier.

    Args:
        task_id: The UUID-like task identifier to look up.

    Returns:
        TaskResponse | None: The matching task, or None when no task exists for
            the supplied identifier.

    Raises:
        None.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial task update for the matching task record.

    Args:
        task_id: The identifier of the task to update.
        payload: Partial update payload containing only fields to change.

    Returns:
        TaskResponse | None: The updated task, or None when the task does not
            exist.

    Raises:
        None.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return task

    now = datetime.now(timezone.utc)
    updated = task.model_copy(update={**updates, "updated_at": now})
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    """Delete a task from the in-memory store if it exists.

    Args:
        task_id: The identifier of the task to delete.

    Returns:
        bool: True when a task was removed, otherwise False.

    Raises:
        None.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def log_activity(task_id: str, action: ActivityAction, details: str) -> ActivityEvent:
    """Record an activity event for a task.

    Args:
        task_id: The task identifier associated with the event.
        action: The activity action being recorded.
        details: A human-readable description of the action.

    Returns:
        ActivityEvent: The newly created activity event.

    Raises:
        None.
    """
    event = ActivityEvent(
        id=str(uuid4()),
        task_id=task_id,
        action=action,
        details=details,
        timestamp=datetime.now(timezone.utc),
    )
    _activity_events.append(event)
    return event


def get_all_activity() -> list[ActivityEvent]:
    """Return all recorded activity events sorted newest-first.

    Args:
        None.

    Returns:
        list[ActivityEvent]: Activity events ordered by timestamp descending.

    Raises:
        None.
    """
    return sorted(_activity_events, key=lambda e: e.timestamp, reverse=True)


def get_activity_for_task(task_id: str) -> list[ActivityEvent]:
    """Return activity events for a specific task sorted newest-first.

    Args:
        task_id: The task identifier whose activity is requested.

    Returns:
        list[ActivityEvent]: All matching activity events ordered by timestamp
            descending.

    Raises:
        None.
    """
    events = [e for e in _activity_events if e.task_id == task_id]
    return sorted(events, key=lambda e: e.timestamp, reverse=True)


def _reset() -> None:
    _tasks.clear()
    _activity_events.clear()