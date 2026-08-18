# Task Tracker Architecture

## What the app does

Task Tracker is a FastAPI REST API with a standalone browser-based Kanban frontend. Users can create, view, filter, update, move, and delete tasks; the API also records task activity and exposes a health check. All task and activity data is held in memory.

## Data model

**Task** — `id` (UUID string), `title`, `description`, `status`, `priority`, `assignee`, `created_at`, and `updated_at`. Titles are required; status values are `ToDo`, `InProgress`, and `Done`; priority values are `Low`, `Medium`, and `High`.

**Activity event** — `id`, `task_id`, `action`, `details`, and `timestamp`. Events are recorded when tasks are created, updated, have their status changed, or are deleted.

## Request flow: create a task

1. The frontend collects task fields and sends `POST /tasks` as JSON.
2. FastAPI parses the request into `TaskCreate` and rejects invalid or unknown fields.
3. `app.main.create_task` passes the validated payload to in-memory storage.
4. Storage generates a UUID and UTC timestamps, creates a `TaskResponse`, stores it, and records a `created` activity event.
5. The API returns the new task with HTTP 201; the frontend reloads the task list.

## Key files

- `app/main.py` — FastAPI application, task/activity routes, CORS, and route registration.
- `app/models.py` — Pydantic task request/response models, enums, defaults, and title validation.
- `app/storage.py` — In-memory task and activity collections plus CRUD operations.
- `app/business_rules.py` — Allowed task-status transition validation.
- `app/api/health.py` — `GET /health` implementation.
- `app/schemas/health.py` — Health-response schema.
- `frontend/index.html` — Static Kanban UI, API calls, editing, drag-and-drop status changes, and UI error states.
- `tests/test_tasks.py` — API tests for task creation, retrieval, filtering, updates, transitions, and deletion.
- `tests/test_activity.py` — Activity logging and ordering tests.

## Conventions

- **Validation:** Pydantic request models forbid unknown fields. Titles are trimmed, non-blank, and limited to 200 characters. Server-owned `id` and timestamp fields are not accepted in create/update payloads.
- **Storage:** Data is maintained in process-local dictionaries/lists; restarting the API clears it. Storage generates IDs and UTC timestamps.
- **Error handling:** Schema and invalid status-transition failures return HTTP 422. Missing tasks return HTTP 404. Successful creation returns 201; successful deletion returns 204.
- **Status rules:** Allowed transitions are `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress`; sending the unchanged status is invalid.
- **Frontend/backend interaction:** The frontend calls `http://localhost:8000` using `fetch`, loads tasks with `GET /tasks`, submits creates/edits with `POST`/`PATCH`, and performs optimistic status moves with rollback on failure. Backend CORS permits configured local development origins.

## Not visible or assumptions

No persistent database, authentication/authorization, production deployment configuration, API versioning strategy, or confirmed standalone frontend development-server command is visible. Activity events are returned as dictionaries rather than a dedicated declared response schema.
