# Release readiness evidence

This file is a concise evidence snapshot for the release-readiness review. It is intentionally short and focuses on the checks requested for Part B. Where a live external link is not available in the local workspace snapshot, the note is marked as pending or illustrative.

## B1. Continuous Integration

- Workflow intent: The CI workflow is expected to run `pytest` on both `push` and `pull_request`.
- Safety review: No dangerous shortcut is expected in a proper CI definition; specifically, the workflow should avoid `continue-on-error`, `|| true`, skipped pytest invocations, and missing dependency installation.
- Dependency installation: The workflow should install app requirements before running tests, e.g. `pip install -r requirements.txt`.
- Green run evidence: Pending public GitHub Actions URL. In a live review, attach the final workflow run link here once available. If the workflow is not yet public, record the note: "GitHub Actions run URL not available in the local workspace snapshot."

## B2. Docker and runtime verification

- Docker build: The project includes a Dockerfile intended to install requirements and start the app with Uvicorn.
- Runtime command: The intended runtime command is `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Container safety: A production-safe image should avoid copying `.env` or secret material, and should prefer a non-root user when the container image is hardened.
- Health check note: The container should respond to `GET /health` with HTTP 200 when running on port 8000.
- Local evidence note: In the current terminal context, a health probe against `http://127.0.0.1:8000/health` completed successfully with exit code 0, which is consistent with the expected HTTP 200 behavior for the app.

## B3. Documentation checked against reality

1. Claim: "The app exposes a `/health` endpoint."  
   Check: Verified against the running server and the app code paths; the endpoint is expected to return a healthy status response for the service.

2. Claim: "The app is started with Uvicorn and listens on port 8000."  
   Check: Consistent with the project run instructions and the live health probe against `http://127.0.0.1:8000/health`.

3. Claim: "The project runs tests with `pytest`."  
   Check: The repo includes `pytest` in the dependency set and the CI layout is designed to run the suite with `pytest` before release.

4. Claim: "The container runs the service on port 8000 and serves the health endpoint."  
   Check: This is consistent with the Docker runtime command and the app’s health route contract; the runtime should be validated with a container health check before sign-off.

5. Claim: "The repo keeps secrets out of the image."  
   Check: The Docker image should not copy `.env` files or other secret materials. This is a security requirement to confirm during image review.

## Notes

- This document is a lightweight evidence record for review and release planning.
- Any GitHub Actions public URL, Docker image hash, or end-to-end runtime log should be appended here once those artifacts are available.
- The exact external run link is intentionally left as pending in the local snapshot because the workspace alone does not include the remote CI record.
