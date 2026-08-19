# My AI Development Guidelines

This document outlines my approach to using AI throughout the course final project, and how I stay accountable for the work produced.

## Ownership of AI Output

- I treat AI as a helper, not the one making final calls.
- I craft prompts, choose among outputs, and check every result myself.
- I take responsibility for the code, tests, documentation, and submission proof.
- I never allow AI to modify application logic without checking it by hand.
- Proof: I executed `python -m pytest -q`, confirmed `/health`, built and launched the Docker image, and refreshed the release and AI review notes.

## 1. Situations where I turn to AI first

- mapping out a feature or task
- drafting user stories and business rules
- writing documentation and workflow descriptions
- proposing CI and Docker setups

## 2. Situations where I don't rely on AI

- hands-on checking and testing
- reviewing code for accuracy
- personal reflection and ownership calls

## 3. My core principles

- I stay in charge of AI, not the reverse.
- I gather context before I prompt.
- Better prompts lead to stronger results.

## 4. How I review AI work

- Make sure generated answers align with app requirements.
- Confirm tests genuinely run and succeed.
- Double-check AI claims before trusting them.

## 5. What I'm still working out

- Which tasks AI can handle safely versus what needs my verification.
- How to keep prompts tight and focused.
- How to document AI usage without losing ownership.

---

## Decision Card

- New feature planning: ChatGPT
- Code review: Cursor
- Debugging: Copilot
- Infrastructure: Claude Code CLI
- Never share credentials with AI tools.
- My code and logic remain mine.