# Ratatoskur User Testing Packet (Google Docs Ready)

Version: 1.1  
Project: REI603M Final Project  
Date: 2026-04-07

## 1. Purpose
This packet standardizes 5 external-user test sessions so two facilitators can run sessions consistently and combine results in one report.

Research questions:
1. Can a user complete the primary flow without help?
2. What do users try that we did not expect?
3. Does the response time feel acceptable?

## 2. Team Split
Use these IDs in all notes, logs, and screenshots.

| User ID | Facilitator | Planned Date | Status |
|---|---|---|---|
| U1 | Facilitator A |  |  |
| U2 | Facilitator A |  |  |
| U3 | Facilitator A |  |  |
| U4 | Facilitator B |  |  |
| U5 | Facilitator B |  |  |

## 3. Session Timing
Target session length: 20 to 30 minutes.

1. Intro and consent: 1 to 2 min
2. Tasks: 12 to 20 min
3. Debrief questions: 3 to 5 min
4. SUS questionnaire: 2 to 3 min

## 4. Pre-Session Checklist
- App build is running and reachable on test device.
- Test account is ready.
- Logging/observability is active.
- This packet + session notes template is open.
- Facilitator knows rule: do not help unless user is blocked for over 60 seconds.

## 5. Facilitator Intro Script
Read this verbatim:

"Thanks for helping us test. We are testing the product, not you.  
There are no right or wrong actions.  
Please think out loud while you use the app and tell me what you expect to happen.  
I will mostly stay quiet and take notes.  
If you are stuck for a while, I may give a small hint.  
Is it okay if I take notes on your actions and feedback?"

## 6. Task Script (Give One Task At A Time)

### Task 1
"Skráðu þig inn og búðu til nýja möppu og eina undirmöppu."

Success criteria:
- User logs in.
- User creates one root folder.
- User creates one subfolder inside that root folder.

### Task 2
"Leystu þetta dæmi, farðu yfir skrefin og sýndu lausn:  
10x = 40"

Success criteria:
- User solves a problem.
- User uses step review.
- User reveals or checks final solution.

### Task 3
"Leystu nýtt dæmi í sömu undirmöppu, gerðu eitt skref, biddu um vísbendingu og kláraðu dæmið:  
x/4 + 2 = 5"

Success criteria:
- New problem is in same subfolder.
- User requests a hint after first step.
- User completes problem flow.

### Task 4 (Seeded Error Task)
"Leystu dæmið áfram frá þessum upphafsreikningi (viljandi villa):  
Dæmi: 3x + 4 = 19  
Byrja á: 3x = 19 + 4  
Biddu um vísbendingu fyrir næsta skref og haltu áfram þar til dæmið er leyst."

Success criteria:
- User continues from provided wrong step.
- User requests hint.
- User recovers and completes flow (or clearly attempts recovery).

### Task 5
"Skoðaðu villuna þína í villubanka."

Success criteria:
- User finds error bank.
- User identifies the recent error entry.

### Task 6
"Búðu til skil með þessum 3 dæmum, skýrðu skilin og exportaðu."

Success criteria:
- User selects the 3 problems.
- User generates export (PDF).
- User explains what the export contains.

## 6.1 Standardized Problems (Use For Every Participant)
Use exactly these equations in all sessions:
1. `10x = 40`
2. `x/4 + 2 = 5`
3. `3x + 4 = 19` with seeded wrong start `3x = 19 + 4`

Facilitator-only answer key:
- Problem 1: `x = 4`
- Problem 2: `x = 12`
- Problem 3: `x = 5`

## 7. Intervention Rule
- If user is stuck under 60 seconds: stay silent and observe.
- If user is stuck over 60 seconds: give one neutral hint and note intervention.
- Never tell exact click sequence unless session is ending.

## 8. Debrief Questions
Ask all 5:
1. What was the most confusing part?
2. Was there a point where you were not sure what to do next?
3. How did you feel about AI responses and hints?
4. Did response times feel acceptable?
5. What would you change first?

## 9. SUS Questionnaire
Use `SUS_FORM.md` right after debrief.

## 10. What To Capture Per Session
- Task completion: yes/no per task.
- Time on task per task (seconds).
- Number of interventions.
- Unexpected actions (what user tried and why).
- Latency perception rating (1 to 5) at least once after AI wait.
- Any crashes, dead ends, or backend errors.
- 1 to 3 key quotes from participant.

## 11. After Each Session (5-Minute Wrap-Up)
Complete immediately:
1. Fill `SESSION_NOTES_TEMPLATE.md`.
2. Append rows to `findings_log_template.csv` (or copy into your final findings file).
3. Append SUS responses to `sus_responses_template.csv`.
4. Write top 3 findings while memory is fresh.

## 12. Report-Ready Output You Need
For final report section on user testing:
- Method summary: who, how many, tasks, session structure.
- Findings table: frequency + severity + evidence + action taken.
- Interaction data examples from logs/traces.
- SUS mean/median and short interpretation.
- Product changes made due to testing.
