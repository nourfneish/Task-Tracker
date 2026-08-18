# Comments on Tasks: Design Plan

## 1. Data Model

Add comment-specific Pydantic models to `app/models.py`, alongside the existing `TaskCreate`, `TaskUpdate`, and `TaskResponse` models. The observed convention is to separate client input models from response models and set `model_config = ConfigDict(extra="forbid")` on each, so the proposed models are:

- `CommentCreate`: accepts `author` and `body` only. It deliberately does not accept `id`, `task_id`, or `created_at`; the task reference comes from the route path and the other two values are server-owned.
- `CommentResponse`: returns `id`, `task_id`, `author`, `body`, and `created_at`.

`CommentCreate.author` should validate to a non-blank, trimmed string of at most 100 characters. `CommentCreate.body` should validate to a non-blank string of at most 2,000 characters. `TaskCreate` and `TaskUpdate` validate titles by stripping whitespace before the non-blank and maximum-length checks; comments should follow that established validation pattern. Whether `body` is returned trimmed or preserved after non-blank validation is not visible in the repository and should be decided before implementation.

Store comments independently in `app/storage.py`, rather than adding them to `TaskResponse`. `TaskResponse` has a closed response shape and represents the existing task resource; embedding comments would change every task list and detail response. A separate in-memory comment collection—such as a dictionary keyed by comment ID or a list of `CommentResponse` values—fits the module's current `_tasks` dictionary and `_activity` list. Its creation helper should generate `str(uuid4())` and `datetime.now(timezone.utc)`, matching `add_task`.

The storage reset helper, `storage._reset()`, must also clear the comment collection so the autouse fixture in `tests/conftest.py` continues to isolate tests.

## 2. API Routes

Routes should be declared directly in `app/main.py`, where all current task and activity routes live. The only currently separate router is the health router imported from `app.api.health`; there is no observed task router abstraction to extend.

### Create a comment

`POST /tasks/{task_id}/comments`

Request body:

- `author` (required string, 1–100 characters after the selected whitespace policy)
- `body` (required string, 1–2,000 characters after the selected whitespace policy)

Success response: HTTP 201 with a `CommentResponse` body containing a server-generated UUID `id`, the route's `task_id`, and a UTC `created_at` datetime. The existing `POST /tasks` route uses HTTP 201 and a response model, which this route should mirror.

Errors:

- HTTP 404 if `task_id` does not identify an existing task. Existing nested activity routing uses `Task with id {task_id} not found` for this case; reuse that detail format for consistency.
- HTTP 422 for missing, blank, oversized, malformed, or unknown request fields. FastAPI/Pydantic currently produces HTTP 422 for input model failures, and `extra="forbid"` rejects unknown fields.
- HTTP 422 if a client supplies `id`, `task_id`, or `created_at`, because those fields are not in `CommentCreate`.

### List a task's comments

`GET /tasks/{task_id}/comments`

Request body: none.

Success response: HTTP 200 with `list[CommentResponse]`. Define and document the ordering as oldest-first by `created_at` (with a deterministic tie-breaker if needed); this is a proposed choice, not a current repository convention. The existing global activity endpoint is explicitly newest-first, while the task activity endpoint inherits that order; no current comment ordering convention exists.

Errors:

- HTTP 404 with the existing task-not-found detail if the task does not exist, including when there would otherwise be no matching comments.

No comment retrieval, update, or deletion endpoints are included in this initial scope because the requested data shape defines creation metadata only and the repository currently has no user/authentication model. Those endpoints can be added later after ownership and moderation rules are decided.

## 3. Tests

Create `tests/test_comments.py`, following the repository's focused endpoint-test files (`tests/test_tasks.py` and `tests/test_activity.py`). Reuse the `client` and `created_task` fixtures from `tests/conftest.py`; those tests use FastAPI `TestClient`, `response.json()`, exact status assertions, and exact 404 `detail` assertions.

### Happy path

- `test_create_comment_valid_returns_201_with_full_body`
  - Create a fixture task, post valid `author` and `body`, and assert the returned task reference, submitted fields, UUID-shaped/present ID, and present timestamp.
- `test_list_task_comments_returns_200_and_comments_for_that_task`
  - Create comments on two tasks and assert the first task's listing contains only its comments.
- `test_list_task_comments_empty_returns_200_and_empty_list`
  - Create a task with no comments and assert an empty response list.
- `test_list_task_comments_returns_oldest_first`
  - Create two comments in sequence and assert the documented ordering. If implementation timestamps can tie, the implementation must use the corresponding deterministic tie-breaker.

### Validation

- `test_create_comment_missing_author_returns_422`
- `test_create_comment_blank_author_returns_422`
- `test_create_comment_author_over_100_characters_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_blank_body_returns_422`
- `test_create_comment_body_over_2000_characters_returns_422`
- `test_create_comment_unknown_field_returns_422`
- `test_create_comment_server_owned_fields_return_422`
  - Parameterize or split this into explicit checks for `id`, `task_id`, and `created_at`, matching the explicit server-owned-field checks in `tests/verify_a.py`.

Add corresponding direct Pydantic checks to `tests/verify_a.py` if that script remains the repository's model-verification script. It currently instantiates task models directly and prints pass/fail results; it is not a pytest test file.

### Edge cases

- `test_create_comment_for_missing_task_returns_404_with_detail`
- `test_list_task_comments_for_missing_task_returns_404_with_detail`
- `test_deleting_task_removes_or_handles_its_comments_according_to_the_selected_policy`
  - This test is intentionally policy-dependent; see Migration Notes and Open Questions.
- `test_storage_reset_clears_comments`
  - Add only if storage behavior is tested directly; the current suite verifies reset indirectly through the autouse fixture.

Activity behavior is not specified for comments. If the team decides comment creation should log activity, add `test_create_comment_logs_comment_created_event` to `tests/test_activity.py`, using the existing activity assertions and a defined action/detail format. Otherwise, add no activity assertion.

## 4. Frontend Changes

The frontend is a single static file, `frontend/index.html`, containing the markup, CSS, and vanilla JavaScript. No separate frontend module, component, or test setup is visible in the repository.

Change `frontend/index.html` as follows:

- Extend the existing edit-task modal (`#task-modal`) so that, when a persisted task is opened with the current **Edit** button, the user sees a Comments section beneath the task fields.
- Fetch `GET /tasks/{task_id}/comments` when the edit modal opens. Show an explicit loading state, an empty state when no comments exist, a readable list of existing comments (author, body, and `created_at`), and an inline retrieval error state.
- Add a small comment form with author and body inputs plus a submit button. Validate required inputs and character limits in the browser for immediate feedback, but continue showing server validation errors through the existing `parseErrorMessage` pattern.
- On submission, call `POST /tasks/{task_id}/comments`; add the returned comment to the modal list or refetch that list, clear only the comment form, and retain the task-edit form values.
- Render author and body through the existing `escapeHtml` helper. `renderBoard` already escapes task fields before interpolating HTML, so comments should use the same protection.
- Do not show the comment form in **New Task** mode: a task ID does not exist until the current `POST /tasks` succeeds. After creation, the user can reopen that task with **Edit** to add a comment. A different post-create navigation flow is not visible in the current frontend and would be a product decision.

The board itself should remain task-focused. Its cards currently show title, optional description, priority, assignee, and an **Edit** button; adding full comments to cards would create unbounded content in Kanban columns. A comment count badge is optional and would require either list requests per task or an API response-shape decision not in this initial design.

## 5. Migration Notes

`app/storage.py` is explicitly in-memory: `_tasks` and `_activity` live in process memory and `storage._reset()` clears them. No database schema, ORM, migration framework, or durable data file is visible. Therefore no database migration is currently required, and all comments will be lost on server restart just as tasks and activity are.

Implementation must add a dedicated comment collection and reset it in `_reset()`. It should not alter the existing `TaskResponse` shape unless the team separately chooses to expose comment summaries on tasks; existing tests compare complete task JSON, so an additional task field would require intentional compatibility updates.

Task deletion needs an explicit data-lifecycle rule. The recommended default for this in-memory implementation is cascade deletion of comments when `delete_task` removes a task, preventing orphaned comments that can no longer be retrieved via the nested routes. The current `delete_task` also retains a deleted task's activity record in `_activity`; whether comment-related activity follows that pattern is undecided.

There is no persistent existing task data to backfill, so existing in-memory tasks simply have zero comments after the feature is introduced. If persistence is introduced later, comments should be stored with a task ID reference and indexed/grouped by that reference; any migration would need to define referential integrity and delete behavior at that time.

## 6. Open Questions

1. Should comment bodies be trimmed before storage like task titles, or only checked with `body.strip()` for blankness while preserving author-entered leading/trailing whitespace?
2. Should creating a comment add an activity event? If yes, what action string and detail format should it use, and should it include the comment body?
3. On task deletion, should comments be cascade-deleted, retained for audit, or should deletion be refused while comments exist? This plan recommends cascade deletion but it is a product decision.
4. Is `author` intentionally free-form text, or should a future authentication system derive it from the current user? No user or authentication model is visible in the repository.
5. Do comments need editing, deletion, moderation, or immutable audit behavior? The requested model includes only `created_at`, so no update timestamp or ownership rule is currently defined.
6. Should the comments list be oldest-first as proposed, newest-first like `/activity`, or user-configurable?
7. Should a task list/card expose a comment count? Doing so efficiently may change the task response shape or require additional requests.

## Sources consulted

- `AGENTS.md` — project guardrails, API summary, and confirmed operational constraints.
- `app/models.py` — Pydantic model structure, validation, and forbidden extra fields.
- `app/main.py` — current route placement, response conventions, 404 detail strings, and CORS configuration.
- `app/storage.py` — in-memory collections, UUID/UTC generation, reset behavior, and activity conventions.
- `tests/conftest.py`, `tests/test_tasks.py`, `tests/test_activity.py`, and `tests/verify_a.py` — test fixtures, assertion style, and direct model-verification convention.
- `frontend/index.html` — single-file frontend structure, edit modal, API fetch/error handling, and escaped HTML rendering.
- `README.md` — documented server command and API base URL.

## Generic vs Repo-Grounded Codex Comparison

**Biggest difference:** The generic plan described a sensible comments feature, while the repo-grounded plan identifies the exact existing conventions it must fit: Pydantic models in `app/models.py`, direct routes in `app/main.py`, resettable in-memory storage in `app/storage.py`, and a single-file edit modal in `frontend/index.html`.

**Plan I would hand to a teammate:** Use the repo-grounded plan. It gives concrete route behavior, test names, storage/reset work, frontend touchpoints, and explicitly calls out decisions that are not already settled by this codebase.

**Where the generic plan was still useful:** It quickly established the core entity, nested REST routes, expected validation coverage, and product questions such as ordering, deletion, and comment ownership.

**Where repo grounding mattered most:** It prevented incorrect assumptions about persistence and frontend structure, preserved the project's existing 404 and validation conventions, and revealed that comments should be added to the existing edit modal rather than an assumed separate task-detail page.
