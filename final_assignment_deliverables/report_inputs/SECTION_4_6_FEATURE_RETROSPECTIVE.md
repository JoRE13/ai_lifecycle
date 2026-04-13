# Section 4.6 - Feature Retrospective (Report Draft)

## Planned Improvement Goals
At the end of Assignment 6, we defined five priorities:
1. Add user-based statistics to the homepage.
2. Add an error bank so users can review recurring mistakes.
3. Reduce latency and improve responsiveness.
4. Generate practice problems based on user error patterns.
5. Implement anonymous data collection to support evaluation and future dataset building.

## What We Implemented

### 1) Personalized Homepage Statistics
We implemented user-focused dashboard statistics, including weekly comparison views and streak/progress indicators. This gives users a clearer sense of learning progress and recent activity trends.

### 2) Error Bank and Error Analytics
We implemented a full error-bank flow:
- structured error extraction from solution checks,
- normalized error categories,
- user-facing error-bank summaries,
- detailed error-event views (including filtering contexts).

This supports reflection and helps users identify repeated mistake patterns.

### 3) Latency and Reliability Improvements
We implemented multiple technical improvements for response robustness:
- better request instrumentation and stage-level observability,
- retry/error-handling improvements,
- safer unclear-input handling and fallback behavior,
- several UI/UX changes that reduce perceived friction during waiting states.

Result: stability and transparency improved, but latency is still a known UX issue from user testing and remains an active optimization area.

### 4) Error-Driven Practice Generation
We implemented personal exam/practice generation that targets user weaknesses:
- automatic targeting based on historical error patterns,
- manual targeting mode,
- configurable pack size and feedback mode,
- end-to-end exam session flow (creation, answering, grading, review).

This directly operationalizes the “learn from your own mistakes” objective.

### 5) Anonymous Data Collection Foundation
We implemented backend support for privacy-aware collection:
- anonymous user identifiers,
- consent fields for analytics and dataset usage,
- structured storage for evaluation/dataset workflows,
- analytics event and metadata tracking.

This establishes a usable foundation for internal evaluation datasets and possible future publication workflows.

## Additional Work Shipped Beyond the Original List
- One-level folder/subfolder organization and safer archive/delete behavior.
- Major Icelandic UI localization and consistency pass.
- Unclear handwriting confirmation flow (`confirm_reading`) to prevent silent misgrading.
- Improved PDF export flow and document quality.
- iOS writing/canvas usability improvements (fullscreen behavior, persistence, interaction fixes).
- Profile and onboarding improvements (name capture, avatar clarity).

## Outcome Summary
The original Assignment 6 goals were largely achieved:
- Fully achieved: goals 1, 2, and 4.
- Achieved with backend foundation in place: goal 5.
- Improved but still ongoing: goal 3 (latency).

Overall, the project moved from a functional prototype to a substantially more robust and user-ready learning workflow with stronger personalization, clearer error feedback, and improved evaluation readiness.

## Remaining Focus (Next Iteration)
1. Continue latency optimization and stronger degraded-mode fallbacks.
2. Expose privacy/consent controls more explicitly in the iOS UI.
3. Expand difficulty adaptation and targeting quality in generated practice packs.
