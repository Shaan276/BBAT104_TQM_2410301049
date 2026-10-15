"""
Paginated Report Streamer (Quality Goal Q05 - Feature 5)
Executes server-side LIMIT/OFFSET chunking to stream historical records with low memory footprint.
"""

import time
import math
from typing import Dict, Any, Optional
from src.database.connection import get_db_connection
from src.config import DEFAULT_PAGE_SIZE, SLA_MAX_PAGE_CHUNK_MS


class ReportPaginator:
    """Manages paginated streaming of student attempt histories."""

    @staticmethod
    def get_paginated_attempts(
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        quiz_id: Optional[int] = None,
        username_query: str = ""
    ) -> Dict[str, Any]:
        """
        Stream attempt logs with indexed reverse-chronological ordering.
        Returns pagination packet with latency benchmarking.
        """
        start_time = time.perf_counter()
        safe_page = max(1, page)
        safe_size = max(1, min(page_size, 100))
        offset = (safe_page - 1) * safe_size

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # Base count and query filters
            where_clauses = ["1=1"]
            params = []

            if quiz_id:
                where_clauses.append("a.quiz_id = ?")
                params.append(quiz_id)

            if username_query.strip():
                where_clauses.append("u.username LIKE ?")
                params.append(f"%{username_query.strip().lower()}%")

            where_sql = " AND ".join(where_clauses)

            # 1. Total records count
            count_sql = f"""
                SELECT COUNT(*) FROM attempts a
                JOIN users u ON a.user_id = u.id
                WHERE {where_sql}
            """
            cursor.execute(count_sql, params)
            total_records = cursor.fetchone()[0]
            total_pages = max(1, math.ceil(total_records / safe_size))

            # 2. Chunked fetch using LIMIT / OFFSET (utilizes idx_attempts_created_at_desc)
            query_sql = f"""
                SELECT a.id, a.quiz_id, q.title AS quiz_title, q.category AS quiz_category,
                       a.user_id, u.username, a.total_questions, a.correct_answers,
                       a.score_percentage, a.status, a.latency_ms, a.created_at
                FROM attempts a
                JOIN quizzes q ON a.quiz_id = q.id
                JOIN users u ON a.user_id = u.id
                WHERE {where_sql}
                ORDER BY a.created_at DESC
                LIMIT ? OFFSET ?
            """
            fetch_params = list(params) + [safe_size, offset]
            cursor.execute(query_sql, fetch_params)
            rows = [dict(r) for r in cursor.fetchall()]

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            within_sla = elapsed_ms <= SLA_MAX_PAGE_CHUNK_MS

            return {
                "records": rows,
                "page": safe_page,
                "page_size": safe_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_prev": safe_page > 1,
                "has_next": safe_page < total_pages,
                "latency_ms": round(elapsed_ms, 3),
                "within_sla": within_sla,
                "sla_limit_ms": SLA_MAX_PAGE_CHUNK_MS
            }
        finally:
            conn.close()
