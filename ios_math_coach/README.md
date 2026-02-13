# iOS Math Coach (SwiftUI + PencilKit)

This folder contains a SwiftUI-first iPad frontend scaffold for the AI Math Coach.

## Scope

- Auth flow: register, login, refresh, me, logout
- Notebook-style view with Pencil input
- Mode-constrained AI actions: hint, check_solution, reveal
- Multipart query upload using:
  - `mode`
  - `prob_image`
  - `sol_image`

## Backend expectations

- FastAPI backend running and reachable from iPad
- Endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
  - `POST /auth/refresh`
  - `GET /auth/me`
  - `POST /auth/logout`
  - `POST /query`

## Setup notes

1. Open Xcode on macOS and create a new iOS App project (SwiftUI lifecycle).
2. Copy the contents of `MathCoach/` into the app target.
3. Add `Config.xcconfig` and set `BACKEND_BASE_URL`.
4. If backend is non-HTTPS in local dev, add ATS exception in `Info.plist`.
5. Run on iPad (or iPad Simulator for layout checks).

## Demo flow

1. Authenticate.
2. Select/upload problem image.
3. Write solution steps with Apple Pencil.
4. Select mode (`hint`, `check_solution`, `reveal`).
5. Submit and render `message_is` from backend JSON response.
