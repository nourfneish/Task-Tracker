# Release Evidence

## Baseline and scope
- Baseline branch: `final-project`
- Scope: release readiness and documentation verification only.
- No new product feature was added; the app behavior is preserved.
- Changes are limited to release documentation and evidence checks.

## Evidence files
- [README.md](../README.md)
- [docs/release-evidence.md](./release-evidence.md)
- [docs/final-ai-review.md](./final-ai-review.md)
- [docs/ai-playbook.md](./ai-playbook.md)

## Claim-Versus-Reality Log

This log documents documentation claims checked against the actual repository state and verified commands.

### Claim 1: Health endpoint returns `{"status":"ok"}`
- Claim Source: [README.md](../README.md#L54-L67)
- Claim Text: "Expected response: `{"status": "ok", "timestamp": "2026-07-02T12:00:00.000000+00:00"}`"
- Reality Check:
  - Actual endpoint: [app/api/health.py](../app/api/health.py#L12-L18)
  - Route registration: [app/main.py](../app/main.py#L129-L130)
  - Reality: ✓ Verified. The endpoint returns a `HealthResponse` with `status="ok"` and an ISO-8601 UTC timestamp.
- Status: PASS — Claim matches implementation.

### Claim 2: Full pytest suite passes
- Claim Source: [README.md](../README.md#L98-L101)
- Claim Text: "Run the full pytest suite: `python -m pytest -v`"
- Reality Check:
  - Command run: `python -m pytest -q`
  - Result: `30 passed in 0.62s`
  - Test files in scope: [tests/test_tasks.py](../tests/test_tasks.py), [tests/test_activity.py](../tests/test_activity.py), and [tests/conftest.py](../tests/conftest.py)
  - Reality: ✓ Verified. The local repository test suite passes successfully.
- Status: PASS — Claim matches reality.

### Claim 3: Docker image builds and the container is configured for health checking
- Claim Source: [README.md](../README.md#L108-L133) and [Dockerfile](../Dockerfile#L18-L44)
- Claim Text: "Build the Docker image... verify `/health` from the running container..."
- Reality Check:
  - Build verification: `docker build -t task-tracker .` completed successfully in this workspace.
  - Non-root user: [Dockerfile](../Dockerfile#L18-L19) creates a `app` user and [Dockerfile](../Dockerfile#L33-L34) switches to it.
  - Exposed port: [Dockerfile](../Dockerfile#L36-L37) exposes port `8000`.
  - Health check: [Dockerfile](../Dockerfile#L39-L44) includes a container health check that probes `http://localhost:8000/health`.
  - Reality: ✓ Verified for the image build and configuration. The runtime port probe was not re-run in this session because `0.0.0.0:8000` was already in use locally, but the service is correctly configured to expose the health endpoint on port 8000.
- Status: PASS for build/configuration; local container-port rerun is environment-limited.

### Claim 4: CI installs dependencies and runs pytest
- Claim Source: [README.md](../README.md#L128-L133) and [.github/workflows/ci.yml](../.github/workflows/ci.yml#L1-L24)
- Claim Text: "CI verifies tests with `python -m pytest -v`."
- Reality Check:
  - Workflow trigger: [.github/workflows/ci.yml](../.github/workflows/ci.yml#L3-L5) runs on `push` and `pull_request`.
  - Dependency install: [.github/workflows/ci.yml](../.github/workflows/ci.yml#L18-L21) installs requirements before tests.
  - Test step: [.github/workflows/ci.yml](../.github/workflows/ci.yml#L23-L24) runs `python -m pytest -v`.
  - Reality: ✓ Verified. The CI workflow implements the documented test gate.
- Status: PASS — Claim matches implementation.

### Claim 5: Docker build context excludes local environment files and stray build artifacts
- Claim Source: [README.md](../README.md#L132-L133) and [.dockerignore](../.dockerignore)
- Claim Text: "The Dockerfile follows best-practices (non-root user, excludes local `.env` files in images)"
- Reality Check:
  - Secret exclusion: [.dockerignore](../.dockerignore#L1-L30) excludes `.env`, `.env.local`, `venv`, `.venv`, build output, and cache directories.
  - Reality: ✓ Verified. The repository explicitly excludes environment and local build artifacts from the Docker build context.
- Status: PASS — Claim matches repository configuration.

## Verified commands

- Full pytest suite:
  ```bash
  python -m pytest -q
  ```
  Result: `30 passed in 0.62s`

- Docker image build:
  ```bash
  docker build -t task-tracker .
  ```
  Result: build completed successfully.

- Runtime configuration check:
  ```bash
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
  This is the runtime command defined in [README.md](../README.md#L46-L52) and [Dockerfile](../Dockerfile#L43-L44).

## CI

- Workflow file: [.github/workflows/ci.yml](../.github/workflows/ci.yml)
- Trigger: `push` and `pull_request`
- Python version: `3.11`
- Dependency installation: `pip install -r requirements.txt`
- Test command: `python -m pytest -v`

## Docker

- Dockerfile uses a non-root `app` user: [Dockerfile](../Dockerfile#L18-L34)
- Container exposes port `8000`: [Dockerfile](../Dockerfile#L36-L37)
- Container runs Uvicorn on `0.0.0.0:8000`: [Dockerfile](../Dockerfile#L39-L44)
- Health probe is configured in the image: [Dockerfile](../Dockerfile#L39-L41)
- Local environment files and build artifacts are excluded from the build context: [.dockerignore](../.dockerignore)

## Manual verification

- [x] Local `pytest` run completed successfully.
- [x] Docker image build completed successfully.
- [x] Health endpoint implementation is present and verified in code.
- [x] No new product feature was added.
- [ ] A second live container port check is environment-limited because port 8000 was already in use during this session.

## Release readiness checklist

- [x] Pytest passes locally
- [x] Docker image builds successfully
- [x] Health endpoint is implemented and exposed in the app
- [x] Docker and CI configuration match the documented release steps
- [x] Documentation claims were checked against the repository and verified commands
