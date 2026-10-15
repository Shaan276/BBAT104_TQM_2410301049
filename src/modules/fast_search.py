"""
Fast Search Engine (Quality Goal Q05 - Feature 1)
Delivers indexed, debounced catalog search with millisecond latency benchmarking.
"""

import time
from typing import List, Dict, Any, Tuple
from src.database.connection import get_db_connection
from src.config import SLA_MAX_SEARCH_LATENCY_MS


class FastSearchEngine:
    """Executes indexed search across quizzes and question repositories."""

    @staticmethod
    def search_quizzes(query: str = "", category: str = "") -> Tuple[List[Dict[str, Any]], float, bool]:
        """
        Search active quizzes by title or category.
        Returns: (results_list, latency_ms, within_sla)
        """
        start_time = time.perf_counter()
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query_str = query.strip()
            cat_str = category.strip()

            sql = "SELECT id, title, category, duration_minutes, passing_score, is_active FROM quizzes WHERE 1=1"
            params: List[Any] = []

            if cat_str and cat_str.lower() != "all":
                sql += " AND category = ?"
                params.append(cat_str)

            if query_str:
                sql += " AND (title LIKE ? OR category LIKE ?)"
                wildcard = f"%{query_str}%"
                params.extend([wildcard, wildcard])

            sql += " ORDER BY category ASC, title ASC"
            cursor.execute(sql, params)
            rows = [dict(r) for r in cursor.fetchall()]

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            within_sla = elapsed_ms <= SLA_MAX_SEARCH_LATENCY_MS
            return rows, round(elapsed_ms, 3), within_sla
        finally:
            conn.close()

    @staticmethod
    def search_questions(quiz_id: int, query: str = "") -> Tuple[List[Dict[str, Any]], float, bool]:
        """
        Search questions within a quiz using indexed quiz_id lookup.
        Returns: (questions_list, latency_ms, within_sla)
        """
        start_time = time.perf_counter()
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            query_str = query.strip()

            if query_str:
                cursor.execute(
                    """SELECT id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks
                       FROM questions
                       WHERE quiz_id = ? AND question_text LIKE ?
                       ORDER BY id ASC""",
                    (quiz_id, f"%{query_str}%")
                )
            else:
                cursor.execute(
                    """SELECT id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks
                       FROM questions
                       WHERE quiz_id = ?
                       ORDER BY id ASC""",
                    (quiz_id,)
                )

            rows = [dict(r) for r in cursor.fetchall()]
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            within_sla = elapsed_ms <= SLA_MAX_SEARCH_LATENCY_MS
            return rows, round(elapsed_ms, 3), within_sla
        finally:
            conn.close()
