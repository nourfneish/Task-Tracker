Search + Combined Filters

Implementation: Added search, status, priority, assignee as optional query params on the existing GET /tasks endpoint rather than a new route. status/priority use the existing Enum types so Pydantic validates them and returns 422 automatically. Search is a case-insensitive substring match on title + description, combined with the other filters via AND. Frontend: one filter bar with a debounced (300ms) search box, status/priority dropdowns, and a clear button.

Rejected alternatives:

Separate /tasks/search POST endpoint : unnecessary; GET + query params is simpler and idiomatic.
Full-text/fuzzy search library : overkill for a small in-memory dataset.
Server-side pagination : out of scope for this brief.
Activity Log

Implementation: Added an ActivityEvent model and in-memory list in storage.py, matching the existing task-storage pattern. log_activity() is called at four points: create, non-status update, status-only update (logged as status_changed with a "from X to Y" detail), and delete (logged before removal so the id/title are still available). Exposed GET /activity (global, newest-first) and GET /tasks/{id}/activity (scoped, 404 if unknown). Frontend: a sticky global activity panel plus a per-task section — no filtering/pagination, per the "simple and readable" brief.

Rejected alternatives:

File/SQLite persistence : inconsistent with the rest of the app's in-memory model.
Event bus/pub-sub : over-engineered for four call sites.
Skipping delete events : defeats the point of an audit trail; solved by logging before deletion instead.
Bugs found and fixed (pre-existing, not new features)
main.py had two PATCH /tasks/{task_id} routes; the first (unvalidated) one silently won, so invalid status transitions returned 200 instead of 422. Removed the dead duplicate.
GET /tasks/{task_id} didn't exist (405 instead of 200/404). Added it.
Cleaned up duplicated import lines left over from iterative edits.