from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}
_activity: list[dict] = []


def _reset() -> None:
    """Test helper: reset in-memory storage to an empty state.

    Tests call `storage._reset()` to ensure a clean slate between cases.
    This clears the internal tasks and activity collections.
    """
    global _tasks, _activity
    _tasks.clear()
    _activity.clear()


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a new task record.

    Args:
        payload: The task creation payload to persist.

    Returns:
        The created task resource with generated identifiers and timestamps.
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
    # log activity
    _activity.append(
        {
            "id": str(uuid4()),
            "task_id": task_id,
            "action": "created",
            "details": f"Task created: {task.title}",
            "timestamp": now.isoformat(),
        }
    )
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
) -> list[TaskResponse]:
    """Return all stored tasks, optionally filtered by status or priority.

    Args:
        status: Optional status filter. Only tasks matching this value are
            included.
        priority: Optional priority filter. Only tasks matching this value are
            included.

    Returns:
        A list of task records matching the provided filters.
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Return a stored task by its identifier.

    Args:
        task_id: The unique task identifier to look up.

    Returns:
        The matching task, or `None` if no task exists for the identifier.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Update a task record with the supplied partial payload.

    Args:
        task_id: The unique identifier of the task to update.
        payload: A partial task update containing only the fields to modify.

    Returns:
        The updated task resource, or `None` if the task does not exist.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return task

    now = datetime.now(timezone.utc)
    # detect status change for activity
    status_changed = False
    new_status = updates.get("status")
    if new_status is not None and new_status != task.status:
        status_changed = True

    updated = task.model_copy(update={**updates, "updated_at": now})
    _tasks[task_id] = updated

    # log activity
    if status_changed:
        _activity.append(
            {
                "id": str(uuid4()),
                "task_id": task_id,
                "action": "status_changed",
                "details": f"Status changed to {new_status.value}",
                "timestamp": now.isoformat(),
            }
        )
    else:
        _activity.append(
            {
                "id": str(uuid4()),
                "task_id": task_id,
                "action": "updated",
                "details": f"Task updated",
                "timestamp": now.isoformat(),
            }
        )

    return updated


def delete_task(task_id: str) -> bool:
    """Remove a task record if it exists.

    Args:
        task_id: The unique identifier of the task to delete.

    Returns:
        `True` when the task is removed, otherwise `False`.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        # log deleted event
        now = datetime.now(timezone.utc)
        _activity.append(
            {
                "id": str(uuid4()),
                "task_id": task_id,
                "action": "deleted",
                "details": "Task deleted",
                "timestamp": now.isoformat(),
            }
        )
        return True
    return False


def get_activity() -> list[dict]:
    """Return all recorded activity entries newest first.

    Returns:
        A list of activity dictionaries sorted by timestamp in descending order.
    """
    # return activity newest first
    return sorted(_activity, key=lambda e: e["timestamp"], reverse=True)


def get_task_activity(task_id: str) -> list[dict]:
    """Return the activity entries for a single task.

    Args:
        task_id: The unique identifier of the task whose activity should be
            returned.

    Returns:
        A list of activity dictionaries associated with the task.
    """
    return [e for e in get_activity() if e["task_id"] == task_id]
