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
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
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
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def log_activity(task_id: str, action: ActivityAction, details: str) -> ActivityEvent:
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
    return sorted(_activity_events, key=lambda e: e.timestamp, reverse=True)


def get_activity_for_task(task_id: str) -> list[ActivityEvent]:
    events = [e for e in _activity_events if e.task_id == task_id]
    return sorted(events, key=lambda e: e.timestamp, reverse=True)


def _reset() -> None:
    _tasks.clear()
    _activity_events.clear()
