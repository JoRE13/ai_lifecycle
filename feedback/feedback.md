# Feedback Summary

## Assignment 2

- Define how answer leakage will be measured and monitored in production, including metrics, thresholds, logging, and manual review.
  - ?
- Consider using agentic vision features to label specific parts of a student's work directly on the image when giving feedback.
  - testing
- Build mistake analysis reporting over time so progress trends can be shown clearly, including for parents.
  - Not sure this is appropriate
- Clarify the parent-facing value proposition with concrete outcomes rather than abstract "learning-focused tutoring" messaging.
- Revisit the 4-second hint latency target and consider background processing plus cached hints.

- Add a parent-facing progress view so parents can see usage and improvement.
  - Streamlit dashboard personalised for users
- Convert handwriting to LaTeX and let the user confirm it before feedback to catch recognition errors early.
  - Don't think its good UX for user to have to proofread entire solution always
- Run a confidence calibration study so "uncertain" thresholds are based on evidence.

## Assignment 3

- Move beyond heuristic qualitative evaluation by trying an LLM-as-judge approach for pedagogical quality.
- Add confidence calibration instructions so the model can admit uncertainty instead of forcing a wrong verdict.
- Keep the structured model contract pattern in production since schema enforcement improves reliability and evaluation.
- Expand evaluation dimensions to include mathematical accuracy, pedagogical appropriateness, Icelandic quality, and tone consistency.
- Analyze performance differences across handwriting authors to see whether accuracy depends on writing style.
- Consider an unstructured-to-structured pipeline where the model reasons freely first and a second step extracts schema fields.
- Evaluate Icelandic output quality systematically for grammar, naturalness, and mathematical terminology.
- Look at external benchmark datasets and handwritten-math datasets as complementary evaluation sources.
- Break down results by problem complexity to understand performance on harder math topics.
- Add a fallback path where users can regenerate with a stronger, more expensive model when needed.
- Shorten the best prompt where possible, since the current version may dilute key instructions.
- Replace prose response-mapping rules with an explicit decision table.
- Add explicit handling for ambiguous handwritten notation.
- Add prompt-level confidence calibration for uncertain mathematical analysis.
- Improve reveal-mode examples so they better show the expected "why" behind each step.

## Assignment 4

- Reduce p95 latency, which is currently too high for interactive tutoring.
- Consider streaming responses so users see partial output earlier.
- Consider a two-stage pipeline: fast OCR or image-to-text first, then text-only reasoning.
- Add progress indicators during longer model runs.
- Replace the single prompt file with a versioned or modular prompt system, or use Langfuse prompt management.
- Improve ambiguity handling so semantically ambiguous but readable notation can still trigger `unclear`.
- Make an explicit product decision about iOS-only native UX versus adding a web fallback.
- Improve prompt organization to make prompt changes easier to manage and test.
- Streamline the UX with a persistent canvas and faster retry flow after feedback.
- Support multi-turn follow-up interactions with prior context.
- Consider voice input for follow-up questions.
- Improve the visual design of the UI, including more polish, transitions, and stronger engagement cues.
- Add canvas-level visual error highlighting tied to the approximate error location.
- Add adaptive difficulty based on student performance.
- Build a curriculum-aligned problem library by topic and difficulty.
- Consider an offline mode for local caching and later sync.
- Add a progress dashboard and light gamification.
- Render LaTeX properly in the UI instead of exposing raw notation.
- Automate batch evaluation so prompt changes are tested against the suite continuously.

## Assignment 6

- Explore models without thought tokens for simpler tasks like hint generation to reduce cost.
- Generate synthetic usage data from team testing so the analytics pipeline can be demonstrated end-to-end without real users.
- Show homepage statistics that personalize by topic performance, recent activity, and suggested next problem type.
- Build an error bank that classifies mistakes into useful review categories.
- Route different operations to different models so hint generation can use a faster or cheaper model than full solution checking.
- For error-based problem generation, return structured fields like `error_type`, `error_step`, and `correct_approach`, then aggregate patterns per user.
- Be careful with anonymous data collection because handwriting is biometrically identifiable; minimize retained identity data and consider synthetic handwriting instead.
- Add a handwriting-confidence indicator that shows the interpreted expression and lets the user correct it before feedback.
- Consider an offline problem bank with local storage and syncing.
- Keep modal and pop-up styling consistent across the UI.
- Strengthen the "What the Data Tells You" section with actual generated session data and concrete insights.
