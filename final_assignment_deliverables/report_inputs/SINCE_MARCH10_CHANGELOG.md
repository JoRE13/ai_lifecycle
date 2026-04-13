# Since March 10, 2026 - Cross-Repo Changelog

Last updated: 2026-04-13

## Scope and Comparison Method
- Backend repo: `ailifecycle/ai_lifecycle`
  - Anchor commit (closest on/around 2026-03-10): `8364b6f` (2026-03-10)
  - Compared range: `8364b6f..HEAD`
  - Commits in range: `43`
- Frontend repo: `ailifecycle_ui/ai_lifecycle_frontend`
  - Anchor commit (closest on/around 2026-03-10): `d7ed7ea` (2026-03-10)
  - Compared range: `d7ed7ea..HEAD`
  - Commits in range: `95`

This file summarizes both committed work and local WIP state.

## High-Level Delta (What Changed Since March 10)
- Full multi-page query pipeline (backend + iOS) matured and stabilized.
- Folder model evolved from flat to one-level nesting with safer archive/delete behavior.
- Personalized exam-prep flow was implemented end-to-end (pack generation, sessions, grading, UX polish).
- Error analytics expanded into a practical error-bank workflow for users.
- Unclear-handwriting handling was hardened via `confirm_reading`-first flow.
- Major iOS UX pass: Icelandic localization, dashboard IA redesign, PDF export redesign, cropper, canvas/fullscreen stabilization, profile/avatar improvements.
- Data collection/consent schema and analytics observability were expanded.

## Assignment 6 Goal Check (Status)
Using this range plus current code state:
1. Add user-based statistics to homepage: `Done`
2. Add error bank for users: `Done`
3. Lower latency further: `Partial / ongoing` (improvements made, still a user testing pain point)
4. Generate problems based on user errors: `Done`
5. Implement anonymous data collection: `Backend done` (consent + anon IDs + schema), UI consent controls not surfaced yet

## Timeline of Major Shipped Work

### 2026-03-22 to 2026-03-28
- Backend:
  - `773202b`: multipage querying + profile fields + versioned legibility pipeline
  - `a71b5d8`: expert-mode prompt versioning and plumbing
  - `a88c75d`: folder organization + move APIs
  - `470834d`: dataset collection schema + exam-pack API flow
  - `5f35f0b`: one-level folder nesting + safe archiving
  - `bc180a2`: structured error fields from `check_solution`
  - `77d29ea`: confirm-before-grading flow for uncertain handwriting
  - `a92d410`: canonical error taxonomy normalization
- Frontend:
  - `c09d12c`: multi-page notebook + PDF/profile integration
  - `50752a0`: expert-mode toggle + persisted draft/query payload wiring
  - `c676f17`: folder organization UI
  - `14f0d6b`: exam prep/session flow + analytics wiring
  - `4d0b16f`: Icelandic localization pass
  - `4e8e7af`: nested folder UI + folder deletion workflow
  - `c4dd038`: profile avatar picker + onboarding avatar flow
  - `a274157`: reading confirmation sheet

### 2026-03-30 to 2026-04-04
- Backend:
  - `1853357`: exam session resume + Icelandic generated exam content
  - `d054219`: handwriting answer extraction for exam grading
  - `f808c35`: `confirm_reading` unclear-flow handling across all modes
  - prompt and model tuning commits (e.g., `5a47ae5`, `cd30ae2`, `7736549`)
- Frontend:
  - Avatar rendering/perf fixes (`c8c9383`, `96371bc`, `159ab20`, `f2ed2f4`)
  - Folder layout iterations (`afc7f3f`, `7c1f765`, `e4b9fa5`, `bec0822`)
  - Date formatting improvements (`40d037c`, `07d03ca`)
  - Exam UX polish (`4cc402d`)
  - Unclear-writing UX redesign + debug trigger (`786928f`, `426b03d`)
  - Camera permissions + image crop flow (`85f6f15`, `719fa9e`, `903f747`, `d68e94c`, `b0379a7`)
  - Draft persistence and PDF flow fixes (`57113ba`, `ef47568`, `6eab1dd`, `b64aec5`)

### 2026-04-05 to 2026-04-13
- Backend:
  - analytics upgrades (`c4634fb`, `cc000c7`)
  - prompt tightening/math correctness (`fe02a97`, `60ddada`, `2c89169`)
  - registration full-name support (`4595fa3`)
  - problem deletion endpoint with dependent cleanup (`5683a8a`)
  - standardized user testing packet assets (`9e2dbf1`)
- Frontend:
  - PDF export redesign + folder-filtered selection + preview (`7e53cda`, `75594a6`)
  - Dashboard contrast and discoverability improvements (`a9f2ee1`, `36ad050`)
  - Onboarding/profile clarity updates (name capture and avatar affordance) (`f2f5346`)
  - Problem deletion UI flow (`cebb16e`)
  - Major fullscreen canvas/A4/zoom stabilization cycle (`147658b` through `9b3f98d`)
  - Apple Pencil double-tap pen/eraser (`73c0c99`)
  - Split folder-tree + problem workspace redesign and panel scrolling (`2d5b210`, `4cea7ae`, `c92c930`, `f36e28b`)
  - Latest polish on attempts, greeting, streak/problem view, preferred paper defaults (`678b674`, `02ada3b`, `ebf4be2`, `9c04555`)

## Feature Buckets (Report-Ready)

### 1) Personalization and Progress UX
- Homepage weekly comparative stats and streak experience.
- Profile improvements: avatar selection, better onboarding clarity, full-name capture.
- Personalized exam-prep flow connected to user error history.

### 2) Error Intelligence
- Structured error extraction from check-solution responses.
- Canonical error taxonomy normalization.
- Error-bank APIs and UI (including folder-scoped filtering and event browsing).
- Error-driven exam target selection (`choose_auto_targets` using historical error patterns).

### 3) Reliability and Safety
- Two-pass legibility flow with `confirm_reading`/clarification safeguards.
- Multipage artifact handling and storage hardening.
- Extensive canvas/draft persistence and fullscreen interaction stabilization.
- Deterministic media-source selection and improved image onboarding/cropping flow.

### 4) Content and Export
- Exam content generation/localization and exam session resume behavior.
- Handwriting OCR for exam answer grading.
- PDF export redesign with folder-aware selection and improved layout flow.

### 5) Data, Observability, and Evaluation
- Dataset collection schema and consent fields.
- Langfuse/analytics instrumentation expansion and per-stage metrics.
- User testing packet, templates, and report-ready user-testing outputs.

## Shipped vs In-Progress

### Shipped (committed)
- All items listed in the timeline above are in git history between anchor and HEAD.

### In-progress / local WIP
- Backend repo currently has local uncommitted files (mostly caches/logs and local report artifacts).
- Frontend repo currently has no local uncommitted changes.

## Reproducibility Commands
Run from workspace root:

```powershell
# Backend anchor and range
$a = git -C ailifecycle/ai_lifecycle rev-list -n 1 --before="2026-03-11 00:00" HEAD
git -C ailifecycle/ai_lifecycle log --date=short --pretty=format:"%h %ad %s" "$a..HEAD"

# Frontend anchor and range
$b = git -C ailifecycle_ui/ai_lifecycle_frontend rev-list -n 1 --before="2026-03-11 00:00" HEAD
git -C ailifecycle_ui/ai_lifecycle_frontend log --date=short --pretty=format:"%h %ad %s" "$b..HEAD"
```

