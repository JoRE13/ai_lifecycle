# Coding Agent Session: Repo Improvement Notes

After the LLM routing work, these are the main additional improvement areas identified across the backend and iOS frontend repositories.

## 1. API Contract Drift

We already hit this with `ambiguous_steps` versus `ambiguous_regions`. The backend and iOS app are manually kept in sync, so a small response-shape change can silently break the client.

Relevant spots:

- `backend/routes/query.py`
- `MathCoach/Core/Models/QueryModels.swift`

Mitigation:

- Add backend response fixture tests for `check_solution`, `hint`, `reveal`, `confirm_reading`, and `ask_clarification`.
- Add Swift decoding tests that load those same JSON fixtures.
- Longer term, generate Swift models from backend OpenAPI or keep a checked-in `api_contract_examples/` directory that both repos test against.

This is the next thing I would personally address.

## 2. Test Coverage Is Mostly Placeholder

The iOS test files are still Xcode template tests, and the backend seems to rely more on prompt-testing scripts than app-layer regression tests.

Relevant spot:

- `ratatoskurTests/ratatoskurTests.swift`

Mitigation:

- Backend: add `pytest` tests around `/query` with mocked LLM responses.
- Frontend: add decoding tests for `QueryResponse`, auth token refresh behavior, and `confirm_reading` view-model state transitions.
- Keep prompt evaluation separate from product regression tests. Prompt quality tests answer "is the model good?"; API tests answer "does the app still work?"

## 3. Analytics Consent Defaults To On

`consent_analytics` defaults to `true` in the user model. That may be acceptable for a class prototype, but it is worth being explicit because the app stores student work, images, attempts, and analytics events.

Relevant spot:

- `backend/models/auth_models.py`

Mitigation:

- Make consent explicit during onboarding.
- Consider defaulting to `false` unless the user opts in.
- Keep the backend guard already in place, but ensure registration/update flows expose the choice clearly.

## 4. Exam Answer Extraction Still Bypasses The Shared LLM Layer

Even setting routing aside, `exam_service.py` directly calls Gemini. That means it bypasses shared observability conventions, retry behavior, schema handling, and future provider normalization.

Relevant spot:

- `backend/exam_service.py`

Mitigation:

- Move answer extraction behind a small shared helper, even if it remains Gemini-only initially.
- Return the same trace/request metadata shape where possible.
- Add a mocked extraction test for valid image, unreadable image, oversized image, and malformed model JSON.

## 5. Repo Artifact Hygiene

The repo still contains a mix of source files, generated reports, PDFs, embedded HTML, prompt results, raw user-testing inputs, and generated Python bytecode deletions. Some of that is intentional for final deliverables, but it needs a clear tracking policy.

Mitigation:

- Decide which deliverables are source-of-truth versus generated artifacts.
- Track source Markdown/CSV inputs.
- Ignore regenerable outputs unless the assignment requires them committed.
- Add a short `final_assignment_deliverables/README.md` explaining what is canonical.

## 6. Frontend Latency UX

The frontend has a 60-second request timeout, but users mostly experience that as "the app is stuck." Model routing helps, but user trust also depends on visible progress and recovery.

Relevant spot:

- `MathCoach/Core/API/APIClient.swift`

Mitigation:

- Show staged status text: uploading, reading handwriting, checking reasoning, saving result.
- Preserve the user's drawing and request state after failure.
- Offer retry without making the user redraw or reselect context.
- Consider a cancel button for long requests.

## Recommended Next Step

Address API contract tests next. That gives us a safety net for the backend and frontend changes that are likely to continue during the next implementation pass.
