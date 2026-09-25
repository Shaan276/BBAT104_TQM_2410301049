# Software Requirements Specification (SRS)
## Online Quiz System — [Q05: Reduce Response Time]

**Course**: BBAT104: Fundamentals of Total Quality Management (TQM)  
**Academic Session**: 2026–27  
**Student Name**: Piyush Pilkhwal  
**University Roll Number**: 2410301049  
**Branch & Section**: Computer Science & Engineering (CSE) — Section A  
**Assigned Baseline System**: Online Quiz System  
**Assigned Quality Goal**: Q05 — Reduce Response Time  
**Mapped Course Outcome**: CO1 (Understand and apply TQM philosophies and baseline software system engineering)  

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document details the functional, non-functional, interface, and performance specifications for the **Online Quiz System**, engineered with a primary focus on **Total Quality Management (TQM) Quality Goal Q05 (Reduce Response Time)**. The goal of this system is to eradicate latency bottlenecks during quiz authoring, question lookup, live candidate test submissions, auto-grading, and historical score report rendering.

### 1.2 Scope of the System
The system is a lightweight, responsive desktop-based assessment platform designed for educational institutions. It facilitates:
1. **Teacher/Administrator Persona**: Rapid question bank management, quiz formulation, test schedule configuration, and instant performance audit viewing.
2. **Student/Candidate Persona**: Frictionless quiz discovery, sub-millisecond question transitions, timer-synchronized test execution, and zero-latency submission with immediate score computation.
3. **TQM Performance Engine (Q05)**: Dedicated B-Tree indexed querying, in-memory metric caching, and paginated record streaming to ensure system response time remains consistently under strict Quality Service Level Agreements (SLAs).

### 1.3 Definitions, Acronyms, and Abbreviations
- **TQM**: Total Quality Management
- **Q05**: Quality Goal 05 — Reduce Response Time
- **SLA**: Service Level Agreement
- **SRS**: Software Requirements Specification
- **CTQ**: Critical to Quality
- **SIPOC**: Suppliers, Inputs, Process, Outputs, Customers
- **CRUD**: Create, Read, Update, Delete
- **Poka-Yoke**: Mistake-Proofing / Error Prevention mechanism
- **B-Tree Index**: Self-balancing tree data structure utilized by SQLite for logarithmic lookup time $O(\log N)$
- **TTL**: Time to Live (Cache expiration duration)

---

## 2. Overall System Description

### 2.1 Product Perspective
In conventional institutional quiz platforms, relational databases suffer severe throughput degradation as question banks and submission histories expand. Table scans cause UI freezing, delayed answer submissions, and report loading timeouts. The **Online Quiz System [Q05]** resolves this systemic failure through architectural TQM intervention:
- Decoupling analytical metric computations from the disk storage layer via a dedicated **Cache Manager**.
- Enforcing **Database Indexing** on all filter and foreign key predicates (`quiz_id`, `category`, `student_id`, `created_at`).
- Implementing **Chunked Paginated Streaming** ($LIMIT / OFFSET$) to eliminate memory-bloat during audit queries.

### 2.2 User Personas & Characteristics

| User Role | Responsibilities | Critical Operational Need |
| :--- | :--- | :--- |
| **Administrator / Teacher** | Create categories, author multiple-choice questions, set time limits, view cohort reports. | Fast search across large question banks; instantaneous student report rendering. |
| **Student / Candidate** | Browse active quizzes, attempt assessments within time limits, submit answers. | Zero submission latency; instantaneous auto-grading feedback; zero UI freeze during question transition. |
| **Quality Auditor** | Monitor query response times, verify SLA compliance, review defect logs. | Real-time latency tracking and empirical performance measurement. |

### 2.3 Operational Environment
- **Operating System**: Windows 10/11, Linux, macOS
- **Language & Runtime**: Python 3.10+
- **Database Engine**: Embedded SQLite3 with WAL (Write-Ahead Logging) and custom indexing
- **GUI Framework**: Python Tkinter / Standard Lightweight Graphical Shell
- **Version Control**: Git / GitHub Desktop

---

## 3. Specific Functional Requirements (Base System & CRUD)

### 3.1 Module 1: Authentication & Role Management (FR-01)
- **FR-01.1**: The system shall provide distinct, lightweight login modes for Administrators (Teachers) and Students.
- **FR-01.2**: User credentials and sessions shall be managed with input sanitization and zero external API latency overhead.

### 3.2 Module 2: Question Bank Management — CRUD (FR-02)
- **FR-02.1 [Create]**: The teacher shall add questions containing question text, 4 options (A, B, C, D), correct option pointer, category tag, and marks weightage.
- **FR-02.2 [Read]**: The system shall display question banks with instant search and category filtering.
- **FR-02.3 [Update]**: Teachers shall modify existing questions, options, or categories with automatic cache invalidation.
- **FR-02.4 [Delete]**: Teachers shall remove deprecated questions with relational cascade verification.

### 3.3 Module 3: Quiz Management & Publishing — CRUD (FR-03)
- **FR-03.1 [Create]**: Teachers shall assemble quizzes by grouping questions, specifying quiz title, category, duration in minutes, and passing score threshold.
- **FR-03.2 [Read]**: Students and teachers shall view active and archived quizzes with search capability.
- **FR-03.3 [Update]**: Teachers shall update quiz metadata, time limits, or active status.
- **FR-03.4 [Delete]**: Teachers shall archive or delete quizzes without breaking historic student attempt logs.

### 3.4 Module 4: Quiz Engine & Zero-Latency Execution (FR-04)
- **FR-04.1**: Students shall launch an active quiz with all questions pre-fetched into memory for instant navigation between questions.
- **FR-04.2**: The system shall maintain an active countdown timer updated every second without blocking UI responsiveness.
- **FR-04.3**: Answers shall be selected via single-click radio buttons with immediate state capture in local memory.
- **FR-04.4**: Upon submission (or timer expiration), the system shall compute score, total marks, percentage, and pass/fail status in a single database transaction under 100 milliseconds.

---

## 4. Specific Quality Goal Requirements (Q05: Reduce Response Time)

As mandated by course allotment **Q05**, the system incorporates 5 specialized architectural features to systematically lower response time:

### 4.1 Feature 1: Fast Search (Q05-F1)
- **Q05-F1.1**: The system shall provide an indexed, search-as-you-type mechanism across quiz titles, categories, and question text.
- **Q05-F1.2**: Search queries shall bypass full table scans by utilizing SQLite B-Tree indexed prefix and exact match routines, returning results in $\le 30\text{ ms}$.

### 4.2 Feature 2: Quick Navigation (Q05-F2)
- **Q05-F2.1**: The user interface shall feature direct keyboard shortcuts (e.g., `Alt+D` for Dashboard, `Alt+Q` for Quizzes, `Alt+R` for Reports, `F5` for Refresh).
- **Q05-F2.2**: The navigation sidebar shall enable instantaneous tab switching with pre-mounted container frames, yielding zero screen-redraw delay.

### 4.3 Feature 3: Cached Dashboard (Q05-F3)
- **Q05-F3.1**: The system shall implement an in-memory `CacheManager` with key-based storage and a 60-second Time-To-Live (TTL).
- **Q05-F3.2**: Aggregated metrics (Total Quizzes, Total Questions, Total Submissions, Average Score, Pass Rate) shall be served directly from memory in $\le 5\text{ ms}$.
- **Q05-F3.3**: The cache shall automatically invalidate when new quizzes are added, updated, or student attempts are finalized.

### 4.4 Feature 4: Database Indexing (Q05-F4)
- **Q05-F4.1**: Explicit B-Tree indexes shall be created on:
  - `idx_quizzes_category` on `quizzes(category)`
  - `idx_questions_quiz_id` on `questions(quiz_id)`
  - `idx_attempts_quiz_student` on `attempts(quiz_id, student_id)`
  - `idx_attempts_created_at` on `attempts(created_at)`
- **Q05-F4.2**: SQLite `EXPLAIN QUERY PLAN` shall confirm `USING INDEX` for all candidate lookup, submission join, and report sorting queries.

### 4.5 Feature 5: Paginated Reports (Q05-F5)
- **Q05-F5.1**: Performance and submission history reports shall enforce server-side pagination with default page size of 10 or 25 records per page.
- **Q05-F5.2**: The report queries shall utilize `LIMIT :limit OFFSET :offset` coupled with indexed timestamp ordering, preventing memory spikes when dataset exceeds thousands of attempt logs.
- **Q05-F5.3**: Each report screen shall display live query execution latency (in milliseconds) to verify Q05 SLA conformance.

---

## 5. Non-Functional Requirements & Performance SLAs

### 5.1 Response Time Service Level Agreements (SLAs)

| Operational Transaction | Baseline / Unoptimized System | Q05 Target SLA (Upper Specification Limit) |
| :--- | :---: | :---: |
| **Catalog Search & Filter** | $250\text{ ms} - 600\text{ ms}$ | $\le \mathbf{40\text{ ms}}$ |
| **Quiz Question Loading** | $300\text{ ms} - 800\text{ ms}$ | $\le \mathbf{50\text{ ms}}$ |
| **Answer Submission & Scoring** | $400\text{ ms} - 1200\text{ ms}$ | $\le \mathbf{100\text{ ms}}$ |
| **Dashboard Metrics Rendering** | $350\text{ ms} - 900\text{ ms}$ | $\le \mathbf{15\text{ ms}}$ *(Cached)* |
| **Paginated Report Page Change** | $500\text{ ms} - 1500\text{ ms}$ | $\le \mathbf{60\text{ ms}}$ |

### 5.2 Reliability & Fault Tolerance
- **NFR-REL-01**: Database operations shall execute with atomic transactions (`ACID`). If a power interruption occurs during quiz submission, uncommitted data rolls back cleanly without database corruption.
- **NFR-REL-02**: The system shall handle missing inputs or unexpected exceptions gracefully with informative user feedback rather than application crashes.

### 5.3 Error Prevention (Poka-Yoke)
- **NFR-POKA-01**: The quiz engine shall prevent duplicate submission of the same quiz attempt by locking submission state upon initial trigger.
- **NFR-POKA-02**: Question entry forms shall validate mandatory fields, verify that correct answer matches one of the provided options, and block negative time durations.

---

## 6. Review 1 Verification & Acceptance Criteria
1. Full traceability from course allotment (Piyush Pilkhwal, 2410301049, Q05) to software specification.
2. Clear definition of the 5 response time reduction features.
3. Quantifiable and measurable response time SLAs established for empirical benchmarking in subsequent reviews.
