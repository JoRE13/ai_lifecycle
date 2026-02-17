# REI603M Assignment 4 Prototype

AI Lifecycle course project (University of Iceland): an AI math coach with an iOS frontend and a FastAPI backend using real Gemini API calls.

## Team
- Johannes Reykdal Einarsson (`jre5`)
- Solvi Santos (`sos106`)
- Saevar Breki Snorrason (`sbs87`)

## Repositories
- Backend + assignment artifacts (this repo): `ai_lifecycle`
- Frontend (iOS SwiftUI): `ai_lifecycle_frontend`  
  Public repo: `https://github.com/JoRE13/ai_lifecycle_frontend`

For final submission zip, include both source trees.

## What Is Implemented
- Interactive user flow with authentication, problem creation, notebook/canvas, and tutor response display.
- Real LLM integration (`Gemini`) via backend `/query` endpoint.
- Prompt management in file-based prompt template (`backend/prompt.txt`).
- Basic API error handling (no raw stack traces to users).
- Observability via Langfuse traces/observations.
- Assignment 4 evaluation artifacts (20 tested cases through prototype flow).

## High-Level Architecture
- Frontend: SwiftUI iOS app (`MathCoach`) with PencilKit canvas and API client.
- Backend: FastAPI + SQLModel + Alembic + JWT auth.
- LLM: Google Gemini (`models/gemini-3-flash-preview`) with structured JSON output.
- Storage: Neon Postgres + Cloudflare R2 for uploaded artifacts.
- Observability: Langfuse tracing + exported observations.

## Repository Structure
- `backend/`: FastAPI app, DB models/migrations, auth, LLM, storage.
- `assignment2/`: PRD.
- `assignment3/`: prompt engineering and A3 evaluation artifacts.
- `assignment4/observability/`: Langfuse export + metrics script + summaries.
- `assignment4/evaluation/`: A4 20-case test export + evaluation comparison summaries.

## Backend Setup
1. Create `backend/.env` from template:
   - Copy `backend/.env.example` to `backend/.env`
2. Install Python dependencies:
   - `pip install -r backend/requirements.txt`
3. Run DB migrations:
   - `cd backend && alembic upgrade head`
4. Start backend:
   - `fastapi dev backend/main.py`

Default backend URL: `http://127.0.0.1:8000`

## Required Backend Env Vars
From `backend/.env.example`:
- `DATABASE_URL`
- `JWT_SECRET`
- `GEMINI_API_KEY`
- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`

Optional:
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_HOST` / `LANGFUSE_BASE_URL`

## Frontend Setup (iOS)
In the frontend repo (`ai_lifecycle_frontend`):
1. Open `ratatoskur.xcodeproj` in Xcode.
2. Set `BACKEND_BASE_URL` in Info settings (or use default).
3. Build and run the `ratatoskur` scheme.

Frontend app flow:
- Register/Login
- Create/open problem
- Upload problem image
- Write solution on canvas
- Submit mode: `Hint` / `Check Step` / `Reveal`
- View tutor response and attempt history

## API Endpoints Used
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`
- `POST /auth/logout`
- `POST /problem`
- `GET /problems`
- `GET /problems/{problem_id}/attempts`
- `POST /query`

## Assignment 4 Observability Artifacts
- Raw observations export:  
  `assignment4/observability/langfuse_observations_export.csv`
- Metrics script:  
  `assignment4/observability/compute_langfuse_metrics.py`
- Metrics summary:  
  `assignment4/observability/langfuse_metrics_summary.md`

### Cost Methodology Used
Pricing basis (Gemini 3 Flash Preview, paid tier):
- Input: `$0.50 / 1M tokens`
- Output: `$3.00 / 1M tokens` (output includes thought tokens)

Formula:
- `estimated_total_cost = (input_tokens / 1_000_000 * input_rate) + ((output_tokens + thought_tokens) / 1_000_000 * output_rate)`
- `estimated_cost_per_interaction = estimated_total_cost / generation_calls`

Note:
- If Langfuse pricing tiers are not configured, `logged_total_cost` may be `0`; use estimated cost fields.

## Assignment 4 Evaluation Artifacts
- Raw A4 test file:  
  `assignment4/evaluation/assignment4_results_raw.csv`
- Evaluation script:  
  `assignment4/evaluation/compute_assignment4_evaluation.py`
- Tested subset (20 cases):  
  `assignment4/evaluation/assignment4_tested_subset.csv`
- Summary (A4 vs A3 v4 subset):  
  `assignment4/evaluation/assignment4_evaluation_summary.md`
- Mismatch breakdown:  
  `assignment4/evaluation/assignment4_mismatches.csv`

## Current A4 Headline Metrics
- Tested rows: `20` (requirement satisfied)
- A4 verdict accuracy: `95.00%`
- A4 non-feasible ratio: `0.00%`
- A3 v4 subset (same 20 images): `95.00%`, non-feasible `0.00%`
- A4 vs A3 subset delta: no change

## Notes
- Keep secrets out of git (`.env` files are ignored).
- For local HTTP development, `COOKIE_SECURE=false` is expected.
