# Ratatoskur - Final Project Report

This report follows the required 8-section final-project structure and documents the current final-state system.

## 4.1 Problem & Users
Ratatoskur addresses a specific learning problem: students often get stuck while solving math problems on paper, but the support tools available to them are either too generic (full-solution calculators) or too rigid (static exercise books). In practice, many students need help that is contextual, step-aware, and available exactly at the moment they are working through their own handwritten solution. The core product goal is therefore not just to provide an answer, but to provide tutoring feedback that matches the student's current step, catches mistakes early, and preserves the student's own reasoning process.

Our primary target users are students who solve algebra and fraction problems by hand and want formative feedback while practicing. A secondary user group is teachers or mentors who need clearer visibility into recurring student errors and progress trends. Before using Ratatoskur, these users typically rely on a combination of class notes, manual checking, web calculators, and occasional teacher/peer help. That workflow is fragmented: it does not preserve step history well, and it provides little structured insight into repeated error patterns.

An AI/LLM-based approach is appropriate because the interaction is language- and context-heavy. The system needs to interpret imperfect handwritten input, reason about mathematical steps, decide feedback mode (`hint`, `check_solution`, `reveal`), and produce pedagogically useful explanations in Icelandic. This is a poor fit for rigid rule-only interfaces, but a strong fit for structured LLM orchestration with guardrails.

Our understanding of the problem evolved materially since Assignment 1. Initially, we framed the challenge mostly as "give useful hints from a student's handwritten solution." Through development and testing, we learned that the harder problem is reliability under real-world input quality and real-world user behavior. Students submit multi-page work, handwriting can be ambiguous, users move between pages and drafts mid-solution, and UX clarity around folders, image capture, and controls strongly affects whether AI feedback is even trusted. The final system reflects this broader framing: not only generating feedback, but supporting a dependable end-to-end learning workflow.

## 4.2 Technical Architecture
Ratatoskur is implemented as an iOS frontend with a Python backend and external model/storage services. The architecture intentionally separates interaction, orchestration, persistence, and observability concerns.

**Figure 1. System architecture (same diagram as presentation):**
![Ratatoskur system architecture](https://raw.githubusercontent.com/JoRE13/ai_lifecycle/main/final_assignment_deliverables/background.png)

From a data-flow perspective, the primary path begins when a user creates or opens a problem and writes one or more handwritten pages. The frontend sends problem image data, solution pages, drawing payloads, selected mode, and context metadata to `/query`. The backend validates payload structure and limits, runs legibility and reasoning (or single-pass reasoning, depending on runtime settings), persists artifacts and attempt metadata, and returns structured feedback. Attempts, error events, and stage metrics are then available for analytics summaries, error-bank views, and personalized exam targeting.

A parallel flow exists for exam preparation. Users create an exam pack (auto-targeted from personal error history or manually targeted), start/resume sessions, answer items, and receive per-question or end-exam feedback depending on selected mode.

Technology choices were driven by iteration speed and reliability trade-offs. SwiftUI and PencilKit gave native handwriting support and fast UI iteration on iPad. FastAPI with SQLModel/Postgres gave a typed API layer and relational integrity for attempts, analytics events, error events, folders, and exam entities. Cloudflare R2 separated binary artifact storage from relational metadata. Gemini models provided multimodal reasoning with structured JSON output contracts, and Langfuse provided trace-level observability for debugging, latency, and cost awareness.

Prompt management is explicit and versioned in the backend prompt tree (`prompts/...`). We maintain prompt versions by capability family (modes, legibility, errors, exam generation/validation/grading). Runtime controls (`QUERY_PROMPT_VARIANT`, `QUERY_LEGIBILITY_PROMPT_VARIANT`, `QUERY_PIPELINE_MODE`, `expert_mode`) allow switching behavior without changing route logic. This was critical for controlled iteration from Assignment 3 to final.

## 4.3 LLM Integration & Prompt Strategy
The system uses Gemini models in a structured, task-routed way rather than a single monolithic prompt.

Our model layer is centered on the Gemini 3 Flash family, with configuration tuned by task type. In practice, the system uses different model/thinking settings across phases (for example, legibility/reasoning/error categorization), while keeping a strict JSON-schema contract at every boundary. For deferred error classification and exam answer extraction, dedicated calls are used with task-specific schemas. The key design decision was to treat model responses as typed contracts, not free text, and reject malformed outputs.

The prompting techniques that worked best were zero-shot and one/few-shot structured prompting, explicit schema-constrained outputs, mode-conditioned prompting (`hint`, `check_solution`, `reveal`) with strict behavioral boundaries, two-pass orchestration for uncertain handwriting (legibility first, reasoning second), taxonomy-guided outputs for error typing, and task-specific prompt families instead of a single universal prompt.

Prompt evolution from Assignment 3 to the final version followed a clear path. Early versions focused on baseline role instructions and output format. Later versions introduced stronger behavioral policies, few-shot grounding, stricter response consistency, and clearer unclear-input handling. Architecturally, this evolved from one prompt handling all behavior to a phased setup with focused prompts per mode plus optional legibility and explicit error-categorization prompts. The latest evaluated prompt iteration in our final flow is v6.

Several advanced patterns were implemented. First, a multi-turn clarification/confirmation loop allows the backend to return `confirm_reading` when handwriting is uncertain but interpretable, after which the user edits or approves interpreted text before grading proceeds. Second, pipeline routing allows configurable two-pass vs single-pass execution based on runtime settings. Third, expert-mode routing allows alternate prompt paths for stricter `check_solution` behavior without duplicating route logic. Fourth, deferred background analysis performs post-response error classification for analytics/error-bank updates without blocking immediate user response.

These patterns collectively improved controllability, debuggability, and user trust.

## 4.4 Evaluation & Quality Assurance
Evaluation builds directly on Assignment 3 methodology to preserve comparability. We keep the same 50-case handwritten dataset as the anchor benchmark and compare the newest prompt iteration (v6) to the Assignment 3 baseline (a3), including both label-based evaluation and LLM-as-judge scoring.

Current quantitative reference points are:
- label-based comparison: **v6 accuracy 0.96** vs **a3 accuracy 0.96**,
- non-feasibility ratio: **0** for both v6 and a3,
- LLM-as-judge aggregate score: **v6 average 3.70** vs **a3 average 3.76**,
- average latency for v6 in evaluation runs: approximately **17 seconds**.

This indicates that core decision behavior stayed stable, while pedagogical quality dimensions remained competitive but mixed across modes.

For LLM-as-judge, we score each response on five dimensions: mathematical correctness (MC), pedagogical helpfulness (PH), policy compliance (PC), clarity (C), and specificity (S), each on a 1-5 scale. Mode-level trends in the current comparison are: `check` improved slightly on policy but dropped on helpfulness/specificity, `hint` remained strong but slightly lower than a3 overall, and `reveal` improved materially (from 3.6 to 4.6 average). This is important because it shows that aggregate averages hide mode-specific quality movement; in product terms, the final flow is strongest in complete-solution explanation while still needing refinement on strict check-mode pedagogy.

The key historical failure class is ambiguous handwriting. In the current setup, the explicit legibility phase mitigates this by catching uncertain reads before final reasoning. In our current benchmark comparison, the specific legibility prompt catches one of two unclear cases in the v6 set, which confirms improvement but also highlights remaining room for robustness gains.

Quality assurance is layered across strict API-side input validation and upload constraints, typed output contracts with JSON/schema checks, bounded retry/backoff and explicit error surfacing, canonical error taxonomy normalization for analytic consistency, exam-specific validation for topics/modes/pack sizes and OCR input safety, auth/session checks with rotation semantics, and frontend preflight validation plus action-state constraints.

In short, the final system is no longer just "prompt and reply"; it is a guarded orchestration pipeline with explicit failure containment.

**Deferred refinement note:** if we run a fresh end-of-semester full evaluation pass on the same 50-case benchmark, we will replace numeric values while preserving this methodology and structure.

## 4.5 Deployment & Monitoring
The application is operated as a hybrid deployment for the final course context: backend services are hosted on Render, while the iOS frontend is run locally on test devices. This setup gives us a live cloud API environment with realistic monitoring, while preserving a manageable mobile distribution workflow for the course phase.

Monitoring combines platform-level and product-level telemetry via two operational views: a Langfuse dashboard for prompt/model traces and an admin analytics dashboard for user-behavior data. On the platform side, we track latency, token usage, cost estimates, mode/model metadata, and trace IDs. On the product side, we track attempt outcomes, error-event distributions, and feedback signals (including thumbs/comment paths) to connect technical behavior with user impact.

Evidence from prior observability runs includes an average latency around 24.823 seconds, p95 latency around 87.697 seconds, and tracked token usage with estimated cost from traced calls.

This monitoring layer is not only diagnostic; it informs product priorities. For example, user-testing feedback about perceived slowness directly matches latency/timeout patterns seen in traces and has been treated as an active optimization track rather than a one-off bug.

**Monitoring evidence from real usage:**

Figure 2. Langfuse trace view (`/query` request stage breakdown)
![Langfuse trace view](https://raw.githubusercontent.com/JoRE13/ai_lifecycle/main/final_assignment_deliverables/trace_view.png)

Figure 3. Latency over time
![Latency over time dashboard](https://raw.githubusercontent.com/JoRE13/ai_lifecycle/main/final_assignment_deliverables/latency_overtime.png)

Figure 4. Average latency and average token usage
![Average latency and token usage dashboard](https://raw.githubusercontent.com/JoRE13/ai_lifecycle/main/final_assignment_deliverables/avglatency_and_avgtokens.png)

Figure 5. Analytics/admin dashboard view
![Admin analytics dashboard view](https://raw.githubusercontent.com/JoRE13/ai_lifecycle/main/final_assignment_deliverables/dashboard_view.png)

## 4.6 Feature Plan Retrospective
In Assignment 6 we planned five core improvements. Table 1 revisits each planned item and states its final status.

| Planned A6 feature | Final status | Notes |
|---|---|---|
| User-based statistics on homepage | Completed | Expanded beyond counters to weekly context and behavior signals. |
| Error bank for users | Completed | Structured taxonomy, summaries, and detail drill-down for reflection. |
| Lower latency | Completed (with ongoing optimization) | Reduced friction via prompt/pipeline reliability improvements and observability-driven tuning. |
| Generate problems from user errors | Descoped | Scope/dependency growth; moved to backlog rather than shipping partial behavior. |
| Anonymous data collection | Partially completed | Backend schema/foundation implemented; not activated as a full in-product workflow. |

We also added major features not originally in the A6 list, including an explicit legibility phase, explicit error categorization, agentic-vision style error detection workflow, one-level folder/subfolder organization with safer archive/delete behavior, extensive PDF workflow upgrades, substantial writing/notebook/toolbar UX stabilization (including canvas and fullscreen behavior), share-problem workflows, and stronger onboarding/profile clarity updates.

This retrospective shows that the roadmap was largely delivered, but also that usability and reliability discoveries during testing caused us to invest more heavily in interaction quality than initially forecast.

## 4.7 User Testing & Interaction Data
We conducted moderated testing with five external participants (non-group members), each completing a standardized six-task scenario designed to cover the primary flow: account/folder setup, solving and iterating on problems, hint usage, seeded-error recovery, error-bank inspection, and PDF submission creation/export. Sessions were approximately 20 to 30 minutes, with think-aloud prompting and no intervention unless a participant was blocked for more than about 60 seconds.

All participants completed all tasks (30/30 total completions), which indicates that the system is operable end-to-end under guided testing. However, completion alone did not mean smooth UX. Timing patterns and think-aloud notes showed that the most time-consuming tasks were those involving multi-step problem solving and AI feedback waits.

Interaction timing data (from `task_results_filled.csv`, with one documented outlier excluded: U4-T5 = 54:49) is summarized below:

| Task | Description (short) | Median time | Mean time |
|---|---|---:|---:|
| T1 | Login + folder + subfolder | 2m 24s | 2m 29s |
| T2 | Solve + review + show solution | 4m 37s | 4m 20s |
| T3 | New problem + hint + complete | 4m 42s | 4m 31s |
| T4 | Seeded error + recovery | 4m 01s | 3m 39s |
| T5 | Open error bank entry | 0m 22s | 0m 28s |
| T6 | Create/export PDF submission | 1m 45s | 1m 41s |

SUS results were 72.5, 67.5, 95.0, 72.5, and 92.5 (mean 80.0, median 72.5), indicating above-average usability with noticeable friction clusters. Qualitative findings were consistent across users: folder hierarchy discoverability was confusing in earlier versions, latency/timeout behavior reduced trust in some flows, media/canvas control discoverability needed better affordances, and missing name capture during registration caused downstream PDF friction.

Interaction data also exposed unexpected behavior patterns: users often navigated to incorrect folder locations first, interpreted add-page actions differently than intended, and sometimes attempted camera capture flows that behaved inconsistently. These patterns informed concrete redesign work in folder IA, onboarding, media flow, and control placement.

The key point is that feedback did not remain descriptive; it was translated into shipped changes. We can now show a clear chain from user observation to product update.

## 4.8 Lessons Learned & Next Iteration
If we started over, we would front-load two areas much earlier: interaction architecture and failure-state design. Early project effort prioritized "can the model produce useful feedback?" That question mattered, but user testing showed that trust depends equally on how the app behaves when inputs are unclear, slow, or incomplete. In hindsight, legibility uncertainty, navigation clarity, and long-session writing ergonomics should have been treated as core product constraints from the beginning, not as late-stage polish.

For the next AI lifecycle iteration, we would expand data collection and iteration loops in three directions. First, we would deepen quality instrumentation for hint usefulness and failure categorization, so prompt changes can be evaluated with faster feedback cycles. Second, we would formalize privacy/consent UX so users can understand and control data usage directly in-app. Third, we would improve adaptive practice generation by incorporating richer temporal patterns (for example, recency-weighted errors and concept drift over time), not just aggregate historical frequency.

Our most important **technical** takeaway is that reliability in AI products comes from orchestration discipline: typed outputs, staged validation, explicit fallback paths, and traceable execution metadata. Our most important **non-technical** takeaway is that user trust is highly sensitive to interaction clarity. Even strong model behavior is undervalued when UI signals are ambiguous or latency feels unexplained. The strongest outcomes came when model design, product design, and user-testing feedback were treated as one integrated loop rather than separate tracks.

---

## Coverage Note
This report explicitly covers every required written-report section (`4.1` through `4.8`) from the final project specification.  
The report content is submission-ready; remaining work is packaging deliverables (slides PDF + report markdown in the final zip) and final presentation/demo execution.
