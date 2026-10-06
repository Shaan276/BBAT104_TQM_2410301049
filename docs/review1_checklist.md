# Review 1 Self-Assessment & Compliance Checklist
## Online Quiz System — [Q05: Reduce Response Time]

**Course**: BBAT104: Fundamentals of Total Quality Management (TQM)  
**Academic Session**: 2026–27  
**Student Name**: Piyush Pilkhwal  
**University Roll Number**: 2410301049  
**Branch & Section**: Computer Science & Engineering (CSE) — Section A  
**Assigned Quality Goal**: Q05 — Reduce Response Time  
**Mapped Course Outcome**: CO1 (10 Raw Marks)  

---

## 1. Compliance Audit Against Master Guidelines (Table 4)

| Evaluation Deliverable | Required Artefact | Target File Location | Status | Self-Score (out of 10) |
| :--- | :--- | :--- | :---: | :---: |
| **1. GitHub Repo Initialization** | Clean public repo structure named `BBAT104_TQM_[RegNo]` with appropriate `.gitignore` and modular folders. | Root directory, `.gitignore`, directory tree | **COMPLIANT** | 2.5 / 2.5 |
| **2. Software Requirements Specification (SRS)** | Complete IEEE-aligned SRS document defining functional, non-functional, and SLA benchmarks for Q05. | [`docs/srs.md`](srs.md) | **COMPLIANT** | 2.5 / 2.5 |
| **3. System Architecture & DFD** | High-level 3-tier architecture flowchart, Level 0 & Level 1 DFDs, ER schema with B-Tree indexes. | [`docs/system_architecture.md`](system_architecture.md) | **COMPLIANT** | 2.5 / 2.5 |
| **4. TQM Process Mapping & Scope** | Critical to Quality (CTQ) Tree, Voice of Customer (VoC) translation, SIPOC process maps, and Poka-Yoke controls. | [`docs/ctq_sipoc.md`](ctq_sipoc.md) | **COMPLIANT** | 2.5 / 2.5 |

**Total Estimated Review 1 Score**: **10 / 10 Raw Marks (100% - Excellent Rubric Tier)**

---

## 2. Review 1 Artefact Inventory

- `docs/srs.md`: 148 lines detailing functional CRUD specs, role requirements, and 5 response-time reduction features.
- `docs/system_architecture.md`: 229 lines containing Mermaid diagrams for 3-tier architecture, Level 0/1 DFD, ER database schema, and latency reduction pipelines.
- `docs/ctq_sipoc.md`: 114 lines covering Deming 85/15 principles, VoC-to-CTQ flowdown, 3 operational SIPOC tables, and Poka-Yoke prevention matrix.
- `src/config.py`: Centralized configuration constants establishing Upper Specification Limits (USL) for all response time metrics.
- `requirements.txt`: Core dependencies and SQC testing tools.
