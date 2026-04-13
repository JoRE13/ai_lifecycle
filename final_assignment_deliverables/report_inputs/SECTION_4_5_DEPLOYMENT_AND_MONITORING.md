# Section 4.5 - Deployment & Monitoring (Draft Input)

## Deployment Decision
- Platform: native iOS app (SwiftUI + PencilKit).
- Decision: no public deployment for the course final.
- Reason: iOS distribution/deployment cost overhead is not justified for this project stage.
- Teacher confirmation: deployment exemption accepted for this case.

## Current Runtime Setup (for demo/testing)
- iOS frontend: run locally from Xcode on iPad/iPhone.
- Backend API: local FastAPI server.
- Database: Neon Postgres.
- Object storage: Cloudflare R2 (uploaded artifacts).
- Analytics/monitoring: Langfuse traces + observations, plus local analytics dashboard.

## Monitoring/Observability Stack
Based on Assignment 4 and Assignment 6 presentation material:
- Langfuse integrated in backend (trace + generation events).
- Per-call tracking includes:
  - mode
  - model
  - latency
  - input/output/total tokens
  - trace IDs
- Product-side tracking focus:
  - where users succeed
  - where users get stuck
  - failure moments
  - thumbs up/down signals and optional comments

## Metrics We Track
Confirmed metrics:
- Latency
- Token usage
- Estimated cost

Also tracked in prior presentations/tooling:
- Model + mode breakdown
- Trace IDs for debugging
- Feedback signals (thumbs up/down, comments)
- Usage/flow behavior trends via dashboard

## Concrete Evidence Already Available (from prior work)
From Assignment 4 slides (observability section):
- aggregate sample of 37 generation calls
- average latency: 24.823s
- p95 latency: 87.697s
- total tokens: 218,662
- estimated total cost: $0.313946
- example trace walk-through with per-request latency/tokens

## What To Add Later (before final submission/presentation)
1. 1-3 screenshots from current Langfuse views:
   - trace detail view
   - latency/token overview
   - any quality/feedback trend view
2. one short "real incident" example:
   - e.g. slow or malformed hint response
   - what users experienced
   - mitigation or fallback behavior
3. final phrasing in report to reflect "locally operated system" rather than cloud-deployed app.

## Deferred By Team (tracked)
Decision date: 2026-04-13

The following items are intentionally deferred and will be completed later:
1. Capture and insert 1-3 current monitoring screenshots (Langfuse/dashboard).
2. Add one concrete recent incident example (slow/bad response + handling/mitigation).
3. Decide whether to keep A4 baseline metrics or replace with newer final-phase metrics.

## Copy-Ready Paragraph (Report)
Our application is a native iOS product, and for the course final we operate it as a locally run system rather than a publicly deployed service. This deployment decision was discussed with and accepted by the instructor, primarily due to iOS distribution cost overhead at this stage. The frontend runs through Xcode on iPad/iPhone, with a FastAPI backend, Neon Postgres for core data, and Cloudflare R2 for artifact storage. For observability, we instrument backend requests with Langfuse traces and generation events, tracking latency, token usage, estimated cost, model/mode metadata, and trace IDs for debugging. In addition, product-level signals (such as feedback and usage patterns) are used together with technical traces to guide iteration priorities.

## Slide-Ready Bullets (Presentation)
- Native iOS app; operated locally for final demo (teacher-approved no-public-deploy path)
- Stack: SwiftUI/PencilKit + FastAPI + Neon Postgres + Cloudflare R2
- Monitoring: Langfuse traces (latency, tokens, cost, trace IDs) + product feedback signals
- We use monitoring for both debugging and product decisions
