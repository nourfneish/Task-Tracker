# Task Tracker Architecture

## What the app does

Task Tracker is a small task-management application with a browser-based Kanban board and a FastAPI REST API. Users can create, view, edit, move, filter, and delete tasks; the API also records activity for task creation, updates, status changes, and deletion.

## Data model

**Task** — server-owned `id` (UUID) and UTC `created_at`/`updated_at`; user fields are `title`, `description`, `status`, `priority`, and nullable `assignee`. Title is required; status values are ToDo, InProgress, and Done; priority values are Low, Medium, and High.

**Activity event** — a dictionary associated with a task: `id`, `task_id`, `action`, `details`, and ISO-8601 `timestamp`. Events are created for task lifecycle changes.

## Request flow: create a task

1. The browser form trims the title, collects task fields, and sends a JSON POST to `/tasks` at `http://localhost:8000`.
2. FastAPI parses the body as `TaskCreate`; Pydantic rejects unknown fields and invalid values, including blank or over-200-character titles.
3. The create endpoint calls the storage layer. It generates a UUID and UTC timestamps, builds a `TaskResponse`, stores it in memory, and appends a `created` activity event.
4. The API returns the task with HTTP 201. The frontend closes the modal and reloads `/tasks` to render the updated board; errors are displayed in the form.

## Key files

| File | Responsibility |
| --- | --- |
| `app/main.py` | FastAPI application, task/activity routes, CORS configuration, and health-router registration. |
| `app/models.py` | Task enums and Pydantic create, update, and response schemas. |
| `app/storage.py` | In-memory task and activity storage plus CRUD operations. |
| `app/business_rules.py` | Permitted task status-transition validation. |
| `app/api/health.py` | `/health` endpoint and UTC health response. |
| `app/schemas/health.py` | Health-response schema. |
| `frontend/index.html` | Standalone HTML/CSS/JavaScript Kanban client and API calls. |
| `tests/test_tasks.py` | Endpoint, validation, filtering, transition, and deletion behavior tests. |
| `tests/test_activity.py` | Activity-recording and ordering tests. |
| `requirements.txt` | Runtime and test dependencies. |

## Conventions

- **Validation:** create/update schemas forbid extra request fields; titles are trimmed and must be non-blank and at most 200 characters. Defaults are ToDo, Medium, and an empty description.
- **Business rules:** only ToDo → InProgress, InProgress → Done, and Done → InProgress transitions are allowed; an unchanged status is invalid.
- **Storage:** tasks and activities are process-local Python collections. Activity is returned newest first; data disappears when the process restarts.
- **Errors:** schema/enum failures and invalid transitions return HTTP 422; missing task resources return HTTP 404; successful create/delete use 201/204.
- **Frontend/backend:** the frontend calls the local API directly with `fetch`, initially loads `/tasks`, uses POST/PATCH for saves, and PATCH for permitted drag-and-drop moves. CORS permits common local frontend origins.

## Not visible or assumptions

No database, authentication/authorization, user identity model, production deployment topology, persistence/migration strategy, API versioning, rate limiting, logging/monitoring, or dedicated frontend build/dev server is visible in the inspected repository files. The README still describes the project as a skeleton with health checking, so it does not fully reflect the implemented task API and frontend.
