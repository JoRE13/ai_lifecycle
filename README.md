# AI Math Coach (Assignment 6)

AI Lifecycle course project (University of Iceland): an AI math coach with an iOS frontend, FastAPI backend, and a Streamlit analytics dashboard.

## Team
- Johannes Reykdal Einarsson (`jre5`)
- Solvi Santos (`sos106`)
- Saevar Breki Snorrason (`sbs87`)

## Repositories
- Backend + analytics dashboard + assignment artifacts (this repo): `ai_lifecycle`
- Frontend (iOS SwiftUI): `ai_lifecycle_frontend`  
  Public repo: `https://github.com/JoRE13/ai_lifecycle_frontend`

## Project Structure
- `backend/`: FastAPI app, auth, query routes, SQLModel models, Alembic migrations, LLM integration.
- `analytics_dashboard/`: Streamlit dashboard, review-summary LLM helper, weekly insights pipeline script.
- `assignment6/`: Assignment 6 artifacts and feedback.

## Backend Setup
1. Create env file:
   - Copy `backend/.env.example` to `backend/.env`
2. Install dependencies:
   - `pip install -r backend/requirements.txt`
3. Run migrations:
   - `cd backend && alembic upgrade head`
4. Start backend:
   - `fastapi dev backend/main.py`

Default backend URL: `http://127.0.0.1:8000`

## Backend Environment Variables
Required (from `backend/.env.example`):
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

## Feedback Rating Format
Feedback ratings are expected as:
- `thumbs_up`
- `thumbs_down`

Dashboard and weekly insights metrics are computed using these values.

## Analytics Dashboard (Streamlit)
The dashboard reads from the same database and includes product/learning KPIs such as:
- Daily active users
- Daily activity (overall + by mode)
- Attempts by mode
- Feedback trend (diverging thumbs up/down)
- Avg attempts by problem order (overall + by mode)
- Problem-level figures (including finished problem ratio)
- First-solve metrics
- Useful hint ratio and unclear fix rate
- Top error types and unclear-attempt ratio trend
- Optional LLM summary of feedback comments for selected date range

### Run Dashboard
1. Install dependencies:
   - `pip install -r analytics_dashboard/requirements.txt`
2. Create env file:
   - Copy or create `analytics_dashboard/.env` with database + LLM settings
3. Start Streamlit:
   - `streamlit run analytics_dashboard/app.py`

## Weekly Insights Pipeline
Script: `analytics_dashboard/weekly_insights.py`

What it does:
- Computes weekly metrics
- Stores insights in DB tables
- Evaluates trigger rules
- Creates deduplicated GitHub issues when thresholds are breached

### Run Weekly Insights Manually
- `python3 analytics_dashboard/weekly_insights.py`

### Suggested Automation
- Run weekly via GitHub Actions or cron.

### Env vars for GitHub issue creation
- `GITHUB_TOKEN`
- `GITHUB_REPO` (format: `owner/repo`)

## Frontend Setup (iOS)
In `ai_lifecycle_frontend`:
1. Open project in Xcode.
2. Set backend base URL.
3. Build/run app.

## Notes
- `.env` files are gitignored; keep secrets out of version control.
- For local HTTP development, `COOKIE_SECURE=false` is expected.
