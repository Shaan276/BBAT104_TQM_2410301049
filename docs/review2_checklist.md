# Review 2 Self-Assessment & Compliance Checklist
## Online Quiz System — [Q05: Reduce Response Time]

**Course**: BBAT104: Fundamentals of Total Quality Management (TQM)  
**Academic Session**: 2026–27  
**Student Name**: Piyush Pilkhwal  
**University Roll Number**: 2410301049  
**Branch & Section**: Computer Science & Engineering (CSE) — Section A  
**Assigned Quality Goal**: Q05 — Reduce Response Time  
**Mapped Course Outcomes**: CO1 & CO2 (15 Raw Marks)  

---

## 1. Compliance Audit Against Master Guidelines (Table 3 & Table 4)

| Milestone 2 Evaluation Criterion | Guidelines Requirement | Target Implementation / Artefact | Status | Self-Score (out of 15) |
| :--- | :--- | :--- | :---: | :---: |
| **1. Base System CRUD Operations** | Fully functional CRUD for baseline topic (Online Quiz System) connected to SQLite database. | [`src/database/schema.sql`](../src/database/schema.sql)<br>[`src/modules/quiz_crud.py`](../src/modules/quiz_crud.py)<br>[`src/ui/crud_view.py`](../src/ui/crud_view.py) | **COMPLIANT** | 7.5 / 7.5 |
| **2. Integration of 5 Quality Goal Features** | Execution and demonstration of 5 assigned Q05 features (Fast Search, Quick Navigation, Cached Dashboard, DB Indexing, Paginated Reports). | [`src/modules/fast_search.py`](../src/modules/fast_search.py)<br>[`src/modules/cache_manager.py`](../src/modules/cache_manager.py)<br>[`src/modules/paginator.py`](../src/modules/paginator.py)<br>[`src/database/indexes.sql`](../src/database/indexes.sql) | **COMPLIANT** | 7.5 / 7.5 |

**Total Estimated Review 2 Score**: **15 / 15 Raw Marks (100% — Excellent Rubric Tier)**

---

## 2. Rubric Alignment (Table 4: System Architecture & Base CRUD)

- **Rubric Tier**: **Excellent (80% - 100%)**
- **Descriptor**: *"All CRUD modules fully functional; robust architecture with zero breaking errors."*
- **Audit Verification**:
  1. `Quizzes` CRUD: Create, Read, Update, Delete operational with live UI forms.
  2. `Questions` CRUD: Question authoring with options A-D, answer key dropdown, and mark assignments.
  3. `Attempts` CRUD: Zero-latency auto-grading commit with attempt logs and answers audit trail.
  4. Exception Handling & Poka-Yoke: Intercepts non-positive numbers, empty titles, invalid answer options, and double submissions.
  5. 11/11 automated unit tests passing cleanly in `pytest`.
