# AGENTS.md

## Project summary

Module 5 Task Tracker is a small FastAPI REST API with a standalone browser frontend.

- The API supports task creation, retrieval, filtering, partial updates, deletion, health checks, and activity history. See `app/main.py`.
- Task data and activity are held in process memory only; restarting the server clears them. See `app/storage.py`.
- The frontend is a static Kanban-style page that calls `http://localhost:8000`. See `frontend/index.html`.

## Tech stack

- Python
- FastAPI and Pydantic
- Uvicorn
- pytest and FastAPI TestClient
- Static HTML, CSS, and vanilla JavaScript frontend

Dependencies are listed in `requirements.txt`.

## Confirmed setup, run, and test commands

From the repository root:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Run the test suite:

```powershell
pytest
```

Run the standalone validation script:

```powershell
python tests/verify_a.py
```

The API health endpoint is:

```text
GET http://localhost:8000/health
```

These commands are supported by `README.md`, `requirements.txt`, and the checked-in test files. A dedicated frontend development-server command is **not confirmed**.

## API behavior and business rules

### Task model

Tasks have these fields:

- `id`: server-generated UUID string.
- `title`: required; leading and trailing whitespace is stripped; it must be non-blank and no longer than 200 characters.
- `description`: optional; defaults to an empty string.
- `status`: `ToDo`, `InProgress`, or `Done`; defaults to `ToDo`.
- `priority`: `Low`, `Medium`, or `High`; defaults to `Medium`.
- `assignee`: optional and may be `null`.
- `created_at` and `updated_at`: server-generated UTC timestamps.

Create and update payloads reject unknown fields. Clients cannot supply server-owned fields such as `id` or timestamps. See `app/models.py` and `tests/verify_a.py`.

### Status transitions

The only permitted status changes are:

```text
ToDo       -> InProgress
InProgress -> Done
Done       -> InProgress
```

A PATCH that supplies the current status unchanged is invalid. Invalid transitions return HTTP 422. See `app/business_rules.py` and `app/main.py`.

### Endpoints and persistence

- `GET /tasks` lists tasks and accepts optional `status` and `priority` filters.
- `POST /tasks` creates a task and returns HTTP 201.
- `GET /tasks/{task_id}` returns HTTP 404 when the task does not exist.
- `PATCH /tasks/{task_id}` partially updates a task and returns HTTP 404 when absent.
- `DELETE /tasks/{task_id}` returns HTTP 204 on success and HTTP 404 when absent.
- `GET /activity` returns activity newest first.
- `GET /tasks/{task_id}/activity` returns activity for one existing task; a missing task returns HTTP 404.
- Creating, updating, changing status, and deleting tasks record activity events.

Data is in-memory only and is not durable across process restarts. See `app/storage.py`.

## Module 5 guardrails

- Follow a docs-first workflow: read the relevant documentation and implementation before proposing conclusions or changes.
- Default to read-only inspection. Do not modify repository files unless the user explicitly asks for the specific change.
- Keep one discrete task per Codex task/thread. Do not combine unrelated work without explicit user direction.
- Do not edit anything under `app/` unless the user explicitly approves that application change.
- If a command, behavior, requirement, or business rule is not visible in repository sources, mark it **not confirmed** rather than inferring it.

## Security and governance

- Never paste, log, commit, or expose secrets, API keys, tokens, credentials, or `.env` contents.
- Do not run destructive commands or irreversible operations without explicit user authorization and a verified target.
- Cite the relevant repository file(s) for findings, proposed changes, and behavior claims.
- Do not invent findings, tests, commands, requirements, or implementation details. State uncertainty clearly.
- Preserve user changes and avoid unrelated edits.
