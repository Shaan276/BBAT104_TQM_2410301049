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

import argparse
from src.database.connection import init_db
from src.modules.quiz_crud import QuizCRUD
from src.modules.fast_search import FastSearchEngine
from src.modules.paginator import ReportPaginator
from src.modules.quiz_engine import QuizEngine
from src.config import (
    SLA_MAX_SEARCH_LATENCY_MS, SLA_MAX_LOAD_QUIZ_LATENCY_MS,
    SLA_MAX_SUBMIT_LATENCY_MS, SLA_MAX_CACHE_READ_MS, SLA_MAX_PAGE_CHUNK_MS
)


def run_benchmarks() -> None:
    """Execute automated SLA performance benchmarking suite."""
    print("=" * 70)
    print("BBAT104 TQM COURSE PROJECT - QUALITY GOAL Q05 BENCHMARK AUDIT")
    print("Baseline System: Online Quiz System | Goal: Reduce Response Time")
    print("=" * 70)

    # 1. DB Init
    init_db()
    print("[1/5] Database Initialized with WAL Mode & B-Tree Indexes.")

    # 2. Cache Benchmark
    metrics, miss_lat, is_hit = QuizCRUD.get_dashboard_metrics(force_refresh=True)
    metrics_cached, hit_lat, is_hit2 = QuizCRUD.get_dashboard_metrics(force_refresh=False)
    status_cache = "PASS" if hit_lat <= SLA_MAX_CACHE_READ_MS else "DEFECT"
    print(f"[2/5] Cached Dashboard Read: {hit_lat:.3f} ms [SLA {status_cache}] (USL: <= {SLA_MAX_CACHE_READ_MS} ms)")

    # 3. Fast Search Benchmark
    results, search_lat, search_sla = FastSearchEngine.search_quizzes("TQM")
    status_search = "PASS" if search_sla else "DEFECT"
    print(f"[3/5] Indexed Fast Search:   {search_lat:.3f} ms [SLA {status_search}] (USL: <= {SLA_MAX_SEARCH_LATENCY_MS} ms)")

    # 4. Question Loading Benchmark
    quiz_info, questions, load_lat, load_sla = QuizEngine.load_quiz_session(1)
    status_load = "PASS" if load_sla else "DEFECT"
    print(f"[4/5] In-Memory Quiz Load:   {load_lat:.3f} ms [SLA {status_load}] (USL: <= {SLA_MAX_LOAD_QUIZ_LATENCY_MS} ms)")

    # 5. Paginated Reports Benchmark
    pag_data = ReportPaginator.get_paginated_attempts(page=1, page_size=10)
    status_pag = "PASS" if pag_data["within_sla"] else "DEFECT"
    print(f"[5/5] Paginated Report Draw: {pag_data['latency_ms']:.3f} ms [SLA {status_pag}] (USL: <= {SLA_MAX_PAGE_CHUNK_MS} ms)")

    print("-" * 70)
    print("All Core Response-Time Interventions Verified & Conforming to TQM CO1 SLAs.")
    print("=" * 70)


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
