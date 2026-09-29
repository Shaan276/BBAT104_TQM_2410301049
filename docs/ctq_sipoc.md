# Total Quality Management (TQM) Analysis: CTQ & SIPOC
## Online Quiz System — [Q05: Reduce Response Time]

**Course**: BBAT104: Fundamentals of Total Quality Management (TQM)  
**Academic Session**: 2026–27  
**Student Name**: Piyush Pilkhwal  
**University Roll Number**: 2410301049  
**Branch & Section**: Computer Science & Engineering (CSE) — Section A  
**Assigned Quality Goal**: Q05 — Reduce Response Time  
**Mapped Course Outcome**: CO1 (TQM Foundations & Process Mapping)  

---

## 1. TQM Philosophical Alignment

The development of the **Online Quiz System [Q05]** is governed by foundational Total Quality Management (TQM) doctrines:

1. **Deming's 85/15 Rule**: 85% of software performance bottlenecks and candidate frustrations arise from unoptimized system architectures and missing database indexes—not from network anomalies or slow hardware. Fixing the indexing and caching design addresses the root cause directly.
2. **Customer-Centric Quality**: Quality is objectively defined as the satisfaction of test-takers and evaluators. A quiz system that experiences UI stuttering or submission delays fails the fundamental expectation of transparency and academic fairness.
3. **Continuous Improvement (Kaizen)**: Every latency bottleneck is quantitatively measured, benchmarked, and reduced iteratively through empirical performance profiling.
4. **Error Prevention (Poka-Yoke)**: Mistake-proofing logic is embedded into input entry points to ensure zero malformed questions or invalid answer states can enter the database.

---

## 2. Voice of Customer (VoC) to Critical to Quality (CTQ) Translation

### 2.1 Voice of Customer (VoC) Table

| Stakeholder | Raw Feedback (Voice of Customer) | Operational Issue | TQM Translation / Quality Driver |
| :--- | :--- | :--- | :--- |
| **Student** | *"When I click 'Submit Quiz', the app hangs for several seconds. I never know if my answers got saved or if my timer ran out."* | High submission latency and unbuffered database write locks. | **Zero-Latency Submission & Instant Feedback** |
| **Student** | *"Searching through the list of available quizzes takes forever when there are many subjects."* | Full table scan on unindexed text columns. | **Sub-50ms Indexed Fast Search** |
| **Teacher** | *"Loading the dashboard and historical score reports freezes my computer when 500+ students have taken a test."* | Uncached aggregate queries (`COUNT`, `AVG`) running repeatedly on disk. | **In-Memory Cached Metrics & Server-Side Pagination** |
| **Quality Auditor** | *"We have no way to verify if the quiz app meets response time guarantees during peak exam hours."* | Absence of latency telemetry. | **Embedded Millisecond Execution Benchmarking** |

---

## 3. Critical to Quality (CTQ) Tree

The CTQ Tree translates broad stakeholder expectations into specific, measurable, and verifiable engineering metrics for **Quality Goal Q05**:

```
[Need: Seamless, Reliable Online Assessment Experience]
  │
  ├──► [Driver 1: Instantaneous Search & Navigation]
  │       │
  │       ├──► CTQ 1.1: Quiz Catalog Search Latency
  │       │     └── Metric: Elapsed search query time
  │       │     └── Target: < 25 ms | USL: ≤ 40 ms
  │       │
  │       └──► CTQ 1.2: Menu Navigation & Screen Switch Time
  │             └── Metric: UI frame swap duration
  │             └── Target: < 10 ms | USL: ≤ 20 ms
  │
  ├──► [Driver 2: Zero-Latency Quiz Execution & Scoring]
  │       │
  │       ├──► CTQ 2.1: Question Transition Delay
  │       │     └── Metric: Memory fetch time per question
  │       │     └── Target: < 5 ms  | USL: ≤ 15 ms
  │       │
  │       └──► CTQ 2.2: Answer Submission & Auto-Grading Commit
  │             └── Metric: Transaction commit + score compute
  │             └── Target: < 60 ms | USL: ≤ 100 ms
  │
  └──► [Driver 3: High-Efficiency Reporting & Analytics]
          │
          ├──► CTQ 3.1: Dashboard Summary Load Time
          │     └── Metric: Cache read latency
          │     └── Target: < 5 ms  | USL: ≤ 15 ms
          │
          └──► CTQ 3.2: Report Page Chunking Delay
                └── Metric: SQL LIMIT/OFFSET execution time
                └── Target: < 30 ms | USL: ≤ 50 ms
```

*Note*: **USL** = Upper Specification Limit. Any operation exceeding the USL is classified as a quality defect.

---

## 4. SIPOC Process Mapping

The **SIPOC** framework (Suppliers, Inputs, Process, Outputs, Customers) maps the three core operational pipelines of the Online Quiz System.

### 4.1 SIPOC 1: Quiz Creation & Question Bank Authoring

| Suppliers (S) | Inputs (I) | Process (P) | Outputs (O) | Customers (C) |
| :--- | :--- | :--- | :--- | :--- |
| • Teacher<br>• Academic Department | • Question text<br>• 4 options (A-D)<br>• Correct answer key<br>• Duration limit<br>• Pass threshold | 1. Teacher authenticates as Admin.<br>2. Form validates input completeness (Poka-Yoke).<br>3. Relational record committed to `quizzes` table.<br>4. Questions committed to `questions` table.<br>5. B-Tree indexes updated automatically.<br>6. CacheManager invalidates stale quiz cache. | • Validated Quiz Record<br>• Indexed Question Bank<br>• Fresh Quiz ID token | • Students (Test Takers)<br>• Evaluators<br>• Academic Department |

### 4.2 SIPOC 2: Student Quiz Execution & Auto-Grading

| Suppliers (S) | Inputs (I) | Process (P) | Outputs (O) | Customers (C) |
| :--- | :--- | :--- | :--- | :--- |
| • Student<br>• Timer Daemon | • Student credentials<br>• Target Quiz selection<br>• Selected option choices<br>• Submission trigger | 1. Student selects quiz via Fast Search.<br>2. Engine pre-loads questions into memory.<br>3. Countdown timer decrements non-blocking.<br>4. Student marks answers via radio buttons.<br>5. Auto-grader compares choices against key.<br>6. Score & percentage computed instantly.<br>7. Transaction recorded in `attempts` table.<br>8. Latency benchmark timer logged. | • Instant Score Feedback<br>• Percentage & Pass/Fail Status<br>• Atomic Attempt Record in DB<br>• Submission Latency Log | • Student (immediate clarity)<br>• Teachers (grade tracking)<br>• Exam Registrar |

### 4.3 SIPOC 3: Performance Audit & Reporting

| Suppliers (S) | Inputs (I) | Process (P) | Outputs (O) | Customers (C) |
| :--- | :--- | :--- | :--- | :--- |
| • SQLite Database<br>• Memory CacheManager | • Teacher report request<br>• Page number ($N$)<br>• Page size limit (e.g., 10)<br>• Category/Title filter | 1. User opens Reports screen via shortcut `Alt+R`.<br>2. Query checks `CacheManager` for overview stats.<br>3. Detailed table runs `LIMIT :limit OFFSET :offset`.<br>4. Execution timer benchmarks total query latency.<br>5. UI renders chunked rows with page controls. | • Paginated Report Table<br>• Total Cohort Pass Rate<br>• Measured Query Latency Display (ms) | • Teacher / Admin<br>• Institutional Quality Cell<br>• TQM Auditor |

---

## 5. Poka-Yoke (Mistake-Proofing) Control Matrix

To prevent errors before they propagate, the system embeds physical and logical Poka-Yoke mechanisms:

| Defect Potential | Root Mechanism | Poka-Yoke Design in Online Quiz System |
| :--- | :--- | :--- |
| **Empty Question Submission** | Accidental form submission by teacher | Form submit button disables until question text and all 4 options contain non-whitespace text. |
| **Invalid Answer Key** | Selecting an option that does not exist | Radio button selector restricts correct answer key strictly to `["A", "B", "C", "D"]`. |
| **Duplicate Student Submission** | Student double-clicking submit button | On initial click, submit button immediately disables and shows `Processing...` state. |
| **Expired Timer Overrun** | Student stalling on last question | Timer daemon triggers auto-submit event the instant remaining time reaches `00:00`. |
| **Unindexed Table Drift** | Accidental schema alteration | Database initializer script enforces `CREATE INDEX IF NOT EXISTS` upon every startup. |
