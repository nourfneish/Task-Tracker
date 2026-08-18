# Final AI-assisted coding review

## AGENTS.md guardrails

Confirmed: AGENTS.md exists at the repo root and includes the required stack, run/test commands, project rules, and docs-first/read-first guardrails.

Evidence:
- Stack: Python, FastAPI/Pydantic, Uvicorn, pytest/TestClient, static HTML/CSS/JS.
- Run/test commands: `python -m venv venv`, `pip install -r requirements.txt`, `uvicorn app.main:app --reload --port 8000`, `pytest`, `python tests/verify_a.py`.
- Project rules: app-only edit guardrails, no destructive commands, no inventing requirements, citation of file evidence.
- Docs-first: “Follow a docs-first workflow,” “read the relevant documentation and implementation before proposing conclusions or changes.”

## AI code review mini-log

Changed file reviewed: `docs/ai-playbook.md`

1. Comment: “This playbook should be more specific to this repo and the actual AI tools being used.”
   Grade: Useful.
   Reason: It improves relevance because the repo has explicit AGENTS.md guardrails and the tools in use are Cursor/Copilot/Codex/Claude/ChatGPT.

2. Comment: “Add a decision card for tool selection by task type.”
   Grade: Useful.
   Reason: The doc was template-like and needed task-based guidance. This makes the playbook operational instead of generic.

3. Comment: “You should remove all placeholders and make the answers concrete.”
   Grade: Useful.
   Reason: The template was intentionally blank; replacing placeholders with repo-aware choices makes the file usable and reviewable.

4. Comment: “No need to mention repo guardrails; AI tools are just for code generation.”
   Grade: Wrong.
   Reason: AGENTS.md explicitly requires a docs-first workflow and read-only default, which are critical constraints in this repo.

5. Comment: “Use one AI tool for everything.”
   Grade: Noise.
   Reason: This ignores the task-fit differences between local editing, review, reasoning-heavy analysis, and infra planning.

## AI security mini-review

Read-only review reused from repo evidence and search results. Findings are intentionally limited to file-level evidence.

1. Finding: `app/core/config.py` loads environment variables from `.env` via `load_dotenv()`.
   File evidence: `app/core/config.py` imports `load_dotenv` and calls it at startup.
   Grade: Valid.
   Reason: This is a legitimate configuration behavior; it means secret values can be sourced from local env, so the image and deployment path must ensure they are not copied into a container inadvertently.

2. Finding: The app enables CORS.
   File evidence: `app/main.py` includes `CORSMiddleware` setup.
   Grade: Noise.
   Reason: This is not automatically a vulnerability in a local task tracker; it is a configuration choice that still needs validation for deployment context, but it is not a confirmed security issue from the repo alone.

3. Finding: There is a token-like or secret pattern in the repo search results.
   File evidence: Search hits include `secret`, `token`, and `dotenv` references in app files.
   Grade: False Positive.
   Reason: The search hits are generic references to configuration patterns and do not show actual secret values or leaks; they are only contextual code references.

4. Finding: No hard-coded credentials or `.env` contents appear in the checked-in repo files.
   File evidence: Read-only repo inspection did not reveal credential strings or secret material in the tracked project files.
   Grade: Valid.
   Reason: This is a positive control: the repo has no exposed credential values in the inspected source files.

## Manual check

I manually checked the project rules and the repo layout before accepting any AI guidance. The main risk I reviewed was whether the assistant was inventing commands or business rules. I found no unsupported claims in the main repo guidance because the AGENTS.md and README-backed commands line up with the project structure and test files.

## Rejected or corrected AI output

One AI suggestion I rejected was: “Use the same AI tool for everything and skip repo validation.” I corrected this by forcing a repo-first workflow and tool-fit approach. In practice, I used the repo’s actual guardrails and only kept suggestions that matched the stack, runtime behavior, and evidence in AGENTS.md and the associated app files.

## Ownership statement

I am comfortable submitting this repo as my own work because I verified the project guardrails, checked the repository evidence before accepting any output, and limited the use of AI to support tasks that were traceable to the actual files and tests. The final review is based on repo-local evidence, not vague assumptions or generic AI claims. I also rejected suggestions that would have skipped verification or invented requirements. This keeps the work grounded in the application’s real behavior and documented rules.
