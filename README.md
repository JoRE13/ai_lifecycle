# Backend (FastAPI)

This README covers the backend only (`backend/`).

## Stack

- FastAPI
- SQLModel + SQLAlchemy
- Alembic migrations
- JWT access tokens + refresh-token cookies
- Gemini API (for `/query`)
- Cloudflare R2 (artifact storage for `/query`)

## Project structure

- `backend/main.py`: FastAPI app entrypoint and router registration.
- `backend/routes/`: API endpoints (`auth`, `problem`, `query`).
- `backend/auth/`: JWT creation/validation and auth dependencies.
- `backend/models/`: SQLModel table models.
- `backend/schemas/`: Pydantic request/response schemas.
- `backend/repositories/`: auth-related DB operations.
- `backend/storage/`: R2 upload helpers.
- `backend/alembic/`: DB migrations.

## Environment variables

Create `backend/.env` with the following:

### Required

- `DATABASE_URL`: Postgres connection string.
- `JWT_SECRET`: JWT signing key.
- `GEMINI_API_KEY`: Gemini API key (required by `backend/llm.py` at import time).

### Auth and cookie settings

- `JWT_ALG` (default: `HS256`)
- `ACCESS_TOKEN_TTL_MIN` (default: `15`)
- `REFRESH_TOKEN_TTL_DAYS` (default: `30`)
- `REFRESH_COOKIE_NAME` (default: `refresh_token`)
- `COOKIE_SECURE` (default: `false`)
- `COOKIE_SAMESITE` (default: `lax`)
- `COOKIE_PATH` (default: `/`)

### Required for `/query` artifact storage (Cloudflare R2)

- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`

### Optional R2 settings

- `R2_ENDPOINT_URL` (default: `https://<R2_ACCOUNT_ID>.r2.cloudflarestorage.com`)
- `R2_REGION` (default: `auto`)

### Optional tracing (Langfuse)

- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_HOST` or `LANGFUSE_BASE_URL`

## Local development

From repo root:

1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r backend/requirements.txt`
3. Run migrations:
   `cd backend && alembic upgrade head`
4. Start the API:
   `fastapi dev backend/main.py`

Default local URL: `http://127.0.0.1:8000`

## API endpoints

- `GET /health`: health check, returns `{ "ok": true }`.
- `POST /auth/register`: register user, sets refresh cookie, returns access token.
- `POST /auth/login`: login, sets refresh cookie, returns access token.
- `POST /auth/refresh`: rotate refresh token cookie, return new access token.
- `POST /auth/logout`: revoke refresh token (if present), clear cookie.
- `GET /auth/me`: return authenticated user (`Bearer` token required).
- `POST /problem`: create problem for current user (`Bearer` required).
- `GET /problems`: list current user problems (`Bearer` required).
- `GET /problems/{problem_id}/attempts`: list attempts for one problem (`Bearer` required).  
  Each attempt includes `id`, `problem_id`, `user_id`, `mode`, `solution_image_key`, `verdict`, `response_type`, `message_is`, `created_at`.
- `POST /query`: submit `problem_id`, `mode`, `prob_image`, `sol_image`, `drawing_data` (multipart, `Bearer` required). Calls LLM, stores artifacts in R2, saves attempt, returns model JSON.

## Notes

- `backend/db.py` requires `DATABASE_URL`; app startup fails if it is missing.
- `backend/llm.py` initializes Gemini client at import time; app startup fails if `GEMINI_API_KEY` is missing.
- For local HTTP dev, `COOKIE_SECURE=false` is expected. Use `true` in production over HTTPS.
