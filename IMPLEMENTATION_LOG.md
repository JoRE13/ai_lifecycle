# Ratatoskur Implementation Log

Last updated: 2026-03-28

This is a living log of major implemented work across:
- Backend repo: `ailifecycle/ai_lifecycle`
- Frontend repo: `ailifecycle_ui/ai_lifecycle_frontend`

## How to maintain this file
After each completed feature:
1. Add a new dated entry under `Recent Work`.
2. Include repo + commit hash.
3. Add a short impact note (why this matters).

## Recent Work

### 2026-03-28 (error taxonomy normalizer)
- Backend (working tree): Added canonical error taxonomy normalization across query, analytics, and exam targeting.
  - New module: `backend/error_taxonomy.py` with canonical error codes and legacy alias mapping.
  - `/query` now normalizes `error_type` before persisting attempts, error events, and error-bank entries.
  - `/exam-packs` now normalizes auto/manual targets and validates unsupported manual targets.
  - Error-bank summary now merges legacy + canonical labels into a single canonical view per concept.
  - Updated v2 prompt contracts to request canonical error codes directly.
  - Impact:
    - More stable training/eval dataset labels.
    - Better exam target quality from historical user errors.

### 2026-03-28
- Backend `5f35f0b`: Added one-level folder nesting and safe folder archiving behavior.
  - Added `parent_folder_id` support (model/schema/routes + migration `e8b1d4c3f6a2`).
  - Archiving parent folders now detaches child folders to root and moves problems safely.
- Frontend `4e8e7af`: Added nested folder UI + folder deletion workflow (Icelandic UI).
  - Parent/subfolder display in dashboard and all-problems views.
  - Folder delete confirmation + API wiring.
- Backend migration executed successfully:
  - `alembic upgrade head` to `e8b1d4c3f6a2 (head)`.

### 2026-03-28 (structured error pipeline)
- Backend (working tree): Added structured error extraction for `check_solution`.
  - Prompt contract now includes:
    - `error_type`
    - `error_step`
    - `correct_approach`
    - `error_confidence`
  - `/query` now normalizes these fields and stores step-level error details in `error_events`.
  - This improves:
    - error-bank quality
    - consistency for error-based exam generation
    - analytics for frequent mistake patterns.

### 2026-03-28 (reading confirmation flow)
- Backend + Frontend (working tree): Added confirm-before-grading flow for uncertain handwriting in `check_solution`.
  - Backend:
    - Legibility output extended with `reading_confidence`, `interpreted_text`, `interpreted_steps`.
    - `/query` accepts optional `confirmed_reading_json`.
    - When legibility is uncertain, backend can return `response_type = confirm_reading` with editable interpreted fields.
    - Confirmed reading is injected into reasoning prompt on follow-up call.
  - Frontend (iOS):
    - Added editable "Staðfesta lestur" sheet.
    - User can edit interpreted steps and submit "Samþykkja og meta" to re-run grading with confirmed reading.
  - Impact:
    - Reduces wrong feedback from handwriting misreads.
    - Creates cleaner corrected-reading traces for future dataset work.

### Earlier phase (already implemented before this update)
- Backend `470834d`: dataset collection schema + exam-pack API flow.
- Backend `a88c75d`: folders and problem move APIs + migration.
- Backend `a71b5d8`: versioned expert prompts + expert mode plumbing.
- Backend `773202b`: multipage querying + profile fields + legibility pipeline.
- Frontend `e4a8c41`: fixed folder creation (POST `/folders`).
- Frontend `4d23ee4`, `1c3db0a`: dashboard/profile/submission UX improvements.
- Frontend `4d0b16f`: broad Icelandic localization across UI.
- Frontend `14f0d6b`: exam prep/session flow and analytics wiring.
- Frontend `c09d12c`, `50752a0`: multipage notebook + expert mode controls.

## Current platform capabilities (high-level)
- Multi-page handwritten solution submission and evaluation.
- Icelandic-first UI across auth/dashboard/notebook/exam flows.
- Observability with tracing and token metrics.
- Error bank and analytics summaries.
- Exam pack generation and online exam flow (10/20/30, auto/manual, per-question/end feedback).
- Folder organization with one-level subfolders and safe deletion.
