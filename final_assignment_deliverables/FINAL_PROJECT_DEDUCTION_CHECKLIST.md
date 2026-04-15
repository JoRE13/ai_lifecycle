# Final Project Deduction Checklist

Date checked: 2026-04-15  
Scope: `ai_lifecycle` repo + `final_assignment_deliverables` folder

This checklist follows the deduction list in `final_project.pdf` and marks each item as:
- `PASS`: satisfied in repo/report artifacts
- `MANUAL VERIFY`: cannot be fully verified from local files only
- `ACTION NEEDED`: missing artifact or required pre-submission step

## Report & Deliverables

| Requirement | Status | Evidence / Note |
|---|---|---|
| Slides submitted as PDF | ACTION NEEDED | Current slides file is `REI603M_FinalProject_presentation.typ`. Export to PDF before submission. |
| Written report submitted | PASS | `REI603M_FinalProject_jre5_sos106_sbs8.md` present. |
| `.env.example` provided (no real keys) | PASS | `backend/.env.example` is tracked. |
| README has setup/run instructions | PASS | Root `README.md` includes backend/dashboard/frontend setup/run steps. |
| Secrets committed to repo | PASS | No tracked `.env`; quick key-pattern scan found no obvious committed secrets. |
| Repo shared with `haffi112` | MANUAL VERIFY | Needs GitHub-side check in repository settings/access list. |

## 4.1 Problem & Users

| Requirement | Status | Evidence |
|---|---|---|
| Clear problem definition | PASS | Report section `4.1`. |
| Target users identified | PASS | Report section `4.1`. |
| AI/LLM approach justified | PASS | Report section `4.1`. |

## 4.2 Technical Architecture

| Requirement | Status | Evidence |
|---|---|---|
| System diagram included | PASS | Report section `4.2` with `background.png`. |
| Key technology choices explained | PASS | Report section `4.2`. |
| Data flow described | PASS | Report section `4.2`. |
| Prompt management described | PASS | Report section `4.2`. |

## 4.3 LLM Integration & Prompt Strategy

| Requirement | Status | Evidence |
|---|---|---|
| Model choice explained | PASS | Report section `4.3`. |
| Prompting techniques discussed | PASS | Report section `4.3`. |
| Prompt evolution from A3 shown | PASS | Report section `4.3`. |
| Advanced patterns described | PASS | Report section `4.3`. |

## 4.4 Evaluation & Quality Assurance

| Requirement | Status | Evidence |
|---|---|---|
| Evaluation methodology + dataset | PASS | Report section `4.4` (50-case handwritten benchmark, v6 vs a3). |
| Quantitative/qualitative results | PASS | Report section `4.4` + user testing section `4.7`. |
| Error/failure analysis | PASS | Report section `4.4`. |
| Guardrails/output validation | PASS | Report section `4.4`. |

## 4.5 Deployment & Monitoring

| Requirement | Status | Evidence |
|---|---|---|
| Deployment described | PASS | Report section `4.5` (Render backend + local iOS clients). |
| Observability beyond A4 baseline | PASS | Report section `4.5` (Langfuse + admin dashboard). |
| Metrics tracked | PASS | Report section `4.5` (latency, tokens, cost, quality signals). |
| Dashboard/trace shown from usage | PASS | Embedded: `trace_view.png`, `latency_overtime.png`, `avglatency_and_avgtokens.png`, `dashboard_view.png`. |

## 4.6 Feature Plan Retrospective

| Requirement | Status | Evidence |
|---|---|---|
| A6 planned features revisited | PASS | Report section `4.6` table. |
| Completed/descoped/added features accounted for | PASS | Report section `4.6`. |

## 4.7 User Testing & Interaction Data

| Requirement | Status | Evidence |
|---|---|---|
| User testing conducted | PASS | `5` external users documented in section `4.7`. |
| At least 5 external users | PASS | SUS/task files show U1-U5 external participants. |
| Testing methodology described | PASS | Report section `4.7`. |
| Findings + feedback presented | PASS | Report section `4.7` + filled findings log. |
| Interaction data shown | PASS | Report section `4.7` timing table + SUS metrics. |

## 4.8 Lessons Learned & Next Iteration

| Requirement | Status | Evidence |
|---|---|---|
| Reflection on what to do differently | PASS | Report section `4.8`. |
| Next lifecycle iteration described | PASS | Report section `4.8`. |
| Technical + non-technical takeaway | PASS | Report section `4.8`. |

## Presentation-Time Requirements (not fully verifiable in repo)

| Requirement | Status | Note |
|---|---|---|
| Live demo during presentation | MANUAL VERIFY | Must be performed in session. |
| Demo includes primary flow | MANUAL VERIFY | Prepare runbook for slides 8-10. |
| Demo includes monitoring/observability | MANUAL VERIFY | Use the same monitoring assets shown in section 4.5. |

## Final Pre-Submission Actions

1. Export `REI603M_FinalProject_presentation.typ` to PDF.
2. Keep report filename as `REI603M_FinalProject_jre5_sos106_sbs8.md`.
3. Zip deliverables for Canvas: slides PDF + final report markdown (and any required supporting assets if desired).
4. Confirm GitHub repo access includes `haffi112`.
