Verification
1. Baseline Check

Before making any changes, I ran the test suite against the repo as pulled from Modules 1-3.

Result: 26 passed, 4 failed

Failures:

test_get_task_by_id_returns_task → got 405, expected 200
test_get_task_by_id_not_found_returns_404_with_detail → got 405, expected 404
test_patch_invalid_transition_todo_to_done_returns_422 → got 200, expected 422
test_patch_same_status_returns_422 → got 200, expected 422

Root causes:

No GET /tasks/{task_id} route existed at all.
update_task was defined twice under the same route. FastAPI matches by registration order, so the first (unvalidated) definition silently won — making the second, validated definition dead code.

Both were pre-existing bugs in the starter repo, not introduced by this work.

2. Backend Test Results (after fixes + both features)

Result: 30 passed in 0.17s

Test file	Coverage
test_tasks.py (23 tests)	CRUD, search, status/priority filters, combined filters, invalid-filter 422s, status validation, new GET /tasks/{id}
test_activity.py (7 tests)	created/updated/status_changed/deleted events, feed ordering, per-task scoping

Also ran tests/verify_a.py, a standalone Pydantic contract check — all 8 assertions passed (blank/whitespace/oversized titles rejected, defaults applied correctly, extra fields and invalid enums rejected).

3. Manual "Browser-Equivalent" Checks

The frontend already had a filter bar and activity panel wired to these endpoints, so I ran the live server and exercised the same requests via curl.

Check	Request	Result
Search matches title/description	GET /tasks?search=login	Only the matching task returned
Combined filter	GET /tasks?status=ToDo&priority=High	Only tasks matching both
No-match search	GET /tasks?search=zzzznotfound	200, []
Invalid filter value	GET /tasks?status=NotAStatus	422
Status change → activity	PATCH status, then GET .../activity	status_changed event, "from ToDo to InProgress"
Invalid transition rejected	PATCH ToDo on an InProgress task	422, no event logged
Delete → activity	DELETE, then GET /activity	204; deleted event still present after task was gone
4. Behavior Contract: Before vs. After
Endpoint	Before	After
GET /tasks/{id}	405 (route missing)	200 or 404
PATCH invalid transition	200, silently applied	422, unchanged, no event logged
PATCH no-op status	200	422
PATCH valid transition	200	200 (unchanged)
GET /tasks filters, GET /activity	Already correct	Unchanged, reconfirmed after cleanup

No response schemas changed. The only behavior change: invalid transitions and single-task lookups now follow the documented contract instead of silently doing the wrong thing.

5. Break Test Evidence

Break Test 1 — reintroduce the duplicate/unvalidated PATCH route

Re-added the unvalidated route ahead of the validated one to reproduce the original bug:

FAILED test_patch_invalid_transition_todo_to_done_returns_422 - assert 200 == 422
FAILED test_patch_same_status_returns_422 - assert 200 == 422

Reverted → 3 passed

Break Test 2 — narrow search to title-only

Removed the description half of the search condition:

FAILED test_list_tasks_search_matches_description - assert 0 == 1

Reverted → 30 passed

Both break tests confirm the suite actually detects regressions in these features rather than passing vacuously.