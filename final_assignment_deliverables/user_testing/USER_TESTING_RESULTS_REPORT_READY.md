# User Testing Results (Report + Slides Ready)

This file consolidates the imported data from:
- `raw_inputs/SUS.pdf`
- `raw_inputs/SESSION_NOTES.pdf`
- `raw_inputs/SUS_extracted_layout.txt`
- `raw_inputs/SESSION_NOTES_extracted.txt`

Use this directly for the Final Project report section 4.7 and presentation slides 11.

## Sample and Method
- External participants: 5 (U1-U5)
- Facilitators: Solvi Santos (U1, U2, U4), Johannes Reykdal Einarsson (U3, U5)
- Devices: iPad
- Protocol: 6-task moderated usability test + think-aloud + post-task debrief + SUS questionnaire
- Core research questions:
  - Can users complete the primary flow without help?
  - What unexpected actions do users attempt?
  - Is response time acceptable?

## Task Completion
- Completion rate: 100% on all 6 tasks for all 5 participants (30/30 task completions)
- Typical completion times:
  - Fastest flows: T1/T5/T6
  - Slowest flows: T2/T3/T4 (influenced by LLM wait time and occasional server timeouts)
- Detailed per-task timings and notes are in `task_results_filled.csv`.

## SUS Results
From `sus_responses_filled.csv`:
- U1: 72.5
- U2: 67.5
- U3: 95.0
- U4: 72.5
- U5: 92.5

Aggregate:
- Mean SUS: 80.0
- Median SUS: 72.5
- Interpretation: overall above-average usability with clear UX friction points.

Data quality notes:
- SUS forms 3 and 5 had blank participant/date text fields in the PDF. They were mapped by tab order to U3 (2026-04-10) and U5 (2026-04-13) using session chronology.
- One timing entry in session 4 task 5 appears anomalous (`54:49`) and should be treated as a recording artifact/outlier.

## Top Findings (Prioritized)
1. Folder/subfolder information architecture was unclear (5/5 users, high severity).
2. Perceived latency and occasional timeout/server-error episodes reduced trust and flow (4/5 users, high severity).
3. Media and action discoverability issues (camera source consistency, fullscreen/control discoverability, add-page meaning) created repeated friction (3/5 users, medium severity).
4. Profile data dependency for PDF export (name missing during signup) caused unnecessary navigation detours (4/5 users, medium severity).
5. Hint quality consistency needs continued tuning (occasional over-revealing or badly formatted response) (low frequency, medium severity when it appears).

Detailed finding-level evidence and status are in `findings_log_filled.csv`.

## Unexpected Behaviors Observed
- Users often navigated to the wrong place first when creating subfolders.
- Several users interpreted add-page as add-problem.
- Some users attempted camera capture but landed in camera roll first.
- Users often scrolled/doodled while waiting for AI responses.

## Product Changes Triggered by Testing
Already implemented or underway based on these sessions:
- Clearer folder hierarchy and navigation structure in dashboard/full problem views.
- Registration now includes name input for downstream PDF workflow.
- Stronger avatar selected-state affordance in registration/profile flows.
- Notebook/control discoverability improvements and improved control placement.
- Ongoing work on hint behavior and robustness/fallback for slow or poor model responses.

## Copy-Paste Blocks for Deliverables
### Report (Section 4.7)
We conducted moderated user testing with five external participants (not group members), each completing a six-task end-to-end workflow on iPad. All participants completed all tasks (30/30), but recurring friction points appeared in folder/subfolder discoverability, latency perception, and action discoverability in the notebook flow. SUS scores were 72.5, 67.5, 95.0, 72.5, and 92.5 (mean 80.0, median 72.5), indicating overall above-average usability despite identifiable UX bottlenecks. Findings were translated into concrete improvements, including restructuring folder navigation, adding required name capture during registration for PDF export, and clarifying selected avatar/control states. We also identified ongoing quality work around hint consistency and latency fallback behavior.

### Slide 11 (User Testing)
- 5 external users, 6-task moderated test, iPad
- Task completion: 30/30 (100%)
- SUS: mean 80.0 (scores: 72.5, 67.5, 95.0, 72.5, 92.5)
- Main issues:
  - Folder/subfolder clarity (5/5)
  - Latency/timeout trust impact (4/5)
  - Camera/control discoverability friction (3/5)
- Shipped improvements:
  - Folder IA redesign
  - Name capture in registration for PDF flow
  - Avatar and control affordance improvements
- Remaining focus:
  - Hint robustness/consistency
  - Stronger fallback behavior on slow model responses
