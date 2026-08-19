# app/main.py
# Entry point that creates and configures the FastAPI application instance.

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware

from app import storage
from app.api.health import router as health_router
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate, ActivityAction, ActivityEvent
from app.core.config import settings


# Create the FastAPI app instance.
app = FastAPI(
    title="Task Tracker API",
    description="A REST API for tracking tasks.",
    version="0.1.0",
)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    search: str | None = None,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee: str | None = None,
) -> list[TaskResponse]:
    """Return tasks matching optional filters and text search.

    Args:
        search: Optional case-insensitive text to match against task title and
            description.
        status: Optional status filter to apply before returning results.
        priority: Optional priority filter to apply before returning results.
        assignee: Optional assignee value to match exactly.

    Returns:
        list[TaskResponse]: Matching tasks from the in-memory task store.

    Raises:
        None.

    Example:
        GET /tasks?status=InProgress&priority=High&assignee=alice
    """
    tasks = storage.get_all_tasks(status=status, priority=priority)
    if assignee is not None:
        tasks = [t for t in tasks if t.assignee == assignee]
    if search is not None:
        needle = search.lower()
        tasks = [
            t
            for t in tasks
            if needle in t.title.lower() or needle in t.description.lower()
        ]
    return tasks


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task and record the creation activity event.

    Args:
        payload: Task creation payload containing required and optional task
            properties.

    Returns:
        TaskResponse: The newly created task with server-generated IDs and
            timestamps.

    Raises:
        ValidationError: If the request body violates the TaskCreate model rules.

    Example:
        POST /tasks
        {"title": "Ship release", "description": "Prepare QA notes", "status": "ToDo", "priority": "High", "assignee": "alice"}
    """
    task = storage.add_task(payload)
    storage.log_activity(
        task.id,
        ActivityAction.CREATED,
        f"Task '{task.title}' created",
    )
    return task


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Fetch a single task by identifier.

    Args:
        task_id: The unique identifier of the task to retrieve.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: Raised with status code 404 if the task does not exist.

    Example:
        GET /tasks/{task_id}
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Apply partial task updates, including status changes when valid.

    Args:
        task_id: The identifier of the task to update.
        payload: Partial update payload for the task fields to modify.

    Returns:
        TaskResponse: The updated task record.

    Raises:
        HTTPException: Raised with status code 404 when the task does not exist.
        HTTPException: Raised with status code 422 when a status transition is
            not allowed.

    Example:
        PATCH /tasks/{task_id}
        {"status": "InProgress"}
    """
    existing = storage.get_task_by_id(task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    if payload.status is not None:
        validate_status_transition(existing.status, payload.status)
    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    updates = payload.model_dump(exclude_unset=True)
    if updates:
        status_changed = (
            "status" in updates and updates["status"] != existing.status
        )
        if status_changed:
            storage.log_activity(
                task_id,
                ActivityAction.STATUS_CHANGED,
                f"Status changed from {existing.status.value} to {task.status.value}",
            )
        elif any(key != "status" for key in updates):
            storage.log_activity(
                task_id,
                ActivityAction.UPDATED,
                f"Task '{task.title}' updated",
            )
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task and log the deletion event.

    Args:
        task_id: The identifier of the task to delete.

    Returns:
        None: The endpoint returns no content on success.

    Raises:
        HTTPException: Raised with status code 404 if the task does not exist.

    Example:
        DELETE /tasks/{task_id}
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    storage.log_activity(
        task_id,
        ActivityAction.DELETED,
        f"Task '{task.title}' deleted",
    )
    storage.delete_task(task_id)


@app.get("/activity", response_model=list[ActivityEvent], tags=["activity"])
def list_activity() -> list[ActivityEvent]:
    """Return all recorded activity entries ordered newest first.

    Args:
        None.

    Returns:
        list[ActivityEvent]: A list of activity events sorted by timestamp in
            descending order.

    Raises:
        None.

    Example:
        GET /activity
    """
    return storage.get_all_activity()


@app.get("/tasks/{task_id}/activity", response_model=list[ActivityEvent], tags=["activity"])
def list_task_activity(task_id: str) -> list[ActivityEvent]:
    """Return activity events for a specific task.

    Args:
        task_id: The identifier of the task whose activity is requested.

    Returns:
        list[ActivityEvent]: Matching activity entries sorted newest first.

    Raises:
        HTTPException: Raised with status code 404 when the task does not exist.

    Example:
        GET /tasks/{task_id}/activity
    """
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return storage.get_activity_for_task(task_id)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "null",
    ],
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Register the health check route.
app.include_router(health_router)