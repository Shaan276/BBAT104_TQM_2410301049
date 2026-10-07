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

1. **Fast Search**: Indexed, debounced query search across quiz catalogs and question banks.
2. **Quick Navigation**: Instant tab switching and designated keyboard shortcuts (`Alt+D`, `Alt+Q`, `Alt+R`) with zero redraw latency.
3. **Cached Dashboard**: High-speed in-memory metric caching (TTL = 60s) providing instant aggregated score analytics in $\le 15\text{ ms}$.
4. **Database Indexing**: B-Tree composite indexes on foreign keys, categories, and timestamps to eliminate full table scans.
5. **Paginated Reports**: Server-side `$LIMIT / OFFSET$` streaming of student attempt histories with real-time millisecond latency display.

---

## 📊 Milestone Progress Tracking

| Milestone | Deliverable Scope | Max Marks | Status |
| :--- | :--- | :---: | :---: |
| **Review 1** | **Setup, Git Repository Initialization, SRS Document & System Architecture** | **10 Marks** | **COMPLETED** |
| **Review 2** | Base System CRUD Operations & 5 Quality Goal Features Integration | 15 Marks | *Next Milestone* |
| **Review 3** | Risk Analysis, FMEA Matrix & Defect Tracking | 15 Marks | *Upcoming* |
| **Review 4** | Statistical Quality Control (SQC), Pareto Analysis & PDCA Cycle | 15 Marks | *Upcoming* |
| **Final Viva** | Software Live Demonstration & Oral Defense | 10 Marks | *Upcoming* |
| **Documentation** | Continuous GitHub Health, Commit Hygiene & User Manual | 5 Marks | *In Progress* |
| **Total** | **Comprehensive TQM Project Assessment** | **70 Marks** | **On Track** |

---

## 📑 Review 1 Deliverables & Technical Documentation

All Review 1 deliverables are documented in the `docs/` directory:

- 📄 **[Software Requirements Specification (SRS)](docs/srs.md)**: Full IEEE-aligned specification of functional requirements, persona models, and quantifiable response-time Service Level Agreements (SLAs).
- 🏗️ **[System Architecture & Data Flow Design](docs/system_architecture.md)**: 3-tier architectural flowcharts, Level 0 & Level 1 DFDs, relational database ER diagram, and B-Tree index specifications.
- 📐 **[TQM CTQ Tree & SIPOC Process Map](docs/ctq_sipoc.md)**: Critical to Quality flowdown, Voice of Customer (VoC) translation matrix, 3 SIPOC process maps, and Poka-Yoke mistake-proofing controls.
- ✅ **[Review 1 Compliance Audit Checklist](docs/review1_checklist.md)**: Self-evaluation matrix mapped to academic marking rubrics.

---

## 🛠️ Technology Stack & Dependencies

- **Programming Language**: Python 3.10+
- **Persistence Layer**: Embedded SQLite3 with B-Tree Indexing & WAL Mode
- **User Interface**: Lightweight Python Desktop UI (Tkinter)
- **Benchmarking Engine**: Python microsecond execution timer (`time.perf_counter`)
- **Version Control**: Git / GitHub Desktop

---

## 🚀 Directory Structure

```
BBAT104_TQM_2410301049/
├── .gitignore                      # Git ignore patterns
├── README.md                       # Project overview and milestone tracking
├── requirements.txt                # Project dependencies
├── data/
│   ├── .gitkeep                    # Runtime database directory
│   └── quiz_system.db              # SQLite database (generated at runtime)
├── docs/
│   ├── srs.md                      # Software Requirements Specification
│   ├── system_architecture.md      # System architecture, DFDs, ER model
│   ├── ctq_sipoc.md                # CTQ Tree, SIPOC maps, and Poka-Yoke matrix
│   └── review1_checklist.md        # Review 1 compliance rubric audit
├── src/
│   ├── __init__.py
│   ├── app.py                      # Main application entry point (Review 2)
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
│       ├── main_window.py          # Window frame & keyboard navigation (Q05-F2)
│       ├── dashboard_view.py       # Cached metrics summary display
│       ├── quiz_view.py            # Active assessment layout & live countdown
│       └── reports_view.py         # Paginated historical score reports
└── tests/
    ├── __init__.py
    ├── test_crud.py                # CRUD unit tests (Review 2)
    └── test_performance.py         # SLA response-time benchmark tests (Review 2)
```
