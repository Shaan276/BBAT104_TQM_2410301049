# System Architecture & Technical Design
## Online Quiz System — [Q05: Reduce Response Time]

**Course**: BBAT104: Fundamentals of Total Quality Management (TQM)  
**Academic Session**: 2026–27  
**Student Name**: Piyush Pilkhwal  
**University Roll Number**: 2410301049  
**Branch & Section**: Computer Science & Engineering (CSE) — Section A  
**Assigned Quality Goal**: Q05 — Reduce Response Time  
**Mapped Course Outcome**: CO1 (System Architecture & Software Engineering)  

---

## 1. Architectural Overview & Design Philosophy

The **Online Quiz System [Q05]** is designed following a modular, layered architectural pattern engineered specifically to minimize CPU overhead, eradicate unindexed disk I/O, and achieve deterministic response times under $100\text{ ms}$ for all operational workloads.

The design decouples user interaction from relational data storage through three decoupled layers:
1. **Presentation Layer (UI/UX)**: Lightweight Python desktop interface with pre-rendered views and asynchronous event loops for countdown timers.
2. **Business Logic & TQM Optimization Layer (Core Engine)**: Incorporates the In-Memory `CacheManager`, `FastSearch` index scanner, `QuizEngine` auto-grader, and `Paginator` record chunker.
3. **Persistence Layer (Data Tier)**: SQLite3 relational database operating in WAL (Write-Ahead Logging) mode with specialized B-Tree indexing.

---

## 2. High-Level System Architecture Diagram

```mermaid
graph TD
    subgraph UI_Layer["Layer 1: Presentation Layer (UI/UX)"]
        A[Dashboard View] --- B[Quiz Catalog & Search View]
        B --- C[Interactive Quiz Taking Engine]
        C --- D[Paginated Reports & Analytics View]
    end

    subgraph Logic_Layer["Layer 2: Core Logic & Q05 Optimization Engine"]
        E[Quick Navigation Router] --> F[Cache Manager - In-Memory TTL Cache]
        E --> G[Fast Search Engine - Debounced Lookup]
        E --> H[Quiz Execution & Auto-Grader]
        E --> I[Paginated Record Streamer]
    end

    subgraph Data_Layer["Layer 3: Persistence & Database Tier"]
        J[(SQLite3 Database Engine)]
        K["B-Tree Indexes:<br/>• idx_quizzes_category<br/>• idx_questions_quiz_id<br/>• idx_attempts_quiz_student<br/>• idx_attempts_created_at"]
        J --- K
    end

    UI_Layer --> Logic_Layer
    Logic_Layer --> Data_Layer

    F -.->|Cache Hit < 5ms| A
    G -->|Indexed Query < 30ms| K
    H -->|Atomic Commit < 100ms| J
    I -->|LIMIT/OFFSET Chunking < 50ms| K
```

---

## 3. Data Flow Diagram (DFD)

### 3.1 DFD Level 0 — Context Diagram
The Level 0 Context Diagram depicts the high-level boundary of the Online Quiz System, illustrating data flows between the primary external entities (Teachers, Students, Quality Auditor) and the central system process.

```mermaid
graph LR
    Teacher([Teacher / Admin]) -->|Question Bank & Quiz Config| System[Online Quiz System Q05]
    System -->|Quiz Catalog & Instant Reports| Teacher

    Student([Student / Candidate]) -->|Answer Submissions & Responses| System
    System -->|Immediate Scores & Explanations| Student

    System -->|Real-time Latency & SLA Metrics| Auditor([TQM Quality Auditor])
```

### 3.2 DFD Level 1 — Functional Decomposition

```mermaid
flowchart TD
    subgraph Users
        U1[Teacher]
        U2[Student]
    end

    subgraph Processes
        P1["1.0 Authentication & Navigation"]
        P2["2.0 Question & Quiz CRUD Management"]
        P3["3.0 Fast Search & Catalog Lookup"]
        P4["4.0 Quiz Taking & Zero-Latency Grading"]
        P5["5.0 In-Memory Cache Computation"]
        P6["6.0 Paginated Reporting & Latency Audit"]
    end

    subgraph Data_Stores["Data Stores"]
        D1[("D1: Users Store")]
        D2[("D2: Quizzes & Questions Store")]
        D3[("D3: Student Attempts Store")]
        D4[("D4: In-Memory Metric Cache")]
    end

    U1 -->|Manage Questions| P2
    P2 -->|Write/Update| D2
    P2 -->|Invalidate Cache| D4

    U2 -->|Search Quizzes| P3
    P3 -->|Indexed Scan| D2
    P3 -->|Render Search Results| U2

    U2 -->|Submit Answers| P4
    D2 -->|Fetch Questions| P4
    P4 -->|Write Attempt Log| D3
    P4 -->|Invalidate Attempt Cache| D4
    P4 -->|Immediate Score Output| U2

    P5 -->|Read Cached Totals| D4
    D3 -->|Aggregate on Miss| P5
    P5 -->|Update Metrics| D4

    U1 -->|Request Reports| P6
    D3 -->|Fetch Chunked Rows| P6
    P6 -->|Display Paginated Audit| U1
```

---

## 4. Database Schema & Entity-Relationship (ER) Design

The relational model is optimized for minimal join depth and maximum B-Tree search performance.

```mermaid
erDiagram
    USERS ||--o{ ATTEMPTS : "submits"
    QUIZZES ||--|{ QUESTIONS : "contains"
    QUIZZES ||--o{ ATTEMPTS : "has attempts"
    ATTEMPTS ||--|{ ATTEMPT_ANSWERS : "records"

    USERS {
        INTEGER id PK
        TEXT username UK
        TEXT role "ADMIN or STUDENT"
        TEXT created_at
    }

    QUIZZES {
        INTEGER id PK
        TEXT title
        TEXT category
        INTEGER duration_minutes
        INTEGER passing_score
        INTEGER is_active
        TEXT created_at
    }

    QUESTIONS {
        INTEGER id PK
        INTEGER quiz_id FK
        TEXT question_text
        TEXT option_a
        TEXT option_b
        TEXT option_c
        TEXT option_d
        TEXT correct_option "A, B, C, or D"
        INTEGER marks
    }

    ATTEMPTS {
        INTEGER id PK
        INTEGER quiz_id FK
        INTEGER user_id FK
        INTEGER total_questions
        INTEGER correct_answers
        REAL score_percentage
        TEXT status "PASSED or FAILED"
        REAL latency_ms
        TEXT created_at
    }

    ATTEMPT_ANSWERS {
        INTEGER id PK
        INTEGER attempt_id FK
        INTEGER question_id FK
        TEXT selected_option
        INTEGER is_correct
    }
```

### 4.1 Specialized B-Tree Index Definitions (Quality Goal Q05)
To prevent table scans across tables with hundreds or thousands of rows, the following B-Tree index specifications are applied:

```sql
-- 1. Fast category and quiz title search indexing
CREATE INDEX IF NOT EXISTS idx_quizzes_category_title 
ON quizzes (category, title);

-- 2. Instant foreign-key question retrieval by quiz ID
CREATE INDEX IF NOT EXISTS idx_questions_quiz_id 
ON questions (quiz_id);

-- 3. Composite index for candidate attempt verification & reporting
CREATE INDEX IF NOT EXISTS idx_attempts_quiz_user 
ON attempts (quiz_id, user_id);

-- 4. Reverse chronological index for paginated report streaming
CREATE INDEX IF NOT EXISTS idx_attempts_created_at_desc 
ON attempts (created_at DESC);
```

---

## 5. Q05 Latency Elimination Flow (Before vs. After)

### 5.1 Unoptimized Baseline Flow ($350\text{ ms} - 1200\text{ ms}$)
```
User Action ──► Full Table Scan (Disk I/O) ──► Uncached SQL Aggregation ──► Unbounded Full-Row Draw ──► UI Freeze
```

### 5.2 Q05 Optimized Flow ($\le 30\text{ ms}$)
```
User Action ──► In-Memory Cache Check ──► [HIT: Return in 2ms]
                     │ (Miss)
                     ▼
         B-Tree Index Lookup O(log N) ──► Server-Side Paginated Limit ──► Non-blocking Render
```

---

## 6. Poka-Yoke (Mistake-Proofing) System Controls
- **Duplicate Protection**: Candidate quiz launch creates a single atomic session token; double-clicks on the submission button are intercepted and disabled.
- **Timer Bounds Check**: If candidate operating system time drifts, server-side delta duration validation ensures automatic submission before deadline expires.
- **Data Integrity Constraints**: Foreign keys are strictly enforced (`PRAGMA foreign_keys = ON;`), preventing orphan questions or missing attempt metadata.
