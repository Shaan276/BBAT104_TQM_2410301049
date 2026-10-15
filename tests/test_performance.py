"""
Performance SLA Benchmark Tests (Quality Goal Q05: Reduce Response Time)
Automates empirical verification against defined Upper Specification Limits (USL).
"""

import pytest
from src.database.connection import init_db
from src.modules.cache_manager import CacheManager, global_cache
from src.modules.fast_search import FastSearchEngine
from src.modules.quiz_crud import QuizCRUD
from src.modules.quiz_engine import QuizEngine
from src.modules.paginator import ReportPaginator
from src.modules.auth import AuthService
from src.config import (
    SLA_MAX_CACHE_READ_MS, SLA_MAX_SEARCH_LATENCY_MS,
    SLA_MAX_LOAD_QUIZ_LATENCY_MS, SLA_MAX_SUBMIT_LATENCY_MS,
    SLA_MAX_PAGE_CHUNK_MS
)


@pytest.fixture(autouse=True)
def setup_benchmark_db():
    init_db()


def test_q05_f3_cached_dashboard_latency():
    """Verify that cached dashboard reads conform to SLA (<= 15.0 ms)."""
    # Prime the cache
    QuizCRUD.get_dashboard_metrics(force_refresh=True)

    # Read from cache
    metrics, latency_ms, is_hit = QuizCRUD.get_dashboard_metrics(force_refresh=False)
    assert is_hit is True
    assert latency_ms <= SLA_MAX_CACHE_READ_MS, f"Cache latency {latency_ms} ms exceeded USL {SLA_MAX_CACHE_READ_MS} ms"


def test_q05_f1_fast_search_latency():
    """Verify that indexed search operates within SLA (<= 40.0 ms)."""
    results, latency_ms, within_sla = FastSearchEngine.search_quizzes(query="TQM")
    assert within_sla is True
    assert latency_ms <= SLA_MAX_SEARCH_LATENCY_MS, f"Search latency {latency_ms} ms exceeded USL {SLA_MAX_SEARCH_LATENCY_MS} ms"
    assert len(results) >= 1


def test_q05_f4_quiz_load_latency():
    """Verify that question bank loading stays under SLA (<= 50.0 ms)."""
    quiz_info, questions, latency_ms, within_sla = QuizEngine.load_quiz_session(quiz_id=1)
    assert within_sla is True
    assert latency_ms <= SLA_MAX_LOAD_QUIZ_LATENCY_MS, f"Load latency {latency_ms} ms exceeded USL {SLA_MAX_LOAD_QUIZ_LATENCY_MS} ms"
    assert len(questions) > 0


def test_q05_quiz_submission_latency():
    """Verify atomic grading and database commit completes under SLA (<= 100.0 ms)."""
    student = AuthService.get_user_by_username("piyush")
    assert student is not None

    answers = {1: "B", 2: "A", 3: "C", 4: "B", 5: "C"}
    summary, latency_ms, within_sla = QuizEngine.submit_attempt(
        quiz_id=1,
        user_id=student["id"],
        user_answers=answers
    )

    assert within_sla is True
    assert latency_ms <= SLA_MAX_SUBMIT_LATENCY_MS, f"Submission latency {latency_ms} ms exceeded USL {SLA_MAX_SUBMIT_LATENCY_MS} ms"
    assert summary["status"] == "PASSED"
    assert summary["score_percentage"] == 100.0


def test_q05_f5_paginated_reports_latency():
    """Verify server-side LIMIT/OFFSET chunking completes within SLA (<= 50.0 ms)."""
    data = ReportPaginator.get_paginated_attempts(page=1, page_size=10)
    assert data["within_sla"] is True
    assert data["latency_ms"] <= SLA_MAX_PAGE_CHUNK_MS, f"Chunking latency {data['latency_ms']} ms exceeded USL {SLA_MAX_PAGE_CHUNK_MS} ms"
    assert len(data["records"]) > 0
