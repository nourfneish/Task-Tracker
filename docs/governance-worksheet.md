# Governance Retrospective - Al-Assisted Coding

## What I Shared With Al

| Item | Module | Risk Level | Reason | Safer Future |
| --- | --- | --- | --- | --- |
| Task Tracker code | 2-5 | Low | This is course toy-project code with no sensitive data or proprietary logic. | Review the files and remove any accidental local configuration before sharing. |
| Test output and stack traces | 2-4 | Medium | Stack traces can reveal private repository paths and internal implementation details even when they contain no secrets or PII. | Redact paths, environment values, and request data, then share only the relevant error excerpt. |
| Frontend code | 3 | Low | This frontend is course toy-project code and contains no sensitive data or proprietary logic. | Check that sample data and client-side configuration are fictional before sharing. |
| Dockerfile and CI YAML | 4 | Medium | These files expose internal build and deployment details, though the reviewed versions contain no credentials, tokens, or production configuration. | Share a sanitized copy and verify that secrets are supplied only through protected CI settings. |
| Any real external data I used by mistake | TODO | High | Real external data may include customer, user, regulated, or otherwise unauthorized-to-share information. | Replace it with synthetic data and remove the real data from prompts, logs, and shared artifacts. |

## What I Received From Al

| Generated Thing | Module | Do I Understand It Line by Line? | Action |
| --- | --- | --- | --- |
| Backend models and validators | 2 | Mostly | Review validation rules and write a small test for each. |
| Frontend board and drag-and-drop logic | 3 | Partly | Trace one drag-and-drop flow and document it. |
| Cl workflow | 4 | Mostly | Review each job step and run the workflow locally where possible. |
| Dockerfile | 4 | Mostly | Check every instruction and rebuild the image. |
| Security findings and plans | 5 | Partly | Verify findings against the code before acting on them. |
