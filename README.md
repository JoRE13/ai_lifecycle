# ai_lifecycle

Project repository for course The AI Lifecycle.

Team

- Johannes Reykdal Einarsson | jre5@hi.is
- Solvi Santos | sos106@hi.is
- Saevar Breki Snorrason | sbs87@hi.is

Project architecture

- `backend/`: FastAPI + SQLModel + Alembic. API, auth, DB models, migrations.
- `my_app/`: Frontend app (React/Next). UI and API client.

Backend structure (high level)

- `backend/main.py`: FastAPI entrypoint.
- `backend/routes/`: HTTP routes.
- `backend/auth/`: JWT utilities + auth dependencies.
- `backend/models/`: SQLModel models.
- `backend/repositories/`: DB access and auth logic.
- `backend/alembic/`: migrations.

Frontend structure (high level)

- `my_app/api.ts`: API client used by components.
- `my_app/components/`: UI components.
- `my_app/app/`: Next app routes/pages (if used).

Environment configuration

Backend env (`backend/.env`)

- `DATABASE_URL`: Postgres connection string (required).
- `JWT_SECRET`: secret used to sign tokens (required for real deployments).
- `JWT_ALG`: JWT algorithm, default `HS256`.
- `ACCESS_TOKEN_TTL_MIN`: access token TTL in minutes.
- `REFRESH_TOKEN_TTL_DAYS`: refresh token TTL in days.
- `REFRESH_COOKIE_NAME`: cookie name for refresh token.
- `COOKIE_SECURE`: `true` on HTTPS, `false` for local dev.
- `COOKIE_SAMESITE`: `lax` recommended for local dev; use `none` for cross-site.
- `COOKIE_PATH`: usually `/`.

Frontend env (`my_app/.env`)

- `BASE_URL`: backend base URL, e.g. `http://127.0.0.1:8000`.

Important: do not commit real secrets for production. For shared setup, create a local `.env`
with dev values or use a `.env.example` template.

Local setup

1. Create virtualenv and install backend deps:
   `pip install -r requirements.txt`
2. Set backend env in `backend/.env`.
3. Run migrations:
   `cd backend && alembic upgrade head`
4. Run backend:
   `fastapi dev backend/main.py`
5. Set frontend env in `my_app/.env`, then run frontend per its package manager.

Notes

- `COOKIE_SECURE=false` for local dev; set to `true` in prod.
- If frontend and backend are on different domains, set `COOKIE_SAMESITE=none` and
  `COOKIE_SECURE=true`.
