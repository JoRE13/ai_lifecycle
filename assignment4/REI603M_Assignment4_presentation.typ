#import "@preview/touying:0.6.1": *
#import "@preview/typslides:1.3.2": *

#show: typslides.with(
  ratio: "16-9",
  theme: "bluey",
  font: "Fira Sans",
  font-size: 20pt,
  link-style: "color",
  show-progress: true,
)

// =======================
// Slide 1 — Title + Team
// =======================
#front-slide(
  title: "AI Math Tutor\nAssignment 4 — Prototype Sprint",
  authors: "Jóhannes Reykdal Einarsson · Sævar Breki Snorrason · Sölvi Santos",
  info: [
    Course: REI603M — The AI Lifecycle,
    iOS Frontend + FastAPI Backend + Gemini,
    February 2026,
  ],
)

// =======================
// Slide 2 — Problem & User Persona
// =======================
#slide(title: "Problem & User Persona", outlined: true)[
  - Primary users:
    - secondary school students solving algebra/calculus homework by hand.
  - Core problem:
    - students get stuck mid-solution and need step-level guidance, not answer dumping.
  - Product intent:
    - preserve learning flow with mode-controlled tutoring:
      - *Hint* (Socratic, one-step guidance),
      - *Check Step* (first-error feedback),
      - *Reveal* (full solution only on explicit request).
  - Success criterion for prototype sprint:
    - runnable end-to-end app with real LLM calls, observability, and measured evaluation.
]

// =======================
// Slide 3 — Architecture Overview
// =======================
#slide(title: "Architecture Overview", outlined: true)[
  - Frontend (iOS, SwiftUI + PencilKit):
    - auth, problem selection, handwritten canvas, mode selection, result display.
  - Backend (FastAPI + SQLModel + Alembic):
    - auth/session handling, prompt loading, LLM orchestration, persistence.
  - LLM + Data:
    - Gemini (`models/gemini-3-flash-preview`) for multimodal reasoning.
    - Neon Postgres for users/problems/attempts.
    - Cloudflare R2 for uploaded artifacts.
  - Observability:
    - Langfuse traces + observations for latency/token/cost visibility.
]

// =======================
// Slide 4 — LLM Integration
// =======================
#slide(title: "LLM Integration", outlined: true)[
  - Model:
    - Gemini 3 Flash Preview (`models/gemini-3-flash-preview`).
  - Prompt management:
    - prompt stored in dedicated file (`backend/prompt.txt`), not scattered inline.
    - live demo uses our revised *v2* prompt.
  - Structured output contract (Pydantic schema):
    - `verdict`, `response_type`, `message_is`.
  - Reliability controls:
    - server-error retries with exponential backoff,
    - JSON parse validation,
    - graceful HTTP errors for invalid input / API failures.
]

// =======================
// Slide 5 — Observability Setup
// =======================
#slide(title: "Observability Setup", outlined: true)[
  #columns(2, gutter: 12pt)[

    - Tooling:
      - Langfuse integrated in backend (`trace` + `generation` events).

    - What we track per call:
      - mode, model, latency,
      - input/output/total usage tokens,
      - trace IDs for debugging.

    - Aggregate metrics (37 generation calls):
      - average latency: **24.823s**
      - p95 latency: **87.697s**
      - total tokens: **218,662** (incl. thought tokens)
      - estimated total cost: **\$0.313946**

    - Example evidence (filtered observations export):
    #image("langfuse_observations_filtered_table.png", width: 100%)

  ]
]


// =======================
// Slide 6 — Evaluation Results
// =======================
#slide(title: "Evaluation Results", outlined: true)[
  - Assignment 3 test cases executed through prototype flow:
    - **20 tested cases** (requirement satisfied).
    - mode split: 9 check_solution, 9 hint, 2 reveal.
  - Prototype metrics (tested subset):
    - verdict accuracy: **95.00%**
    - non-feasible ratio: **0.00%**
  - Comparison to A3 v4 baseline on same 20 images:
    - A3 subset: **95.00%**, non-feasible **0.00%**
    - Delta (A4 - A3 subset): **0.00%**
  - Reference:
    - A3 full v4 (50 rows): **96.00%**, non-feasible **0.00%**.
]

// =======================
// Slide 7 — Failure Analysis
// =======================
#slide(title: "Failure Analysis", outlined: true)[
  - Failure mode categorization (A4 app-stack run):
    - observed model-level failure: ambiguity handling mismatch (same known issue as A3).
    - observed app-layer UI failures: none in tested run (`0/20`).
  - Observed mismatch in A4 test run (same known issue as A3):

  - App-layer reliability observation:
    - UI-breaking failures observed: **0 / 20** tested cases.
    - measured UI reliability in this run: **100%** (fallback handling prevented user-facing breakage).
    
  - Interpretation:
    - this is primarily a model-level ambiguity handling issue, not a frontend/backend integration bug.
  - Potential app-layer failure modes to monitor (not observed in this run):
    - UI rendering/truncation of long `message_is` outputs in response cards.
    - request timeout or upload failures for large/problematic images.
    - auth/token refresh failure causing silent request drops in long sessions.
    - mode-mapping mismatch between frontend selection and backend request payload.
  - Mitigation plan:
    - stricter uncertainty triggers in prompt,
    - increase ambiguous-handwriting regression cases,
    - add targeted app-layer regression tests for UI rendering, timeout handling, and auth refresh,
    - keep targeted regression set for ambiguity-sensitive examples.
]

// =======================
// Slide 8 — DEMO Part 1
// =======================
#slide(title: "DEMO (1/3) — Primary User Flow", outlined: true)[
  - Live walkthrough:
    - login/register,
    - create/open problem,
    - upload problem image + write solution on canvas,
    - submit in `Hint` mode.
  - What to highlight:
    - real API request through `/query`,
    - structured tutor response rendered in app.
]

// =======================
// Slide 9 — DEMO Part 2
// =======================
#slide(title: "DEMO (2/3) — Mode Behavior", outlined: true)[
  - Show mode switching on same problem:
    - `Check Step` -> identifies first error,
    - `Reveal` -> full step-by-step solution only on explicit request.
  - Confirm expected policy behavior:
    - no full solution leakage in `Hint`/`Check Step` modes.
  - Show attempt history load for the problem.
]

// =======================
// Slide 10 — DEMO Part 3
// =======================
#slide(title: "DEMO (3/3) — Trace Walkthrough", outlined: true)[
  - Open Langfuse trace live:
    - Trace ID: `21d643eb2b0db13eb9bd40e224669e59`.
  - Walk through one request:
    - mode: `hint`,
    - model: `models/gemini-3-flash-preview`,
    - latency: `6.982s`,
    - tokens: input `3686`, output `103`, thought `806`, total `4595`.
  - Explain why this matters:
    - trace-level debugging + performance/cost transparency.
]

// =======================
// Slide 11 — Engineering Reflection
// =======================
#slide(title: "Engineering Reflection", outlined: true)[
#columns(2, gutter:5pt)[

  - Architecture decisions:
    - SwiftUI iOS client for tablet handwriting UX,
    - FastAPI backend for typed API contracts + orchestration,
    - Langfuse for low-friction observability.

  - PRD vs reality:
    - built core primary flow (auth, problems, hint/check/reveal, persistence).
    - descoped advanced OCR correction and personalization loops.

  #colbreak()

  - Team work split:
    - Sölvi Santos: App Developer (frontend, core user flow).
    - Jóhannes Reykdal Einarsson: LLM Engineer (prompting, model integration, response policy).
    - Sævar Breki Snorrason: Ops + Eval Engineer (observability, metrics, evaluation runs, demo support).

  - LLM-assisted development:
    - used for prompt iteration, schema/policy wording, and debugging support;
      

]

]

// =======================
// Slide 12 — Next Steps
// =======================
#slide(title: "Next Steps", outlined: true)[
  - Improve robustness:
    - expand ambiguity dataset and enforce clarification-first behavior under uncertainty.
  - Reduce latency:
    - optimize image preprocessing/context size and tune model/runtime configuration.
  - Strengthen eval loop:
    - run full 50-case app-stack regression on each prompt revision.
  - Product roadmap:
    - richer attempt analytics, better handwriting ambiguity handling,
      and broader topic coverage beyond current math scope.
]
