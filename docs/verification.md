# Verification

## 1. Baseline check (before any changes)

Ran the existing test suite against the repo exactly as it was pulled from Modules 1-3, before touching any code:

```
26 passed, 4 failed in 0.20s
```

Failures found at baseline:
- `test_get_task_by_id_returns_task` — `405 != 200`
- `test_get_task_by_id_not_found_returns_404_with_detail` — `405 != 404`
- `test_patch_invalid_transition_todo_to_done_returns_422` — `200 != 422`
- `test_patch_same_status_returns_422` — `200 != 422`

Root causes identified by reading `app/main.py`:
1. No `GET /tasks/{task_id}` route existed (only list/create/patch/delete), so single-task lookups returned `405 Method Not Allowed`.
2. `update_task` was defined **twice** with the same route (`@app.patch("/tasks/{task_id}")`). FastAPI matches routes in registration order, so the first definition (which does not call `validate_status_transition`) silently won, and the second, validated definition was dead code.

These were pre-existing bugs in the starter repo, not something introduced by this work — fixing them was a prerequisite for building the two features on solid ground.

## 2. Backend test results (after fixes + both features)

Full suite, verbose:

```
30 passed in 0.17s
```

Breakdown:
- `tests/test_tasks.py` — 23 tests covering CRUD, search, status/priority filters, combined filters, invalid-filter 422s, status-transition validation, and the newly added `GET /tasks/{id}`.
- `tests/test_activity.py` — 7 tests covering created/updated/status_changed/deleted events, global feed ordering, and per-task scoping (including 404 for unknown task).

Also ran the standalone Pydantic contract check:

```
$ PYTHONPATH=. python3 tests/verify_a.py
PASS: whitespace title rejected
PASS: empty title rejected
PASS: title > 200 chars rejected
PASS: defaults applied (status=ToDo, priority=Medium, description='')
PASS: extra field rejected on TaskCreate
PASS: id rejected on TaskCreate
PASS: created_at rejected on TaskUpdate
PASS: invalid status rejected
--- Part A verifications complete ---
```

## 3. Manual "browser-equivalent" checks

The frontend (`frontend/index.html`) already contained a filter bar and activity panel wired to these endpoints, so verification was done by running the live server (`uvicorn app.main:app`) and exercising the exact requests the frontend makes, via `curl`, matching what the network tab would show in a browser:

| Check | Request | Result |
|---|---|---|
| Search matches title/description | `GET /tasks?search=login` | Returned only the task whose title contained "login" |
| Combined filter | `GET /tasks?status=ToDo&priority=High` | Returned only the task matching both fields |
| No-match search | `GET /tasks?search=zzzznotfound` | `200 OK`, `[]` |
| Invalid filter value | `GET /tasks?status=NotAStatus` | `422`, Pydantic enum validation detail |
| Status change → activity | `PATCH /tasks/{id}` `{"status":"InProgress"}` then `GET /tasks/{id}/activity` | Logged a `status_changed` event with `"Status changed from ToDo to InProgress"` |
| Invalid transition rejected | `PATCH /tasks/{id}` `{"status":"ToDo"}` on an InProgress task | `422`, no activity event logged |
| Delete → activity | `DELETE /tasks/{id}` then `GET /activity` | `204` on delete; `deleted` event present in the global feed with the task's title, even after the task itself was gone |

Raw output for these checks is preserved in the implementation session; the table above summarizes the pass/fail outcome of each.

## 4. Behavior contract before/after refactor

| Endpoint | Before | After |
|---|---|---|
| `GET /tasks/{id}` | `405 Method Not Allowed` (route didn't exist) | `200` with the task, or `404` if not found |
| `PATCH /tasks/{id}` with an invalid status transition (e.g. `ToDo → Done`) | `200 OK`, task silently updated — no validation ran | `422 Unprocessable Entity`, task unchanged, no activity event logged |
| `PATCH /tasks/{id}` with the same status (no-op transition) | `200 OK` | `422 Unprocessable Entity` |
| `PATCH /tasks/{id}` with a valid transition (e.g. `ToDo → InProgress`) | `200 OK` | `200 OK` (unchanged — this path was already correct) |
| `GET /tasks` with search/status/priority/assignee | Already worked correctly | Unchanged — confirmed still correct after the `main.py` cleanup |
| `GET /activity`, `GET /tasks/{id}/activity` | Already worked correctly | Unchanged — confirmed still correct after cleanup |

No response schemas changed. The only behavior change is that invalid status transitions and single-task lookups now behave per the documented contract instead of silently doing the wrong thing.

## 5. Break Test evidence

**Break Test 1 — reintroduce the duplicate/unvalidated PATCH route.**
Temporarily re-added the old unvalidated `update_task` route ahead of the validated one (reproducing the original bug exactly), then ran the transition tests:

```
FAILED tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 - assert 200 == 422
FAILED tests/test_tasks.py::test_patch_same_status_returns_422 - assert 200 == 422
2 failed, 1 passed
```

Reverted the change and re-ran:

```
3 passed
```

**Break Test 2 — narrow search to title-only.**
Temporarily removed the `t.description.lower()` half of the search condition in `list_tasks`, then ran the search tests:

```
tests/test_tasks.py::test_list_tasks_search_matches_title PASSED
tests/test_tasks.py::test_list_tasks_search_matches_description FAILED
tests/test_tasks.py::test_list_tasks_search_no_matches_returns_200_and_empty_list PASSED
assert 0 == 1  (expected 1 task matching "oauth" in description, got 0)
```

Reverted the change and re-ran the full suite:

```
30 passed
```

Both break tests confirm the test suite actually detects regressions in the two features (rather than passing vacuously), which is the point of the exercise.
