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
    task = storage.add_task(payload)
    storage.log_activity(
        task.id,
        ActivityAction.CREATED,
        f"Task '{task.title}' created",
    )
    return task


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
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
    return storage.get_all_activity()


@app.get("/tasks/{task_id}/activity", response_model=list[ActivityEvent], tags=["activity"])
def list_task_activity(task_id: str) -> list[ActivityEvent]:
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
