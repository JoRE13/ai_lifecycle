# Section 4.4 - Evaluation & Quality Assurance (Draft Input)

## Evaluation Dataset (final report choice)
- Dataset used: same dataset as Assignment 3 (`assignment3/assignment3.csv`, 50 labeled cases).
- Reason for continuity:
  - Same benchmark across lifecycle phases.
  - Directly comparable to Assignment 3 and Assignment 4 app-stack subset results.

## Quantitative Results To Reuse
From `assignment3/qualitative_summary_by_prompt.csv`:
- v4 (selected prompt baseline):
  - correctness_rate: 96.0%
  - policy_violations: 0
  - total_cases: 50

From `assignment4/evaluation/assignment4_evaluation_summary.csv` (app-stack subset):
- tested_rows: 20
- a4_verdict_accuracy: 95.0%
- a4_non_feasible_ratio: 0.0%
- a4_mismatch_count: 1
- a4_mismatch_ids: ["48"]

Interpretation:
- The core policy behavior stayed stable when moved from dataset-only evaluation into full app-stack evaluation.
- Main known failure persisted around ambiguous handwriting case 48.

## Failure Analysis (known issue and mitigation)
Known historical failure:
- Dataset case `id=48` (ambiguity/unclear handwriting) was misread as `correct_so_far` in earlier prompt/system variants.

Current mitigation strategy now implemented:
- Two-pass pipeline with strict legibility stage before reasoning (`backend/routes/query.py`).
- Fail-closed legibility decision if key readability signal is missing.
- If uncertain but interpretable: return `confirm_reading` and require user confirmation/edit before grading.
- If unreadable: return `ask_clarification` with specific rewrite request.

Practical effect:
- This moves ambiguous handwriting from silent misgrading risk to explicit user-confirmation/clarification flow.

## Guardrails and Validations (code-level inventory)

### A) Input and payload guardrails (query route)
- Mode is constrained to `hint | check_solution | reveal` at API boundary.
- Multi-page upload safety:
  - matching page counts required for solution and drawing payloads
  - max page count enforced (`QUERY_MAX_PAGE_COUNT`)
  - max single-file and max total submission bytes enforced.
- Image validation:
  - invalid/empty images rejected with `422`.
- `confirmed_reading_json` validation:
  - strict JSON parse with `422` on invalid JSON
  - must include at least one valid text entry
  - per-entry length, page bounds, and structure normalization.

Files:
- `backend/routes/query.py`
- `backend/config.py`

### B) Legibility and unclear-writing guardrails
- Dedicated legibility prompt/model pass before reasoning (when in `two_pass` mode).
- Fail-closed evaluation for legibility payload (missing `all_readable` treated as failure).
- `reading_confidence` normalized/clamped into [0, 1].
- Decision rule:
  - `confirm_reading` when there is usable interpreted content and confidence is acceptable.
  - `ask_clarification` fallback when content cannot be trusted.

File:
- `backend/routes/query.py`

### C) Model output contract and runtime reliability
- Gemini is called with enforced JSON schema (`response_json_schema`) from Pydantic models.
- Route-level JSON and type checks:
  - invalid JSON => `502`
  - non-object payload => `502`
  - empty response text => `502`
- Retry/backoff:
  - retry on server errors with exponential backoff
  - bounded retry attempts
  - non-retryable exceptions fail fast.

File:
- `backend/llm.py`
- `backend/routes/query.py`

### D) Storage and persistence guardrails
- R2 configuration must be present; missing envs raise explicit configuration errors.
- Storage failures return controlled server errors (`500/502`) rather than silent partial success.
- Parent attempt row is flushed before dependent analytics inserts (FK safety).

Files:
- `backend/storage/r2.py`
- `backend/routes/query.py`

### E) Error taxonomy and labeling consistency guardrails
- Error types normalized to canonical taxonomy before persistence/targeting.
- Structured error events only recorded in relevant contexts:
  - mode must be `check_solution`
  - verdict must be `incorrect` or `unclear`
  - requires meaningful extracted error content.

Files:
- `backend/error_taxonomy.py`
- `backend/routes/query.py`
- `backend/routes/exam.py`
- `backend/exam_service.py`

### F) Exam flow validation guardrails
- Pack input constraints:
  - allowed sizes only: 10/20/30
  - allowed modes only: auto/manual + per_question/end_exam
  - allowed topics only.
- Manual target validation against canonical error taxonomy.
- Handwritten final-answer OCR safety checks:
  - base64 validity
  - image byte-size and dimension limits
  - null/unreadable extraction => explicit `422` with retry guidance.
- Grading robustness:
  - normalization and numeric/fraction equivalence checks.

Files:
- `backend/routes/exam.py`
- `backend/exam_service.py`
- `backend/schemas/exam.py`

### G) Auth/session/security guardrails
- Request/auth schemas enforce:
  - valid email format
  - password minimum length
  - field length limits.
- Access token checks:
  - JWT decode validation
  - token type check (`type=access`)
  - active-user check.
- Refresh token lifecycle hardening:
  - selector/validator split
  - hashed validator at rest
  - expiry + revoked checks
  - rotation on refresh.

Files:
- `backend/schemas/auth.py`
- `backend/auth/jwt.py`
- `backend/auth/deps.py`
- `backend/repositories/auth_repo.py`

### H) Frontend (iOS) guardrails and UX validations
- Auth form validation before network calls:
  - email required and normalized
  - full name required on registration
  - password checks before submit.
- Query request preflight checks:
  - solution image pages and drawing pages must both exist
  - counts must match before API call.
- Draft/persistence safety:
  - local draft load/save guards to prevent corrupt or empty page hydration
  - page index bounds checks for add/remove/navigation operations.
- Export/PDF workflow safeguards:
  - submit disabled if required fields are missing (title, student name, selected problems)
  - explicit user-facing error text for recoverable failures.
- Destructive actions protected with confirmation dialogs:
  - delete folder
  - delete problem.
- Unclear-writing confirmation flow wired at UI layer:
  - handles `confirm_reading` with editable fields
  - blocks submit when clarified text is empty.

Files:
- `MathCoach/Features/Auth/AuthViewModel.swift`
- `MathCoach/Core/API/APIClient.swift`
- `MathCoach/Core/Storage/ProblemDraftStore.swift`
- `MathCoach/Features/Notebook/NotebookViewModel.swift`
- `MathCoach/Features/Notebook/NotebookView.swift`
- `MathCoach/Features/Problems/ProblemsOverviewView.swift`
- `MathCoach/Features/Problems/ProblemsOverviewViewModel.swift`

## Copy-Ready Paragraph (Report)
For final evaluation, we kept the same 50-case dataset from Assignment 3 to preserve comparability across lifecycle iterations. The selected v4 baseline remains strong (96.0% correctness rate, 0 policy violations on the 50-case set), and app-stack validation on a 20-case subset remained stable (95.0% verdict accuracy, 0.0% non-feasible ratio). Historically, the main recurring edge case was ambiguous handwriting (case 48). In the current system, we added explicit guardrails for this class of failure via a two-pass legibility-first pipeline: uncertain submissions now trigger either a user-confirmed reading flow (`confirm_reading`) or a clarification request (`ask_clarification`) instead of silent grading assumptions. Combined with schema-constrained model outputs, bounded retry/backoff, upload-size constraints, canonical error normalization, and strict auth/token validation, this yields a substantially safer and more diagnosable QA envelope for production-like usage.

## Deferred (fill later if you update numbers)
If you run a fresh final-phase eval pass on the same 50 cases, replace only the metric values above while keeping the same dataset and methodology description.
