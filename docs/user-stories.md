# User Stories

## Feature 1: Search + Combined Filters

**Story 1 — Free-text search**
As a user with a large board, I want to search tasks by keyword so that I can find a specific task without scrolling through every column.
- Acceptance criteria:
  - `GET /tasks?search=<term>` matches the term case-insensitively against title and description.
  - A search with no matches returns `200 OK` with `[]`, not an error.
  - The frontend search box is debounced (300ms) so it doesn't fire a request per keystroke.

**Story 2 — Filter by status**
As a user, I want to filter the board by status so that I can focus on tasks that are still To Do, In Progress, or Done.
- Acceptance criteria:
  - `GET /tasks?status=ToDo` returns only tasks with that status.
  - An invalid status value (e.g. `status=Bogus`) returns `422` with a validation error, not a silently-empty list.
  - Columns stay visible on the board even when a filter empties them (empty state per column, not a blank page).

**Story 3 — Filter by priority**
As a user, I want to filter by priority so that I can see what's urgent first.
- Acceptance criteria:
  - `GET /tasks?priority=High` returns only High-priority tasks.
  - Invalid priority values return `422`.

**AI assumption corrected:** The first draft the AI produced for `GET /tasks` treated an unrecognized `status` value as "no filter applied" (i.e. it would silently return the unfiltered list instead of rejecting the request). That's the wrong contract for this project — the brief explicitly requires `422` on an invalid filter value. I corrected the endpoint to declare `status: TaskStatus | None` as a typed enum query parameter so FastAPI validates it and returns `422` automatically, and added a test (`test_list_tasks_invalid_status_returns_422`) to lock that behavior in.

---

## Feature 2: Activity Log

**Story 1 — Log task creation**
As a user, I want every new task to generate a "created" event so that I have a record of when work entered the board.
- Acceptance criteria:
  - `POST /tasks` creates the task and appends a `created` activity event referencing the new task's id.
  - The event is visible immediately in `GET /activity`.

**Story 2 — Log field updates**
As a user, I want non-status edits (title, description, assignee, priority) to generate an "updated" event so that I can see what changed on a task over time.
- Acceptance criteria:
  - `PATCH /tasks/{id}` with any non-status field change logs an `updated` event.
  - No event is logged if the PATCH body doesn't actually change anything (`exclude_unset` semantics — omitted fields aren't treated as changes).

**Story 3 — Log status changes distinctly**
As a user, I want status changes (e.g. drag-and-drop between columns) to be logged as their own event type with the from/to values, so that I can tell "moved to Done" apart from a routine text edit.
- Acceptance criteria:
  - A status-only PATCH logs a `status_changed` event whose `details` field includes both the old and new status (e.g. "Status changed from ToDo to InProgress").
  - An invalid status transition (per `business_rules.py`) is rejected with `422` and does **not** log an event.


**AI assumption corrected:** The AI's first pass logged a generic `updated` event any time `PATCH` was called, including when the only field in the payload was `status`. That would have produced duplicate/noisy events (`status_changed` **and** `updated` for the same request). I corrected the logic so a status-only change logs `status_changed` and nothing else, while a mixed or non-status change logs `updated`, keeping one event per meaningful action.
