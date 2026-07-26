# Mini Architecture Decision Record

## Context
The Task Tracker (FastAPI backend, in-memory storage, vanilla JS/HTML frontend) needed two additions: search/combined filters on the task list, and an activity log for create/update/delete/status-change events. Both had to be small, end-to-end, and testable without adding new infrastructure.

## Decision: Search + Combined Filters

**What we did:**
- Added `search`, `status`, `priority`, `assignee` as optional query parameters on the existing `GET /tasks` endpoint rather than creating a separate `/tasks/search` endpoint.
- `status` and `priority` are typed as their existing `Enum` classes so FastAPI/Pydantic validates them automatically and returns `422` for bad values — no manual validation code needed.
- Search matches case-insensitively against `title` and `description` only (not assignee), applied in Python after status/priority filtering, since the dataset is in-memory and small.
- Filters are combined with AND semantics (all provided filters must match).
- Frontend: a single filter bar above the board with debounced text input (300ms) so search doesn't fire a request per keystroke, plus `select` dropdowns for status/priority and a "clear filters" button.

**Alternatives AI suggested and we rejected:**
- *A dedicated `/tasks/search` POST endpoint with a filter object in the body.* Rejected as unnecessary complexity — `GET` with query params is idiomatic REST for a read-only filter operation, keeps the existing `/tasks` contract intact, and doesn't require new frontend request-building logic.
- *Full-text search library (e.g. a trigram or fuzzy-match dependency).* Rejected as out of scope — the dataset is small and in-memory, so a plain substring `in` check on lowercase strings is sufficient and doesn't add a dependency.
- *Server-side pagination for filtered results.* Rejected as out of scope for this brief; the board is expected to hold a modest number of tasks, and pagination would touch the frontend rendering logic in ways not required by the acceptance criteria.

## Decision: Activity Log

**What we did:**
- Added an `ActivityEvent` model (`id`, `task_id`, `action`, `details`, `timestamp`) and an in-memory list in `storage.py`, mirroring the existing pattern used for tasks rather than introducing a database.
- `log_activity()` is called explicitly at the four points that matter: after create, after a non-status update, after a status-only update (as a distinct `status_changed` action with a human-readable "from X to Y" detail string), and after delete (logged *before* the task is removed from storage, so the id/title are still available).
- Exposed two read endpoints: `GET /activity` (global feed, newest first) and `GET /tasks/{id}/activity` (scoped to one task, 404 if the task doesn't exist).
- Frontend: a sticky activity panel next to the board (global feed) plus a per-task activity section, both simple lists — no filtering/pagination UI, since the brief asked for "simple and readable," not a full audit UI.

**Alternatives AI suggested and we rejected:**
- *Persisting activity in a separate file or SQLite table for durability.* Rejected — the whole app currently uses in-memory storage that resets on restart; adding real persistence for just the activity log would create an inconsistent storage model and is out of scope for this module.
- *Emitting activity via an event bus / pub-sub pattern (decoupling logging from the route handlers).* Rejected as over-engineered for four call sites in a single-file app; explicit calls in each route handler are easier to read and to test.
- *Excluding delete events entirely (to "avoid complexity" around already-removed tasks).* We considered this but rejected it — losing the record of a delete defeats the purpose of an audit trail. We resolved the ordering issue instead by logging before deleting from storage.

## Bugs found and fixed during implementation (not new features, but blocking correct behavior)
1. `app/main.py` had **two** `@app.patch("/tasks/{task_id}")` route definitions. FastAPI/Starlette matches routes in registration order, so the first (unvalidated) definition silently won, meaning invalid status transitions (e.g. `ToDo → Done`) returned `200` instead of the required `422`. Removed the duplicate and kept the version that calls `validate_status_transition`.
2. There was no `GET /tasks/{task_id}` endpoint, even though tests and the general REST contract expected one (returned `405 Method Not Allowed`). Added it.
3. `app/main.py` had several duplicated import lines from iterative AI edits. Cleaned up to a single import block.
