# Ratatoskur Implementation Log

Last updated: 2026-04-04

This is a living log of major implemented work across:
- Backend repo: `ailifecycle/ai_lifecycle`
- Frontend repo: `ailifecycle_ui/ai_lifecycle_frontend`

## How to maintain this file
After each completed feature:
1. Add a new dated entry under `Recent Work`.
2. Include repo + commit hash.
3. Add a short impact note (why this matters).

## Recent Work

### 2026-04-04 (fínpússun á persónulegum prófum)
- Backend `b8d4bcb`: polished exam backend behavior and localization.
  - `/exam-packs/{pack_id}/start` now resumes an existing `in_progress` session for the same user/pack instead of always creating a new one.
  - Localized generated exam prompts and grading feedback to Icelandic in `exam_service.py` (question text + result messages).
  - Impact:
    - Users can safely continue unfinished personal exams.
    - Exam experience is language-consistent with the rest of the app.
- Frontend `a5873ac`: polished personal exam UX in `ExamPrepSheet`.
  - Added in-session question navigator (quick jump between questions).
  - Added unanswered counter and submit confirmation when unanswered questions remain.
  - Added session hydration/resume logic by loading existing session answers/feedback on open.
  - Added automatic save-before-navigation when current answer changed.
  - Updated recent pack timestamp display to Icelandic date-only format (lowercase month names).
  - Impact:
    - Stronger exam flow reliability with less accidental data loss.
    - Faster navigation and better completion clarity for users.

### 2026-03-30 (problem timestamp readability)
- Frontend `40d037c`: changed problem date display from raw ISO timestamp to Icelandic date-only format.
  - Applied across dashboard recent problems, all-problems list, and submission export selection.
  - Uses lowercase Icelandic month names (for example: `30. mars 2026`) with no time shown.
  - Impact:
    - Removes noisy fractional-second timestamps from UI.
    - Improves readability and aligns with Icelandic language expectations.

### 2026-03-30 (avatar rendering performance + folder layout)
- Frontend `c8c9383`: fixed avatar SVG bundle lookup fallback so profile/dashboard icons resolve reliably.
- Frontend `96371bc`: adjusted avatar UX sizing and styling.
  - Larger dashboard/profile/picker avatars.
  - Removed extra wrapper circles so only the avatar artwork border is shown.
- Frontend `159ab20`: hotfix for clipped/blank avatar rendering by restoring stable HTML-based SVG scaling path.
- Frontend `f2ed2f4`: migrated avatar rendering to native PNG images for speed.
  - Generated and added six PNG avatars under `MathCoach/Resources/profile_avatars/`.
  - Added `Shared/AvatarImageView.swift` with in-memory image caching.
  - Avatar usage now prefers PNG (fast path) with SVG fallback.
- Frontend `afc7f3f`: updated dashboard folders list to two columns per row.
  - Subfolder behavior unchanged (same data model/actions), only visual layout changed.
  - Added truncation handling to keep folder cards stable in narrower cells.
  - Impact:
    - Faster and more stable avatar rendering on iOS.
    - Better dashboard density and quicker folder scanning.

### 2026-03-28 (avatar onboarding + labeled selector)
- Frontend `c4dd038`: completed Norse avatar rollout and selection flow polish.
  - Added six themed SVG avatar assets under `MathCoach/Resources/profile_avatars/`.
  - Replaced dashboard/profile avatar rendering with SVG resource-based avatars.
  - Added labeled avatar selector grid (name under each icon) in Profile.
  - Added avatar selection in Registration so users pick a starting avatar at account creation.
  - Standardized selected avatar storage to `profile.avatar.id` and shared option resolution.
  - Impact:
    - Clearer profile customization UX.
    - Better first-run onboarding personalization.
    - Consistent avatar identity between signup, profile, and dashboard.

### 2026-03-28 (norse avatar assets in profile UI)
- Frontend (working tree): Replaced placeholder profile icons with six Norse SVG avatars.
  - Added assets under `MathCoach/Resources/profile_avatars/`:
    - `avatar_odin.svg`
    - `avatar_thor.svg`
    - `avatar_loki.svg`
    - `avatar_freya.svg`
    - `avatar_garmur.svg`
    - `avatar_idun.svg`
  - Updated avatar border color in all six files from blue tones to theme-matching brown (`rgb(90,48,24)`).
  - Profile selection UI now uses the SVG avatars directly.
  - Dashboard profile button now shows the currently selected avatar.
  - `SVGLogoView` now supports resource paths with subdirectories.
  - Updated Xcode project file to include the six new SVG resources.

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
