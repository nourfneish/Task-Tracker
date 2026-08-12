# app/main.py
# Entry point that creates and configures the FastAPI application instance.

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.api.health import router as health_router
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate


# Create the FastAPI app instance.
app = FastAPI(
    title="Task Tracker API",
    description="A REST API for tracking tasks.",
    version="0.1.0",
)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[TaskResponse]:
    """Return all tasks, optionally filtered by status or priority.

    Args:
        status: Optional task status filter. Only tasks matching this value are
            returned when provided.
        priority: Optional priority filter. Only tasks matching this value are
            returned when provided.

    Returns:
        A list of task resources matching the supplied filters.

    Example:
        GET /tasks?status=ToDo&priority=High
    """
    return storage.get_all_tasks(status=status, priority=priority)


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task and return the created resource.

    Args:
        payload: A task creation payload containing the task title, optional
            description, status, priority, and assignee.

    Returns:
        The newly created task representation, including server-generated IDs and
        timestamps.

    Raises:
        ValidationError: If the request body violates the `TaskCreate` schema,
            such as a blank title or an overly long title.

    Example:
        POST /tasks
        {
          "title": "Draft sprint plan",
          "description": "Review backlog and milestones",
          "status": "ToDo",
          "priority": "High",
          "assignee": "alex"
        }
    """
    return storage.add_task(payload)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Fetch a single task by its identifier.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The matching task resource.

    Raises:
        HTTPException: If no task exists for the supplied `task_id`.

    Example:
        GET /tasks/123e4567-e89b-12d3-a456-426614174000
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Update a task's fields and return the updated resource.

    Args:
        task_id: The unique identifier for the task to update.
        payload: A partial task update payload, containing only fields that need
            to change.

    Returns:
        The updated task resource.

    Raises:
        HTTPException: If the task does not exist.
        HTTPException: If a status transition is invalid and the status field is
            being changed.

    Example:
        PATCH /tasks/123e4567-e89b-12d3-a456-426614174000
        {
          "status": "InProgress",
          "priority": "Medium"
        }
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        # validate transition (may raise 422)
        validate_status_transition(existing.status, payload.status)
    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by identifier.

    Args:
        task_id: The unique identifier for the task to delete.

    Returns:
        None. The endpoint responds with a 204 No Content status on success.

    Raises:
        HTTPException: If no task exists for the provided `task_id`.

    Example:
        DELETE /tasks/123e4567-e89b-12d3-a456-426614174000
    """
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


@app.get("/activity", tags=["activity"])
def get_activity():
    """Return the most recent activity events, newest first.

    Returns:
        A list of activity records sorted by timestamp in descending order.
        Each record includes an `id`, `task_id`, `action`, `details`, and
        `timestamp` field.

    Example:
        GET /activity
    """
    return storage.get_activity()


@app.get("/tasks/{task_id}/activity", tags=["activity"])
def get_task_activity(task_id: str):
    """Return activity events associated with a single task.

    Args:
        task_id: The unique identifier for the task whose activity should be
            returned.

    Returns:
        A list of activity records for the given task.

    Raises:
        HTTPException: If no task exists for the supplied `task_id`.

    Example:
        GET /tasks/123e4567-e89b-12d3-a456-426614174000/activity
    """
    # ensure task exists
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return storage.get_task_activity(task_id)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "null",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register the health check route.
app.include_router(health_router)