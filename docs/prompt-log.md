**Activity Log Feature**

**1. Backend Prompt **

Add an activity log to this FastAPI project. Keep it minimal — don't refactor or restructure anything else.
Add a simple in-memory list to store activity events (same style as the existing task storage — no database). Each event needs: id, task_id, action (one of "created", "updated", "deleted", "status_changed"), a short description or details string, and a timestamp.
Record an event whenever a task is created, updated, deleted, or its status changes. Add this inside the existing create/update/delete endpoint logic — don't rewrite those endpoints beyond adding the logging call.
Add two GET endpoints:
- `GET /activity` — returns all events, most recent first.
- `GET /tasks/{id}/activity` — returns events for just that task, most recent first. Return 404 if the task doesn't exist.
Only touch the task endpoints (to add logging calls), the new activity storage/model, and the two new endpoints. Don't change unrelated routes or file structure.


AI returned typed search/status/priority/assignee query params with AND-combined filtering logic and 9 matching tests, and I accepted it all as-is after confirming status/priority used the existing Enum types so 422-on-invalid-value came for free from Pydantic.


**2. Tests Prompt**

Add tests for: creating a task logs a "created" event, updating a task logs an "updated" event, deleting a task logs a "deleted" event, changing status logs a "status_changed" event, `GET /activity` returns events in most-recent-first order, and `GET /tasks/{id}/activity` returns only that task's events (and 404s for an unknown task).

**3. Frontend Prompt (HTML/CSS/JS)**
Add a simple activity view to this vanilla HTML/CSS/JS task tracker frontend. The API now has `GET /activity` (all events) and `GET /tasks/{id}/activity` (events for one task), each returning a list of events with action, description, and timestamp, most recent first.
Add a small activity panel (e.g. a sidebar section or a collapsible panel) that fetches and lists recent events from `GET /activity`. Show action + description + a readable relative or formatted timestamp per entry. Keep it a plain list — no pagination or filtering needed.
On the task detail/edit view (wherever a single task is opened), add a small "Activity" section that fetches and shows that task's events from `GET /tasks/{id}/activity`.
Keep both views read-only and simple — no editing, deleting, or real-time updates needed. A manual refresh or refetch on open is enough.
Keep it minimal — reuse existing styles, API helper functions, and layout patterns already in the codebase. Don't introduce new libraries, don't restructure existing files, and don't touch anything unrelated to the activity log.

AI returned a .filter-bar with a debounced search input, status/priority selects, an assignee field, a clear button, and a buildTaskQueryParams() helper wired into the existing fetchTasks() flow, and I accepted it fully after manually verifying the debounce timing and clear-button state in the running app.

**Search + Combined Filters Feature**

**Backend Prompt (FastAPI)**
Extend the existing GET /tasks endpoint in this FastAPI project to support search and combined filters. Keep it minimal — don't refactor or restructure anything else.
Add an optional `search` query param that matches (case-insensitive, substring) against task title and description.
Add optional query params for the filters that already exist as task fields — e.g. `status`, `priority`, `assignee`, and `tag`/`due_date`-related filters if those fields exist in this project. If a param has a fixed set of valid values (e.g. status or priority enums), validate it and return 422 for an invalid value; if it's a free-text field (e.g. assignee), just match it directly with no validation needed.
All params should combine with AND logic — e.g. `status=open&priority=high&search=login` returns only tasks matching all three. Any subset of params can be used together, and none are required. No matches should return a normal 200 with an empty list `[]`, not an error.
Only touch the GET /tasks endpoint and its query handling. Don't change other endpoints, the task model, or file structure.

AI returned the correct diagnosis (the description half of the or condition had been dropped) and a one-line fix, which I accepted outright and confirmed with a full suite rerun (30 passed).

**Tests Prompt**
Add tests for: search matches on title, search matches on description, combining two filters (e.g. status + priority) returns only tasks matching both, no matches returns 200 with `[]`, and an invalid value for a validated filter (e.g. bad status/priority) returns 422.

**Frontend Prompt**
Add a compact search + filter bar to this vanilla HTML/CSS/JS task tracker frontend, above the existing board. The GET /tasks endpoint now supports combinable query params: `search` (matches title/description) plus filters for whichever task fields exist in this app (e.g. `status`, `priority`, `assignee`, `tag`/`due_date`). No matches returns an empty list, not an error.
Add a single-line search input and small filter controls (dropdowns or similar, matching whatever filter UI already exists) in one compact bar above the board. Only include filter controls for fields that actually exist on tasks in this app.
Combine all active search/filter values into one request to GET /tasks whenever any of them change (debounce the search input slightly, e.g. 300ms, so it doesn't fire on every keystroke).
Keep the existing board/column layout intact — columns should stay visible even when a filter returns few or no tasks. Use the app's existing empty-state pattern for a column/board with no matching tasks (don't invent a new one).
Add a simple way to clear all search/filter values back to showing everything.
Keep it minimal — reuse existing styles, API helper functions, and layout patterns already in the codebase. Don't introduce new libraries, don't restructure existing files, and don't touch anything unrelated to search/filtering.


AI returned the ActivityEvent model, storage functions, both GET endpoints, and 7 tests, and I accepted all of it except the update-logging branch, which I edited so a status-only PATCH logs status_changed exclusively instead of also firing a redundant updated event.