# REI603M - Assignment 1 - Proposal 2

## Project: Meeting Notes Summarizer

**Group:** Sölvi Santos (sos106), Jóhannes Reykdal Einarsson (jre5), Sævar Breki Snorrason (sbs87)

---

## Project Overview

### Solution Definition
We are building a meeting notes summarizer, an AI-powered tool designed to automatically record, transcribe, and summarize meetings. The system helps teams keep track of what was discussed, what decisions were made, and what actions need to be taken, without requiring participants to manually take notes. The application allows users to either record meetings directly within the app or upload an existing audio recording. The audio is transcribed using a speech-to-text model, after which a Large Language Model processes the transcript to generate a structured summary. The output includes a concise overview of the meeting, key discussion points, decisions, and clearly defined action items.

### Target Users
The primary users of this solution are teams within companies that rely on meetings for coordination, planning, and decision-making. This includes development teams, project groups, and small to medium-sized organizations where meetings are frequent but documentation is often incomplete or inconsistent. In such environments, meetings are commonly used to define goals, assign responsibilities, and track progress, yet the outcomes are not always clearly documented. The solution is also relevant for university student groups working on long-term projects that require regular meetings over several weeks or months. These groups face similar challenges to professional teams, such as keeping track of decisions and assigned tasks across multiple meetings. By supporting both professional and academic users, the system targets a clearly defined user group with a shared need for structured meeting summaries and reliable follow-up.

### User Journey
A typical user journey begins when the user opens the application and is presented with two primary options: starting a live meeting recording or uploading an existing audio file from a previous meeting. If the user chooses to record a meeting, the application captures the audio locally and streams or stores it temporarily until the meeting ends. If an existing recording is uploaded, the system validates the file format and length before processing. Once the audio input is confirmed, the system sends the audio file to a speech-to-text service, which generates a full transcript of the meeting. This transcript is then passed to a Large Language Model along with a structured prompt designed to extract key information such as the meeting summary, main discussion topics, decisions, and action items.

After processing, the user is presented with a structured meeting summary in the application interface. In addition to viewing the summary, the user can interact with the AI through a chat interface that allows follow-up questions based on the meeting content, such as clarifying decisions or requesting task lists for specific participants. The generated summary is then stored within a shared group or team workspace, where it is associated with the specific meeting and made accessible to all relevant team members. This allows users to easily revisit past meetings, track progress across multiple sessions, and maintain consistent documentation over time.

### Motivation and Market Context
Many people struggle to keep track of meeting content. Existing approaches usually involve either re-listening to full recordings, which is time-consuming, or attempting to take detailed notes during the meeting, which can reduce participation and focus. This project aims to automate that process by combining speech-to-text technology with LLM-based summarization, enabling participants to engage fully in the discussion while still retaining accurate documentation. The solution does not attempt to replace meetings or human judgment but instead acts as a support tool that improves clarity, accountability and productivity. By automatically organizing information discussed during meetings, the system reduces cognitive load and improves follow-up.

### Course Fit
This project is well-suited for a course focused on AI lifecycle and operations. It relies on existing, production-ready AI models rather than custom model training, allowing the focus to remain on system integration, prompt design, deployment, and operational considerations. The technical feasibility is high, as modern LLMs and speech-to-text systems already perform well on this type of task. The project scope is realistic and achievable within the constraints of the course.

---

## Data Requirements

### Input Data
The primary input data for the system is audio data provided directly by users. This includes live audio recordings captured through the application as well as uploaded audio files from previously recorded meetings. The audio data represents spoken conversation between multiple participants and may vary in length, quality, and speaking style. In addition to audio data, the system generates intermediate text data in the form of transcripts produced by a speech-to-text model. These transcripts are used internally as input to the Large Language Model for summarization and information extraction.

### Output Format
The system produces structured text-based meeting summaries. The output includes a concise summary of the meeting, key discussion topics, decisions, and action items. The results are presented directly within the application interface and stored as text associated with a specific meeting and team workspace. Optionally, summaries may be exported in formats such as plain text or Markdown for external use.

### Data Collection Strategy
This project does not require custom model training. All AI components are used in an inference-only manner through existing APIs. As a result, no large training datasets are required. For development and evaluation purposes, non-sensitive and publicly available audio content may be used to test transcription and summarization quality. These datasets are used solely for testing system behavior, prompt design, and output structure. No user-provided data is reused for training. If retrieval-augmented generation (RAG) is introduced, stored meeting summaries and transcripts within a team workspace may be indexed to allow querying past meetings. This data remains scoped to each user group and is not shared across teams.

### Privacy Considerations
Meeting audio and transcripts may contain highly sensitive information, including personal data and confidential business discussions. Privacy is therefore a core concern of the system design. All user data is processed only for the purpose of generating meeting summaries and is not retained longer than necessary. Audio files and transcripts are stored only when required for user access and collaboration and are scoped to specific team workspaces. All communication with external AI APIs is performed over encrypted connections. Users are informed that third-party AI services are used for transcription and summarization, and clear limitations on data usage are communicated. The system avoids using any user data for training or external evaluation and follows data minimization principles wherever possible.

---

## Technical Architecture

### AI Components
The system uses two off-the-shelf AI components via APIs. For transcription, we use OpenAI Whisper (speech-to-text), which is well-suited for converting meeting audio into a readable transcript across different speaking styles and audio quality. For summarization and structured extraction, we use GPT-4 (or GPT-4o) to generate a topic-based summary, decisions, and action items from the transcript. These models are suitable because they are production-ready, require no training, and integrate cleanly through stable APIs.

### System Design
Users provide audio either by recording inside the application or uploading an audio file. The backend receives the audio and stores it temporarily in object storage (or local storage during development). A background job is then triggered to process the audio. Transcription step is when the backend sends the audio to Whisper and receives a transcript (text). Next the summarization step, thats when the transcript is sent to GPT-4 with a structured prompt that requests specific output fields (summary, topics, decisions, action items). And last but not least the storage and delivery. The resulting structured output is stored and returned to the user in the UI. The summary is also saved to a team “workspace” so all members can access the notes for each meeting. Optionally, the application exposes a chat interface where users can ask questions about a specific meeting. In that case, the stored transcript/summary is provided as context to the LLM so answers stay grounded in the meeting content.

### Integration
The system wil use components like backend API, a simple REST API (e.g., FastAPI or Node/Express) handles uploads, authentication, and retrieval of meeting summaries. Database, a relational database (e.g., PostgreSQL) stores users, teams/workspaces, meeting metadata, and generated summaries. File storage, object storage (e.g., S3-compatible) is used for audio files if long-term access is needed; otherwise files are deleted after processing. Frontend, a minimal web app (React or similar) provides recording/upload, status tracking (processing/completed), and summary viewing.

### Scaling Considerations
The main bottlenecks are external API rate limits, latency for long audio files, and cost per request. If usage grows, the system must handle concurrent processing using a job queue and worker processes. Additional limits such as maximum meeting length, file size validation, and per-team rate limits reduce overload. Database growth is primarily driven by stored transcripts/summaries, retention policies and optional transcript storage can control long-term storage costs.

---

## Ethical Considerations

### Privacy
The system processes potentially sensitive information, including private conversations and confidential company discussions. To minimize risk, the system follows data minimization principles. Audio files are processed only for transcription and are not stored by default after processing is complete. Users may optionally choose to retain audio files, but this is explicitly controlled by user settings. The primary data stored long-term consists of generated meeting summaries and associated metadata, which are saved within secure, access-controlled team workspaces. All data is stored in a secured database, and communication with external AI services is performed over encrypted connections. Clear data retention policies define how long summaries are stored, and users are informed about how their data is processed and handled.

### Fairness and Bias
Although the system does not generate original opinions, it can still produce biased or incomplete outputs through summarization. Bias may appear in the form of omitted viewpoints, overemphasis on certain speakers, or incorrect interpretation of decisions or responsibilities. To mitigate this, the system avoids making assumptions that are not explicitly stated in the transcript and focuses on extracting factual content. Evaluation during development includes testing summaries across different speaking styles, meeting formats, and group dynamics to identify systematic omissions or distortions. The system is positioned as an assistive tool rather than a source of authoritative truth.

### Transparency
Users are clearly informed that the meeting summaries are generated using AI-based transcription and summarization. The interface communicates that outputs may contain errors, omissions, or misinterpretations, particularly in cases of unclear audio or overlapping speech. Limitations such as maximum file size, supported audio formats, and processing constraints are disclosed upfront. This transparency ensures users understand both the capabilities and limitations of the system.

### Social Impact
The system has several potential positive impacts, including improved meeting engagement, better documentation, and increased accountability within teams. By reducing the need for manual note-taking, participants can focus more fully on discussions and decision-making. Potential negative effects include over-reliance on automated summaries and reduced personal responsibility for remembering or documenting meeting outcomes. To address this, the system is designed to support—not replace—human judgment, encouraging users to review and validate summaries rather than treating them as definitive records.
