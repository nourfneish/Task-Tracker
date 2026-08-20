# Release Evidence

## Verified commands

- Start backend API:
  ```bash
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

- Health check:
  ```bash
  curl http://127.0.0.1:8000/health
  ```
  Verified response:
  ```json
  {"status":"ok","timestamp":"2026-08-20T15:25:57.305278+00:00"}
  ```

- Full pytest suite:
  ```bash
  python -m pytest -v
  ```
  Result: `41 passed`

- Docker build:
  ```bash
  docker build -t task-tracker .
  ```

- Docker run:
  ```bash
  docker run --rm -p 8000:8000 task-tracker
  ```

- Container health endpoint verification:
  ```bash
  curl http://127.0.0.1:8000/health
  ```

## CI

- Workflow file: `.github/workflows/ci.yml`
- Python version: `3.11`
- Test command: `python -m pytest -v`
- Dependency install: `python -m pip install --no-cache-dir -r requirements.txt`

## Docker

- Dockerfile uses a non-root `app` user.
- `.dockerignore` excludes `.env`, `*.env`, `.git`, `venv`, and other local files.
- The container exposes port `8000` and uses `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

## Claims vs Reality

- Claim evidence table to be verified by hand.