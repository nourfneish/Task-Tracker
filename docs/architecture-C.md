# Task Tracker — Architecture (Strategy C)

## 1. What the app does

Task Tracker is a FastAPI REST API for creating, retrieving, filtering, updating, deleting, and tracking activity for tasks. It keeps task and activity data in process memory.

## 2. Data model

- **Task** (`TaskResponse`): `id`, `title`, `description`, `status`, `priority`, `assignee`, `created_at`, and `updated_at`.
- **Create payload** (`TaskCreate`): title plus optional description, status, priority, and assignee.
- **Update payload** (`TaskUpdate`): optional versions of editable task fields.
- **Status values**: `ToDo`, `InProgress`, `Done`.
- **Priority values**: `Low`, `Medium`, `High`.
- **Activity record**: dictionary containing `id`, `task_id`, `action`, `details`, and `timestamp`.

## 3. Request flow: create a task

1. `POST /tasks` accepts a `TaskCreate` payload.
2. The title is trimmed, must be non-blank, and must be at most 200 characters; unknown payload fields are forbidden.
3. `app.main.create_task` passes the validated payload to `storage.add_task`.
4. Storage generates a UUID and UTC creation/update timestamps, creates a `TaskResponse`, and stores it in an in-memory dictionary.
5. Storage records a `created` activity event, then the API returns the task with HTTP 201.

## 4. Key files

- `app/main.py` — FastAPI application, routes, CORS configuration, and HTTP error handling.
- `app/models.py` — Task enums and request/response validation models.
- `app/storage.py` — In-memory task and activity storage operations.
- `app.business_rules` — Imported for status-transition validation; contents are not visible from the files I read.
- `app.api.health` — Imported health router; contents are not visible from the files I read.

## 5. Conventions

- **Validation:** Pydantic models forbid unknown fields; titles are stripped and validated for blank and maximum-length values.
- **Storage:** Tasks are held in a dictionary keyed by UUID; activity is held in a list. Both are in-memory only.
- **Error handling:** Missing task reads, updates, deletes, and task-specific activity requests explicitly raise HTTP 404. Status-transition validation is delegated to an imported module.
- **Frontend/backend interaction:** CORS allows selected localhost origins and all methods/headers. The actual frontend implementation is not visible from the files I read.

## 6. Not visible or assumptions

- Status-transition rules and the precise validation failure behavior are not visible from the files I read.
- The health endpoint path and behavior are not visible from the files I read.
- Frontend files, UI behavior, and the exact requests it sends are not visible from the files I read.
- Persistence beyond process memory, authentication, authorization, deployment, tests, logging, and API documentation beyond the route definitions are not visible from the files I read.
