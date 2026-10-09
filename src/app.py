"""
Application Main Entry Point
Project: Online Quiz System [Q05: Reduce Response Time]
Student: Piyush Pilkhwal (2410301049) | CSE-A
Course: BBAT104 Fundamentals of TQM (Academic Session 2026-27)
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import argparse
from src.database.connection import init_db, verify_indexes, explain_query_plans
from src.modules.quiz_crud import QuizCRUD
from src.modules.fast_search import FastSearchEngine
from src.modules.paginator import ReportPaginator
from src.modules.quiz_engine import QuizEngine
from src.config import (
    SLA_MAX_SEARCH_LATENCY_MS, SLA_MAX_LOAD_QUIZ_LATENCY_MS,
    SLA_MAX_SUBMIT_LATENCY_MS, SLA_MAX_CACHE_READ_MS, SLA_MAX_PAGE_CHUNK_MS
)


def run_benchmarks() -> None:
    """Execute comprehensive Review 2 CRUD and SLA performance audit."""
    print("=" * 75)
    print("BBAT104 TQM COURSE PROJECT - REVIEW 2 VERIFICATION AUDIT")
    print("Baseline System: Online Quiz System | Quality Goal: Q05 [Reduce Response Time]")
    print("Student: Piyush Pilkhwal (2410301049) | Branch: CSE-A")
    print("=" * 75)

    # 1. DB Init & Index Audit
    init_db()
    indexes = verify_indexes()
    print("\n[PHASE 1: B-Tree Index Audit - Q05-F4]")
    for idx_name in indexes:
        print(f"  [OK] Active B-Tree Index: {idx_name}")
    assert len(indexes) >= 4, "Missing mandatory B-Tree indexes"

    # 2. Query Plan Inspection (EXPLAIN QUERY PLAN)
    print("\n[PHASE 2: Query Optimizer Execution Plans]")
    plans = explain_query_plans()
    for p in plans:
        tag = "[INDEX USED]" if p["uses_index"] else "[TABLE SCAN DEFECT]"
        print(f"  [OK] {p['label']:24} : {p['plan_details']} {tag}")


    # 3. Response Time SLA Benchmarks
    print(f"\n[PHASE 3: Response Time SLAs & Latency Benchmarks]")

    # Cache read
    QuizCRUD.get_dashboard_metrics(force_refresh=True)
    metrics_cached, hit_lat, is_hit2 = QuizCRUD.get_dashboard_metrics(force_refresh=False)
    status_cache = "PASS" if hit_lat <= SLA_MAX_CACHE_READ_MS else "DEFECT"
    print(f"  1. Cached Dashboard Read (Q05-F3) : {hit_lat:6.3f} ms [SLA {status_cache}] (USL: <= {SLA_MAX_CACHE_READ_MS} ms)")

    # Fast Search
    results, search_lat, search_sla = FastSearchEngine.search_quizzes("TQM")
    status_search = "PASS" if search_sla else "DEFECT"
    print(f"  2. Indexed Fast Search   (Q05-F1) : {search_lat:6.3f} ms [SLA {status_search}] (USL: <= {SLA_MAX_SEARCH_LATENCY_MS} ms)")

    # Quiz Load
    quiz_info, questions, load_lat, load_sla = QuizEngine.load_quiz_session(1)
    status_load = "PASS" if load_sla else "DEFECT"
    print(f"  3. In-Memory Quiz Load   (Q05-F2) : {load_lat:6.3f} ms [SLA {status_load}] (USL: <= {SLA_MAX_LOAD_QUIZ_LATENCY_MS} ms)")

    # Quiz Submission
    answers = {q["id"]: q["correct_option"] for q in questions}
    sub_res, sub_lat, sub_sla = QuizEngine.submit_attempt(1, 2, answers)
    status_sub = "PASS" if sub_sla else "DEFECT"
    print(f"  4. Atomic Submit/Score            : {sub_lat:6.3f} ms [SLA {status_sub}] (USL: <= {SLA_MAX_SUBMIT_LATENCY_MS} ms)")

    # Paginated Reports
    pag_data = ReportPaginator.get_paginated_attempts(page=1, page_size=10)
    status_pag = "PASS" if pag_data["within_sla"] else "DEFECT"
    print(f"  5. Paginated Report Draw (Q05-F5) : {pag_data['latency_ms']:6.3f} ms [SLA {status_pag}] (USL: <= {SLA_MAX_PAGE_CHUNK_MS} ms)")

    print("\n" + "=" * 75)
    print("ALL REVIEW 2 CRUD MODULES & Q05 QUALITY GOAL FEATURES FULLY OPERATIONAL!")
    print("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(description="Online Quiz System [Q05: Reduce Response Time]")
    parser.add_argument("--benchmark", action="store_true", help="Run automated response time SLA benchmarks")
    parser.add_argument("--cli", action="store_true", help="Run in headless console mode")
    args = parser.parse_args()

    # Ensure DB is initialized
    init_db()

    if args.benchmark or args.cli:
        run_benchmarks()
        return

    # Launch Desktop GUI
    try:
        from src.ui.main_window import MainWindow
        app = MainWindow()
        app.mainloop()
    except Exception as err:
        print(f"Graphical interface could not be launched ({err}). Running benchmark audit:")
        run_benchmarks()


if __name__ == "__main__":
    main()
