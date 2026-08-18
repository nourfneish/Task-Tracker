# Personal AI Coding Playbook

## 1. When I reach for AI first

- Type of task or situation: Small-to-medium implementation work, refactors, test-writing, API design, and bug triage in Python/FastAPI projects.
- Desired outcome: Produce a correct first draft quickly, then verify behavior against the repository’s rules and tests before accepting it.
- Boundary or condition: I use AI when the task is well-scoped, the repo constraints are already visible, and I can validate the output with a focused check.

## 2. When I do not reach for AI

- Type of task or situation: Security-sensitive changes, production-critical logic, or architecture decisions that require independent reasoning without model assumptions.
- Reason or constraint: I do not trust AI to safely handle secrets, irreversible system changes, or unverified business rules without explicit source evidence.
- Alternative approach: I inspect the relevant files directly, confirm the repository contract, and validate behavior with tests or a narrow execution path before making the change.

## 3. My non-negotiables

- Rule I will always follow: I will treat the repository and its tests as the source of truth; AI is a drafting assistant, not the authority.
- Information or action I will protect: Secrets, credentials, token values, .env contents, and any sensitive user data.
- Quality or safety requirement: I will not accept output that cannot be explained, traced to source files, or verified with a concrete command or test.

## 4. My review rules

- What I verify before accepting output: The change matches the task scope, respects project guardrails, and does not modify unrelated files or violate the app rules in AGENTS.md.
- What requires independent confirmation: Security-sensitive logic, status transitions, validation rules, and any claim about expected behavior that is not directly supported by code or tests.
- What I check for in changes: Scope control, backward compatibility, test coverage, API contract preservation, and whether the code still follows the repo’s documented workflow.

## 5. What I am still figuring out

- Question I am exploring: Which AI tool is strongest for each stage of the workflow—drafting, reasoning, repo-wide planning, and validation.
- Practice I want to test: Using the right tool for the right problem instead of defaulting to one model for everything.
- Signal that would change my approach: If a tool produces confident but unsupported answers, ignores repo constraints, or hides uncertainty, I stop using it for that task.

## Decision Card

- For a new feature I reach for: Cursor for local implementation and quick iteration, with Codex when the work needs a broader repo-aware pass or structured multi-step execution.
- For a code review I reach for: Copilot for inline review and issue spotting, then Claude or ChatGPT for deeper reasoning when I need a second opinion on tradeoffs or edge cases.
- For debugging I reach for: Cursor or Copilot first for targeted code inspection, then Claude if the issue needs deeper logic tracing; ChatGPT is useful for explaining failed assumptions and alternative hypotheses.
- For infrastructure I reach for: Claude or ChatGPT for architecture tradeoff analysis, and Codex when I need a structured implementation workflow with validation steps.
- I will never paste: secrets, API keys, personal credentials, environment values, or sensitive production data into any AI tool.
- My one rule is: I will verify every AI-generated change against the repo, the tests, and the business rules before I trust it.

## Tool-by-tool usage

- Cursor: Best for direct code editing, local file-level iteration, and fast drafting inside the active workspace. I use it when I want to move quickly without losing context.
- Copilot: Best for in-editor suggestions, quick refactors, test scaffolding, and code review support while I work in VS Code. It is my default assistant for small, local tasks.
- Codex: Best for repo-aware implementation tasks, broader refactors, and disciplined execution when the work needs step-by-step planning and validation.
- Claude: Best for deep reasoning, architecture tradeoffs, root-cause analysis, and documentation-heavy work where nuance matters more than speed.
- ChatGPT: Best for brainstorming, comparing approaches, summarizing tradeoffs, and explaining unfamiliar concepts before I commit to a solution.

## Personal default workflow

1. Start with the source of truth in the repo, especially AGENTS.md, README.md, and the relevant code/test files.
2. Use the smallest viable AI tool for the job.
3. Ask for a draft or opinion, not a blind implementation.
4. Validate the result with the narrowest test or command that checks the changed behavior.
5. If the answer is uncertain, I do not accept it; I inspect, explain, and verify instead.
