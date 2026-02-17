# PRD

## Executive Summary

We are building a tablet‑first AI Math   Coach designed to help secondary school students learn algebra by providing step‑aware guidance on their own handwritten work. The product targets students who are motivated to understand the material but frequently get stuck mid‑problem or make small errors that disrupt their reasoning. Unlike existing tools that either give full solutions immediately or require typed math input, this system works directly with students’ natural handwritten workflows and emphasizes learning over answer delivery.

The core experience is a notebook‑style interface where students start problems inside the app, write their solution steps by hand, and request help through clearly defined actions such as requesting a hint, checking a step, or explicitly revealing the full solution. The AI provides Socratic, next‑step guidance and error detection while enforcing strict boundaries to prevent unintended answer leakage.

Technically, the system consists of a tablet‑first web client, a Python‑based backend using FastAPI, a PostgreSQL database for structured problem and session data, and a third‑party multimodal large language model for reasoning and explanation generation. By combining constrained AI interactions with explicit policy enforcement, the product aims to reduce frustration, improve learning outcomes, and provide a buildable, operationally realistic AI tutoring system.

## Problem Statement

Secondary school students learning algebra frequently struggle not because they lack motivation or effort, but because they encounter moments of partial understanding during problem solving. These moments typically arise mid‑problem, when a student is unsure whether a transformation is valid, cannot identify the next logical step, or has made a small mistake—such as a sign error or incorrect distribution—that breaks the chain of reasoning. When this happens, students often stall, lose confidence, and disengage from the task despite being close to a correct solution.

In the absence of timely, targeted feedback, students turn to existing tools such as solution websites, Photomath, or general‑purpose large language models. While these tools are easily accessible, they tend to provide full worked solutions or overly broad explanations that bypass the student’s current line of reasoning. This undermines learning by removing the need for the student to think through the problem themselves. Additionally, many of these tools require typed mathematical input, which does not align with how students naturally work when doing algebra homework by hand on paper or tablets.

As a result, there is a mismatch between students’ needs and the available support. Students do not primarily need answers; they need confirmation, correction, or a small nudge in the right direction that respects the work they have already done. Human tutoring provides this kind of step‑aware guidance, but it is expensive, time‑limited, and not available on demand. Teachers also cannot provide immediate, individualized feedback outside of class time.

The core problem, therefore, is the lack of an accessible, learning‑oriented tool that integrates directly into students’ handwritten workflows and provides targeted, step‑level support without taking over the problem‑solving process. Solving this problem requires a system that understands both the original task and the student’s intermediate work, delivers minimal and intentional guidance, and preserves the student’s agency in reaching the solution.

## Target Users

### Primary Users

The primary users of this product are secondary school students (typically ages 14–18) who are learning algebra and completing homework or exam preparation outside of class. These students usually work by hand, either on paper or on a tablet with a stylus, and are expected to show intermediate steps as part of their learning process. They are generally motivated to understand the material but frequently experience moments of difficulty during problem solving.

What these students care about most is making progress. When they get stuck mid‑problem or suspect they have made a small mistake, they want quick confirmation or guidance that helps them continue without giving away the full solution. They value tools that respect the work they have already done and that help them learn, rather than tools that simply produce answers.

### Current Workflow

When students encounter difficulty today, their typical workflow is fragmented. They write their solution by hand, then switch context to external tools such as Photomath, general‑purpose AI systems, or online solution websites. These tools usually require re‑entering the problem, typing mathematical expressions, or uploading images that are interpreted without reference to the student’s partial work. In many cases, the tools provide complete solutions, which discourages active problem solving and reduces learning value. Students then return to their notebook and copy steps without fully understanding them.

### Explicit Non‑Users

This product is intentionally not designed for all students. In particular:

    If a student’s primary goal is to obtain final answers for homework with minimal effort, this product is not for them.

Students without access to a tablet and stylus, or students unwilling to engage with step‑by‑step reasoning, are also outside the target audience. This deliberate focus allows the product to optimize for learning‑oriented use rather than broad, answer‑centric appeal.

## Feature Requirements (Kano Model)

This section specifies the core functionality of the AI Math Coach, organized using the Kano model to distinguish between baseline expectations, competitive differentiators, and optional delighters. Categorizing features in this way clarifies development priorities and helps ensure that essential functionality is delivered before investing in enhancements.

### Must‑Be Features

Must‑be features are foundational capabilities that users implicitly expect. Their presence does not increase satisfaction, but their absence would make the product unusable or untrustworthy.

- #### Problem Initialization

  The system must allow the user to start a new problem by importing or photographing the problem statement. The system must associate all subsequent work with this problem context.

- #### Handwritten Input Support

  The system must support freehand algebra input using a stylus. Students must be able to write continuously, as they would in a traditional notebook, without being forced to type mathematical expressions.

- #### Step‑by‑Step State Tracking

  The system must track the student’s solution as an ordered sequence of steps. Each step must be associated with the problem and preserved for later validation and review.

- #### Hint Mode

  The system must provide a Hint mode that offers exactly one actionable next step at a time, framed in a Socratic manner. The hint must not reveal the full solution or multiple future steps.

- #### Check Step Functionality

  The system must allow the student to request validation of a specific step. The output must indicate whether the step is valid and, if invalid, identify the error type and propose a corrected version of that step.

- #### Explicit Reveal Solution Mode

  The system must only provide a full worked solution when the student explicitly selects a Reveal Solution action. This separation is essential for maintaining learning‑oriented use.

- #### Interaction Boundaries

  The system must not allow arbitrary free‑text prompting. All AI interactions must be initiated through clearly defined UI actions (Hint, Check Step, Reveal Solution).

- #### Data Persistence
  The system must store problems, steps, and feedback per authenticated user account so that students can revisit previous work.

### Performance Features

Performance features have a direct, linear impact on user satisfaction. Improvements in these areas meaningfully enhance the learning experience and distinguish the product from alternatives.

- #### Hint Quality and Specificity

  Hints should be grounded in the student’s current step and problem context. More precise and context‑aware hints increase perceived intelligence and learning value.

- #### Error Localization and Classification

  When validating a step, the system should accurately identify where the error occurs and classify it (e.g., sign error, distribution error, arithmetic mistake). Better error feedback reduces frustration and accelerates recovery.

- #### Latency

  The system should respond to Hint and Check Step requests in under four seconds. Long delays disrupt cognitive flow and reduce trust in the system.

- #### Handwriting Robustness

  The system should tolerate common variations in student handwriting, including messy notation, uneven spacing, and minor ambiguities. Higher tolerance directly improves usability.

- #### Clarity of Explanations
  Explanations should be concise, readable, and appropriate for secondary school students. Overly verbose or abstract explanations reduce effectiveness.

### Attractive Features

Attractive features are not required for the core product to function, but they can significantly increase engagement and long‑term loyalty once must‑be and performance features are solid.

- #### Support for Additional Math Topics

  Expanding beyond algebra into other high‑school topics (e.g., functions, geometry, calculus) would increase the product’s usefulness but is out of scope for the initial release.

- #### Personalized Feedback Over Time

  The system could adapt its hints based on recurring student mistakes, offering more targeted guidance as it learns from prior interactions.

- #### Multiple Hint Styles

  Allowing students to choose between conceptual hints and procedural hints could improve perceived control and accommodate different learning preferences.

- #### Export and Sharing
  The ability to export problems, handwritten work, and tutoring feedback as a PDF would provide additional value without affecting core functionality.

### Explicit Non‑Features

To preserve the learning‑focused identity of the product, the following capabilities are intentionally excluded:

- Automatic generation of full solutions without explicit user intent

- General‑purpose chatbot functionality

- Solving problems without reference to the student’s own work

- Gamification or competitive features

## Technical Architecture

This section describes the high‑level system architecture of the AI Math Coach, the responsibilities of each component, and how data flows through the system. The architecture is designed to be buildable by a contractor, operationally realistic, and flexible enough to evolve as the project matures.

### High‑Level System Overview

The system is composed of four main parts: a tablet‑first client application, a cloud‑hosted backend API, a relational database, and a third‑party multimodal large language model (LLM). The client handles all user interaction and handwriting capture, while the backend orchestrates AI calls, enforces tutoring policies, and manages persistent state.

### Client Application

The client is a tablet‑optimized progressive web application (PWA) built with React. It provides a notebook‑style interface where students can start problems, write algebra steps using a stylus, and interact with the AI through clearly defined actions (Hint, Check Step, Reveal Solution).

The client is responsible for:

- Capturing handwritten input and problem images

- Rendering extracted mathematical steps and feedback

- Managing user actions and UI state

- Sending images and structured requests to the backend API

No AI reasoning occurs on the client; all intelligence is delegated to backend services.

### Backend API

The backend is implemented using Python and FastAPI. It acts as the central orchestrator of the system and enforces all product constraints.

Key responsibilities include:

- User authentication and session management

- Validating and normalizing image uploads

- Maintaining problem and step state

- Enforcing tutoring policies (e.g. no answer leakage in Hint mode)

- Calling the LLM API with structured prompts

- Validating and sanitizing AI responses before returning them to the client

- FastAPI is chosen for its clear API contracts, built‑in data validation, and suitability for asynchronous AI calls.

### Database

A PostgreSQL database stores all persistent data. This includes user accounts, problems, handwritten steps (in extracted form), and AI feedback. A relational database is used to make relationships between users, problems, and steps explicit and easy to reason about.

The database supports:

- Long‑term problem history per user

- Step‑level feedback tracking

- Future personalization and analytics

### AI and Reasoning Layer

The system uses a third‑party multimodal LLM API to interpret images, reason about algebraic steps, and generate explanations. The LLM is not treated as a free‑form chatbot. Instead, it operates under strict backend‑enforced constraints:

- Inputs are structured and limited to the current problem state

- Outputs must conform to predefined schemas

- The depth and type of feedback depend on the selected interaction mode

This design allows the system to benefit from LLM flexibility while maintaining predictable and learning‑oriented behavior.

### Data Flow Summary

1. The user uploads a problem image or writes a new step.

2. The client sends the input to the backend API.

3. The backend validates the input and updates session state.

4. The backend calls the LLM with policy‑constrained prompts.

5. The LLM returns structured feedback.

6. The backend validates the response and returns it to the client.

7. The client renders the feedback and updates the notebook view.

## Data Model

This section describes the core data entities required by the AI Math Coach and the relationships between them. The data model is designed to support step‑aware tutoring, long‑term problem history, and future personalization while remaining simple enough for a first implementation.

### Core Entities

#### User

Represents an authenticated student using the system.

- id (primary key)

- email

- created_at

- last_login_at

Each user can create and revisit multiple problems over time.

#### Problem

Represents a single math problem session initiated by the user.

- id (primary key)

- user_id (foreign key → User)

- problem_image_url

- created_at

- status (active | completed)

A problem serves as the container for all handwritten steps and AI feedback related to that task.

#### Step

Represents one handwritten solution step entered by the student.

- id (primary key)

- problem_id (foreign key → Problem)

- step_index (ordering within the problem)

- latex_representation

- confidence_score (extraction confidence)

- created_at

Steps are stored as structured LaTeX to allow rendering, validation, and AI reasoning. Users may correct extracted steps if recognition is imperfect.

#### Feedback

Represents an AI response tied to a specific step or problem state.

- id (primary key)

- step_id (foreign key → Step, nullable)

- problem_id (foreign key → Problem)

- mode (hint | check | reveal)

- content

- created_at

Feedback records enable traceability of tutoring interactions and support later review.

#### Session

Represents the user’s active interaction context.

- id (primary key)

- user_id (foreign key → User)

- active_problem_id

- last_active_at

- Sessions allow the backend to maintain continuity across interactions without overloading the client.

### Relationships Summary

- One User → many Problems

- One Problem → many Steps

- One Step → many Feedback entries

- One User → one active Session

This relational structure ensures that all AI feedback is grounded in a specific problem and step context, enabling step‑aware tutoring and long‑term review while remaining extensible for future features such as personalization and analytics.

## API Design

This section describes the core backend API endpoints required to support the AI Math Coach. The API is designed to be consumed by a tablet‑first web client and to provide clear inputs, outputs, and error handling so that a contractor can implement it without additional context. All endpoints are exposed by a FastAPI backend and communicate using JSON over HTTPS.

### `POST /api/auth/login`

Authenticates a user and initializes a session.

#### Input

```
{
  "email": "string",
  "password": "string"
}
```

#### Output

```
{
  "user_id": "string",
  "session_token": "string"
}
```

#### Error Cases

- 401 Unauthorized – invalid credentials

- 500 Internal Server Error – authentication service failure

### `POST /api/problems`

Creates a new problem session.

#### Input

- Multipart form data:
  - problem_image (image file)

#### Output

```
{
  "problem_id": "string",
  "status": "active"
}
```

#### Error Cases

- `400 Bad Request` – missing or invalid image

- `413 Payload Too Large` – image exceeds size limits

- `500 Internal Server Error` – upload or storage failure

### `POST /api/steps`

Uploads a new handwritten step for a problem.

#### Input

```
{
  "problem_id": "string",
  "step_image": "image file"
}
```

#### Output

```
{
  "step_id": "string",
  "latex_representation": "string",
  "confidence_score": 0.0
}
```

#### Error Cases

- `422 Unprocessable Entity` – handwriting could not be reliably interpreted

- `404 Not Found` – problem does not exist

### `POST /api/hint`

Requests the next Socratic hint.

#### Input

```
{
  "problem_id": "string",
  "current_step_id": "string"
}
```

#### Output

```
{
  "hint_text": "string"
}
```

#### Error Cases

- `409 Conflict` – hint request violates tutoring policy

- `500 Internal Server Error` – LLM generation failure

### `POST /api/check-step`

Validates a specific step.

#### Input

```
{
  "step_id": "string"
}
```

#### Output

```
{
  "is_valid": true,
  "error_type": "string | null",
  "corrected_step": "string | null",
  "explanation": "string"
}
```

#### Error Cases

- `422 Unprocessable Entity` – step is ambiguous

- `500 Internal Server Error` – validation failure

### `POST /api/reveal`

Explicitly reveals the full solution.

#### Input

```
{
  "problem_id": "string"
}
```

#### Output

```
{
  "full_solution": ["string"]
}
```

#### Error Cases

- `403 Forbidden` – reveal not allowed in current state

- `500 Internal Server Error` – generation failure

This API design ensures that all AI interactions are policy‑controlled, auditable, and grounded in explicit problem and step context.

## User Flow

This section describes the complete end‑to‑end user journey for the AI Math Coach, from first entry into the product to successful completion of a problem. The flow is written as a textual replacement for wireframes, as required by the assignment, and includes normal operation, error states, and important edge cases.

---

### 1. Entry Point

The user opens the tablet‑first web application and is prompted to log in with their account credentials. If the user is already authenticated, they are taken directly to their dashboard, which shows an option to start a new problem or continue a previous one.

**Success condition:**  
The user is authenticated and reaches the main notebook interface.

---

### 2. Start New Problem

The user selects **“Start New Problem.”**  
They are prompted to upload or photograph the problem statement. After uploading, the system displays a preview and asks the user to confirm or re‑upload if the image is unclear.

**System actions:**

- Validate image format and size
- Create a new problem record
- Store the problem image

**Success condition:**  
The problem is successfully created and associated with the user.

---

### 3. Solving the Problem

The user writes solution steps freehand using a stylus in the notebook interface. Each handwritten step is captured and sent to the backend, where it is interpreted and stored as a structured step.

The notebook view shows:

- The original problem statement
- The list of extracted steps
- Controls for requesting help

**Success condition:**  
Steps are saved and rendered correctly in order.

---

### 4. Requesting Help (Key Interactions)

At any point, the user may choose one of the following actions:

- **Hint:**  
  The system provides a single Socratic hint describing the next valid step.
- **Check Step:**  
  The system validates a selected step and returns correctness feedback.
- **Reveal Solution:**  
  The system explicitly reveals the full worked solution.

The user may repeat Hint or Check Step multiple times as they continue solving.

---

### 5. Completion

The user completes the problem by either:

- Reaching a correct final answer independently, or
- Explicitly selecting **Reveal Solution**

The problem is marked as completed and saved to the user’s history.

**Success condition:**  
The user can review the full problem, steps, and feedback later.

---

### 6. Error States

- **Unreadable problem image:**  
  The system asks the user to upload a clearer photo.
- **Ambiguous handwriting:**  
  The system requests that the user rewrite the step.
- **AI generation failure:**  
  The system shows an error message and allows retry.

---

### 7. Edge Cases

- Multiple valid solution paths
- Skipped or combined steps
- Very messy or inconsistent handwriting

In these cases, the system responds conservatively and may request clarification rather than providing incorrect guidance.

---

This user flow ensures a predictable, learning‑oriented experience while clearly defining system behavior when things go wrong.

## Success Metrics

This section defines how success will be measured for the AI Math Coach. The metrics are designed to be **measurable, specific, and testable**, and to support both pre‑deployment validation and post‑deployment monitoring, as required by the assignment.

### Learning and Task Completion Metrics

- **Problem completion rate:**  
  At least **70% of started problems** are completed (either independently or via explicit Reveal Solution).
- **Hint effectiveness:**  
  In at least **80% of Hint requests**, the student is able to produce a valid next step within two subsequent actions.
- **Error recovery rate:**  
  After a Check Step identifies an error, at least **75% of users** successfully correct the error within two steps.

### System Quality Metrics

- **Latency:**  
  Median response time for Hint and Check Step requests is **under 4 seconds**.
- **Recognition failure rate:**  
  Fewer than **10% of uploaded steps** result in unreadable or ambiguous handwriting errors requiring rewrite.
- **Unintended answer leakage:**  
  Fewer than **5% of Hint or Check Step responses** reveal the full solution or final answer unintentionally.

### Operational Metrics

- **Session stability:**  
  Less than **2% of sessions** terminate due to backend or AI failures.
- **Retry success rate:**  
  Over **90% of failed AI requests** succeed on retry.

These metrics allow the team to verify that the system supports learning, operates reliably, and adheres to its integrity constraints.

---

## Risks and Mitigations

This section outlines the primary technical, product, and ethical risks associated with the AI Math Coach, along with planned mitigation strategies.

### Technical Risks

- **Incorrect step validation or misleading hints**  
  _Risk:_ The AI may confidently produce incorrect feedback.  
  _Mitigation:_ Use conservative language, allow user correction of extracted steps, and prefer asking for clarification over asserting correctness when confidence is low.

- **Poor handwriting recognition**  
  _Risk:_ Messy handwriting could prevent reliable step extraction.  
  _Mitigation:_ Allow users to rewrite steps, expose extracted LaTeX for correction, and provide clear error messages.

- **High latency or cost spikes**  
  _Risk:_ Multimodal AI calls may be slow or expensive.  
  _Mitigation:_ Enforce image size limits, trim context aggressively, and monitor cost per session.

---

### Product and Misuse Risks

- **Use as a shortcut tool for cheating**  
  _Risk:_ Students may rely on Reveal Solution instead of learning.  
  _Mitigation:_ Explicit separation of Hint, Check, and Reveal modes, with Reveal requiring deliberate user intent.

- **Over‑reliance on AI feedback**  
  _Risk:_ Students may defer thinking to the system.  
  _Mitigation:_ Socratic hint design and one‑step‑at‑a‑time guidance.

---

### Privacy and Ethical Risks

- **Sensitive information in uploaded images**  
  _Risk:_ Photos may include names or incidental background data.  
  _Mitigation:_ Encourage cropping, limit stored data to problem‑relevant content, and provide clear deletion options.

By explicitly identifying these risks and mitigations, the project demonstrates realistic planning and responsible AI system design.

---

## Constraints and Out of Scope

### Constraints

- Internet connection required
- Tablet and stylus required
- Algebra‑only scope for initial release
- No custom model training in v1

### Out of Scope

- Offline usage
- Teacher dashboards or classroom management tools
- Full secondary‑school curriculum coverage
- Guaranteed symbolic correctness of all steps
