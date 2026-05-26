# Final Assignment Deliverables

This directory contains the submitted assignment artifacts and supporting review material for the AI Math Coach project.

## Canonical Files

- Source-of-truth writeups and planning notes should be kept as Markdown when possible.
- User-testing inputs and manually curated CSV files are canonical when they are used to reproduce a report or dashboard result.
- `CODING_AGENT_SESSION_REPO_IMPROVEMENT_NOTES.md` is the handoff note for follow-up engineering work.

## Generated Artifacts

Generated PDFs, exported reports, rendered HTML, screenshots, prompt-output snapshots, and bytecode/cache files should only be committed when they are required for the assignment submission or when they capture a reviewed result that cannot be regenerated easily.

When a generated artifact is committed, keep the source input beside it or document how it was produced.

## Regression Fixtures

API contract examples live outside this folder in `api_contract_examples/`. Those JSON files are intentionally checked in because both backend and frontend tests use them to detect response-shape drift.

