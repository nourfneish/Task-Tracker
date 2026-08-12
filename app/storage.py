from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}
_activity: list[dict] = []


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


def _reset() -> None:
    _tasks.clear()
    _activity.clear()


def get_activity() -> list[dict]:
    # return activity newest first
    return sorted(_activity, key=lambda e: e["timestamp"], reverse=True)


def get_task_activity(task_id: str) -> list[dict]:
    return [e for e in get_activity() if e["task_id"] == task_id]
