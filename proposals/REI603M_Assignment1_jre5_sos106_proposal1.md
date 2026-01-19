# REI603M - Assignment 1 - Proposal 1

## Project: AI Math Coach for Secondary School (Framhaldsskóli)

**Group:** Sölvi Santos (sos106), Jóhannes Reykdal Einarsson (jre5), Sævar Breki Snorrason (sbs87)

---

## Project Overview

### Solution definition

We will build a mobile-first web app (PWA) that helps secondary school students solve homework in algebra, functions and other fields using photo input. The product is designed for the reality that many students either get stuck on their homework or make AI do it for them entirely. Most students do their homework by hand, either on paper or tablets, and almost everyone has a smartphone today's age. The app therefore treats the camera as the primary input channel and is structured around two distinct captures. First, the student photographs the problem statement itself. Second, the student photographs their handwritten work (one or more pages). Separating problem capture from work capture reduces ambiguity, improves usability on mobile, and enables the system to compare the student's steps against the original task rather than guessing what is being solved.

The tutoring interaction is centered on learning support rather than answer delivery. By default the system operates in what we call Hint Mode. Hint Mode provides a Socratic prompt followed by exactly one actionable next step and a short justification of why that step is valid. We don't want our app to become an answer generator and that is why we went with this "one at a time" constraint, along with keeping the student in control of the process. When students are worried they made a small mistake, they can use "Check my last step" which verifies a selected step (defaulting to the most recent one), identifies the error type if the step is invalid, proposes a corrected line, and provides a micro-hint about what to do next. If the student decides they want a full worked solution, they must explicitly press a Reveal Solution button. Only then does the app produce a complete derivation and the final answer. This explicit separation is part of the integrity policy by designing the UI in a way which makes it clear what kind of help the student is requesting.

There are some non-essential features which we will try to implement. First, the app will support topic tagging so the system can adopt a slightly different tutoring style and vocabulary depending on context. Second, it will support export to PDF so students can keep a record of the problem, their work, and the tutoring thread without requiring accounts or long-term storage.

### Target users

The primary users are upper secondary students doing homework at home. We explicitly optimize for two common failure modes. The first is stuckness: students understand the general topic but cannot identify the next valid step, which causes them to stall and lose momentum. The second is careless errors: even when the student knows the method, a sign error, distribution slip, or arithmetic mistake breaks the chain of reasoning and makes the rest of the work look "wrong," often leading to frustration and giving up. The product is designed to reduce time-to-progress for stuck students and to shorten the feedback loop for typical small mistakes.

### User journey

A typical session begins when the student opens the app and starts a new problem. They photograph the problem statement and confirm a crop. The app returns a readable extracted representation of the problem (shown as editable text/LaTeX-style math), because in a photo-driven workflow recognition errors are unavoidable and must be easy to fix. Next the student photographs their work. The app extracts the steps into a numbered list and again allows edits, enabling the student to correct misread symbols (for example, confusing "−" with "+" or "x" with "×") without restarting. The main tutoring view shows three things together: the original problem, the extracted steps, and a hint thread. The student can request the next hint, ask the system to check a specific line, or reveal the full solution. If the student proposes a final answer, the system is allowed to confirm whether it matches the expected result, but it does not reveal the correct answer in Hint Mode. At the end, the student can export a PDF with the problem image, the work images, the extracted steps, and the tutoring thread.

### Motivation and market context

Students already have access to LLMs, forums, and solution websites, but those tools tend you just give students the answer, prohibiting actually learning, when a student rather only needs a targeted nudge. Many tools either require typed math (difficult on mobile) or produce full solutions immediately. The differentiator here is a step-aware coaching experience that uses the student's own handwritten work as the object of feedback, not just the problem statement. By grounding the interaction in the student's intermediate steps, the app can do two valuable things: it can point to exactly where a mistake likely occurred, and it can propose the smallest next valid step rather than jumping ahead.

This positioning also supports realistic iteration. The core value can be demonstrated with a relatively small topic scope and a small benchmark set, while leaving a clear path to later expansion into more complex topics, and later a roadmap to Icelandic-language tutoring and Icelandic curriculum alignment.

### Course fit

This project is a strong match for an AI lifecycle and operations course because the main technical challenge is not training a model but integrating and operating AI components reliably in a user-facing system. The app must handle image capture and compression, the backend must orchestrate AI calls and enforce policy boundaries, and the team must monitor latency, cost, and failure modes. The system also requires continuous evaluation practices that look like real AI operations: regression tests for "no-answer leakage" in Hint Mode, benchmark-driven quality tracking for error detection and next-step hints, and observability around OCR/vision failures. The project therefore naturally touches deployment, monitoring, maintenance, and iteration loops that are central to the AI lifecycle.

---

## Data Requirements

### Input data

The system consumes two main input categories: images and optional text. The image inputs are (1) a photo of the problem statement and (2) one or more photos of the student's handwritten work. The system should support common phone-camera variability, including rotation, different lighting, and multi-page work. The optional text inputs include a short "what I tried / where I'm stuck" note and user edits to the extracted math. The purpose of editable extraction is practical: if the system misreads a symbol, the user can correct it once and continue, rather than repeatedly fighting recognition errors.

We also capture lightweight session settings that directly affect behavior: selected topic tag, interaction mode (Hint, Check Step, Reveal), and language choice (English-first, with a planned Icelandic roadmap). We do not require identity data because the will not have accounts, for the time being.

### Output format

The primary output is an on-screen tutoring response rendered in the UI. In Hint Mode, the system outputs a short Socratic prompt followed by one concrete next-step transformation and a brief explanation. In Check Step mode, the system outputs a validity judgment for a chosen line, an error-type label when invalid (e.g., sign error, distribution error, arithmetic slip), a corrected line, and a micro-hint. In Reveal mode, the system outputs a full step-by-step solution that ends with the final answer, optionally including a short "common mistakes" note tied to the student's observed error pattern. The system also produces a PDF export containing the problem image, work image(s), extracted text/steps (as corrected by the user), and the tutoring thread.

### Data collection strategy

We do not plan to train new models. Instead, we will create evaluation data and collect minimal feedback signals. The evaluation dataset will include 50–100 representative secondary school math problems, each paired with multiple "student work traces." These traces will include both correct partial work (stuck states) and realistic incorrect steps. For end-to-end testing, we can handwrite traces and photograph them to capture real camera and handwriting variation. For ongoing quality checks, the app can record anonymous signals such as "hint helped / didn't help," "step check was correct / incorrect," and "extraction incorrect." These signals are used to monitor product quality over time and to guide prompt/policy iteration.

### Privacy considerations

Because photos can contain names, handwriting, and incidental background, the default app policy is to avoid long-term retention. Session state is short-lived and expires automatically. Operational logging stores only aggregate metrics needed for operations (latency, error categories, feature usage) and avoids raw images and full extracted problem text.

---

## Technical Architecture

### AI components

The core AI capability is a tutor model that can reason over the problem and the student's intermediate steps and return structured outputs that the UI can render reliably. The primary plan is to use a multimodal model (Open AI GPT-4/5) that can accept the problem photo and work photo(s) directly and return a schema-constrained JSON response. This reduces pipeline complexity and aligns with the course emphasis on multimodal systems. As an implementation variant, we may introduce a specialized math OCR stage that converts images into a structured text/LaTeX representation and segmented steps before calling the tutor model. The OCR-first variant can improve editability and determinism because the UI can display extracted steps as text, allow user correction, and then base tutoring on the corrected representation.

### System design and flow

The app sends the problem image and work images to a backend orchestrator. The backend performs basic validation and normalization (file type, size limits, compression) and then executes one of two flows: (a) multimodal tutoring directly, or (b) OCR extraction followed by tutoring. The backend always enforces the tutoring policy, including Hint vs Reveal separation and answer-confirmation rules. It requests a schema-based response and validates that response before returning it to the client. The client renders the hint thread, highlights a suspected error line when applicable, and exposes the three main actions: Next Hint, Check Step, Reveal Solution. Export to PDF is generated server-side from the session state to ensure consistent formatting across devices.

### Integration and services

Front end: a mobile-first PWA (e.g., React-based). Backend: a small API service responsible for orchestration, policy enforcement, schema validation, and PDF export. Session state is anonymous and stored short-term (in-memory or TTL cache), containing only what is needed to maintain continuity: extracted problem, extracted steps, user edits, and the tutoring thread. Observability includes request tracing across stages (upload -> extraction -> tutoring -> render), cost tracking per session, and quality telemetry based on user feedback signals. Security controls include HTTPS, strict input validation, rate limiting, and careful handling of any debug mode that might temporarily store images.

### Scaling considerations

Likely bottlenecks include image upload bandwidth, concurrent AI calls during peak homework hours, and cost growth as sessions become longer or images become larger. Mitigations include client-side compression, strict image resolution limits, queueing and rate limiting on the backend, and context compaction (keeping only the minimum necessary steps and thread content for the next response). Because the backend is largely stateless beyond short-lived session state, it can scale horizontally with standard cloud practices.

---

## Ethical Considerations

### Privacy

This system processes homework photos that may include identifiers. The design therefore follows a privacy-minimization approach: no accounts, no default history, and short-lived session state with automatic expiry. The UI encourages cropping and user review before upload, reducing accidental capture of unrelated personal information. Operational logging is designed to exclude raw images and full problem content, focusing on aggregate metrics needed for monitoring. If a future version introduces history or personalization, it should require explicit opt-in, clear retention settings, and a way for users to delete stored content.

### Fairness and bias

Performance may vary across handwriting styles, camera quality, and language proficiency. To reduce systematic disadvantage for users with messier handwriting or lower-end cameras, the system will (1) allow users to edit extracted text/steps, (2) include varied handwriting and photo conditions in the evaluation benchmark, and (3) provide graceful failure messaging when extraction confidence is low (e.g., asking for a clearer photo or a crop). The intial design is English-first, which may create accessibility gaps for Icelandic-first students; therefore a roadmap to Icelandic localization (UI strings, tutoring output language, and Icelandic math phrasing) is part of the project plan, with dedicated evaluation cases added once the English pipeline is stable.

### Transparency

The app will clearly disclose that responses are AI-generated and may be imperfect. It will show the extracted problem and steps so the student can see what the system is using as input and correct it when needed. The system will also communicate what it can and cannot do (for example, limitations with unclear handwriting or ambiguous steps) and encourage verification practices such as substitution checks or checking equivalence between consecutive transformations.

### Social impact and academic integrity

The positive impact is reduced frustration, faster recovery from small mistakes, and more consistent access to tutoring-like feedback outside school hours. The primary negative risk is misuse for shortcutting. The design mitigates this through a strict Hint Mode policy (one step at a time, no final answer revealed) and an explicit Reveal Solution action that makes intent clear. The system is allowed to confirm a student-proposed final answer without revealing the correct one, supporting self-checking while limiting "answer harvesting." A secondary risk is overreliance on AI feedback but the Socratic style and step-checking emphasis encourage active reasoning rather than passive copying.
