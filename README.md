# Online Quiz System — [Q05: Reduce Response Time]
### Course Project: BBAT104 — Fundamentals of Total Quality Management (TQM)

---

## 👨‍🎓 Student & Project Details

| Parameter | Specification |
| :--- | :--- |
| **Student Name** | **Piyush Pilkhwal** |
| **University Roll Number** | **2410301049** |
| **Branch & Section** | Computer Science & Engineering (CSE) — Section A |
| **Academic Course** | BBAT104: Fundamentals of Total Quality Management |
| **Academic Session** | 2026–27 |
| **Allotted Baseline Software** | **Online Quiz System** *(Roll digit 9: "Ensure zero latency during submissions & auto-grading")* |
| **Assigned Quality Goal** | **Q05: Reduce Response Time** |
| **Repository Name** | `BBAT104_TQM_2410301049` |

---

## 🎯 Project Overview & Q05 Mandate

The **Online Quiz System** is an engineering project combining core software engineering principles with rigorous **Total Quality Management (TQM)** practices. 

In real-world assessment software, growing question repositories and student cohorts frequently degrade system responsiveness, causing submission timeouts, UI freezes, and slow report loading. This project resolves these issues by implementing **Quality Goal Q05 (Reduce Response Time)** via five mandatory architectural interventions:

1. **Fast Search**: Indexed, debounced query search across quiz catalogs and question banks ($\le 40\text{ ms}$).
2. **Quick Navigation**: Instant tab switching and designated keyboard shortcuts (`Alt+D`, `Alt+Q`, `Alt+M`, `Alt+R`) with zero redraw latency.
3. **Cached Dashboard**: High-speed in-memory metric caching (TTL = 60s) providing instant aggregated score analytics in $\le 15\text{ ms}$.
4. **Database Indexing**: B-Tree composite indexes on foreign keys, categories, and timestamps to eliminate full table scans.
5. **Paginated Reports**: Server-side `$LIMIT / OFFSET$` streaming of student attempt histories with real-time millisecond latency display ($\le 50\text{ ms}$).

---

## 📊 Milestone Progress Tracking

| Milestone | Deliverable Scope | Max Marks | Status |
| :--- | :--- | :---: | :---: |
| **Review 1** | **Setup, Git Repository Initialization, SRS Document & System Architecture** | **10 Marks** | **COMPLETED** |
| **Review 2** | **Base System CRUD Operations & 5 Quality Goal Features Integration** | **15 Marks** | **COMPLETED** |
| **Review 3** | Risk Analysis, FMEA Matrix & Defect Tracking | 15 Marks | *Upcoming* |
| **Review 4** | Statistical Quality Control (SQC), Pareto Analysis & PDCA Cycle | 15 Marks | *Upcoming* |
| **Final Viva** | Software Live Demonstration & Oral Defense | 10 Marks | *Upcoming* |
| **Documentation** | Continuous GitHub Health, Commit Hygiene & User Manual | 5 Marks | *In Progress* |
| **Total** | **Comprehensive TQM Project Assessment** | **70 Marks** | **On Track** |

---

## 📑 Project Documentation Index

### Review 1 Deliverables (Setup & SRS — CO1)
- 📄 **[Software Requirements Specification (SRS)](docs/srs.md)**: Full IEEE-aligned specification of functional requirements, persona models, and response-time SLAs.
- 🏗️ **[System Architecture & Data Flow Design](docs/system_architecture.md)**: 3-tier architectural flowcharts, Level 0 & Level 1 DFDs, relational ER diagram, and B-Tree index definitions.
- 📐 **[TQM CTQ Tree & SIPOC Process Map](docs/ctq_sipoc.md)**: Critical to Quality flowdown, Voice of Customer (VoC) translation matrix, 3 SIPOC process maps, and Poka-Yoke mistake-proofing controls.
- ✅ **[Review 1 Compliance Audit Checklist](docs/review1_checklist.md)**: Self-evaluation rubric checklist (10/10 Marks).

### Review 2 Deliverables (Base CRUD & Q05 Integration — CO1 & CO2)
- 🛠️ **[Review 2 Technical Report](docs/review2_report.md)**: Full report detailing CRUD module implementation, Q05 feature code, benchmark tables, and `EXPLAIN QUERY PLAN` verification.
- ✅ **[Review 2 Compliance Audit Checklist](docs/review2_checklist.md)**: Self-evaluation rubric checklist (15/15 Marks).

---

## ⚡ Review 2 Empirical SLA Benchmark Audit

Running `python src/app.py --benchmark` executes automated microsecond verification against defined Upper Specification Limits (USL):

```
===========================================================================
BBAT104 TQM COURSE PROJECT - REVIEW 2 VERIFICATION AUDIT
Baseline System: Online Quiz System | Quality Goal: Q05 [Reduce Response Time]
Student: Piyush Pilkhwal (2410301049) | Branch: CSE-A
===========================================================================

[PHASE 1: B-Tree Index Audit - Q05-F4]
  [OK] Active B-Tree Index: idx_attempts_created_at_desc
  [OK] Active B-Tree Index: idx_attempts_quiz_user
  [OK] Active B-Tree Index: idx_questions_quiz_id
  [OK] Active B-Tree Index: idx_quizzes_category_title

[PHASE 2: Query Optimizer Execution Plans]
  [OK] Quiz Category Filter     : SEARCH quizzes USING INDEX idx_quizzes_category_title (category=?) [INDEX USED]
  [OK] Question Bank Lookup     : SEARCH questions USING INDEX idx_questions_quiz_id (quiz_id=?) [INDEX USED]
  [OK] Student Attempt Lookup   : SEARCH attempts USING INDEX idx_attempts_quiz_user (quiz_id=? AND user_id=?) [INDEX USED]
  [OK] Paginated Attempt Feed   : SCAN attempts USING INDEX idx_attempts_created_at_desc [INDEX USED]

[PHASE 3: Response Time SLAs & Latency Benchmarks]
  1. Cached Dashboard Read (Q05-F3) :  0.018 ms [SLA PASS] (USL: <= 15.0 ms)
  2. Indexed Fast Search   (Q05-F1) :  2.394 ms [SLA PASS] (USL: <= 40.0 ms)
  3. In-Memory Quiz Load   (Q05-F2) :  1.917 ms [SLA PASS] (USL: <= 50.0 ms)
  4. Atomic Submit/Score            : 45.092 ms [SLA PASS] (USL: <= 100.0 ms)
  5. Paginated Report Draw (Q05-F5) :  7.536 ms [SLA PASS] (USL: <= 50.0 ms)

===========================================================================
ALL REVIEW 2 CRUD MODULES & Q05 QUALITY GOAL FEATURES FULLY OPERATIONAL!
===========================================================================
```

---

## 🛠️ Technology Stack & Dependencies

- **Programming Language**: Python 3.10+
- **Persistence Layer**: Embedded SQLite3 with B-Tree Indexing & WAL Mode
- **User Interface**: Lightweight Python Desktop UI (Tkinter)
- **Benchmarking Engine**: Python microsecond execution timer (`time.perf_counter`)
- **Version Control**: Git / GitHub Desktop

---

## 🚀 Quick Start & Execution

1. **Launch Interactive Desktop Application**:
   ```bash
   python src/app.py
   ```
2. **Run Automated SLA Performance Benchmarks**:
   ```bash
   python src/app.py --benchmark
   ```
3. **Run Unit & Performance Test Suite**:
   ```bash
   pytest -v
   ```

---

## 📂 Directory Structure

```
BBAT104_TQM_2410301049/
├── .gitignore                      # Git ignore patterns
├── README.md                       # Project overview and milestone tracking
├── requirements.txt                # Project dependencies
├── data/
│   ├── .gitkeep                    # Runtime database directory
│   └── quiz_system.db              # SQLite database (generated at runtime)
├── docs/
│   ├── srs.md                      # Software Requirements Specification (Review 1)
│   ├── system_architecture.md      # System architecture, DFDs, ER model (Review 1)
│   ├── ctq_sipoc.md                # CTQ Tree, SIPOC maps, and Poka-Yoke matrix (Review 1)
│   ├── review1_checklist.md        # Review 1 compliance rubric audit (10 Marks)
│   ├── review2_report.md           # Review 2 technical report & CRUD evidence (15 Marks)
│   └── review2_checklist.md        # Review 2 compliance rubric audit (15 Marks)
├── src/
│   ├── __init__.py
│   ├── app.py                      # Main entry point & SLA benchmark runner
│   ├── config.py                   # Centralized configuration & SLA constants
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py           # SQLite connection manager & WAL enabler
│   │   ├── schema.sql              # Relational schema definition
│   │   └── indexes.sql             # B-Tree index definitions (Q05-F4)
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── auth.py                 # User authentication & role management
│   │   ├── quiz_crud.py            # Question bank & quiz CRUD operations
│   │   ├── quiz_engine.py          # Zero-latency test taking & auto-grading
│   │   ├── fast_search.py          # Indexed debounced catalog search (Q05-F1)
│   │   ├── cache_manager.py        # In-memory TTL dashboard cache (Q05-F3)
│   │   └── paginator.py            # Server-side report streaming (Q05-F5)
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py          # Window frame & keyboard navigation router (Q05-F2)
│       ├── dashboard_view.py       # Cached metrics summary display
│       ├── quiz_view.py            # Active assessment layout & live countdown
│       ├── crud_view.py            # Question bank & quiz CRUD management interface
│       └── reports_view.py         # Paginated historical score reports
└── tests/
    ├── __init__.py
    ├── test_crud.py                # CRUD unit tests & indexing verification
    └── test_performance.py         # SLA response-time benchmark tests
```
