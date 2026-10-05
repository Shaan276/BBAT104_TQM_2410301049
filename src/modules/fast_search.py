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
    def search_quizzes(query: str = "", category: str = "", sort_by: str = "id_asc") -> Tuple[List[Dict[str, Any]], float, bool]:
        """
        Search active quizzes by title or category with fast index-accelerated sorting.
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

            order_clause = "id ASC"
            sort_clean = sort_by.strip().lower()
            if sort_clean in ("title_asc", "title (a-z)", "title"):
                order_clause = "title COLLATE NOCASE ASC"
            elif sort_clean in ("title_desc", "title (z-a)"):
                order_clause = "title COLLATE NOCASE DESC"
            elif sort_clean in ("category_asc", "category (a-z)", "category"):
                order_clause = "category COLLATE NOCASE ASC, title ASC"
            elif sort_clean in ("category_desc", "category (z-a)"):
                order_clause = "category COLLATE NOCASE DESC, title ASC"
            elif sort_clean in ("duration_asc", "duration (short-long)", "duration (min)"):
                order_clause = "duration_minutes ASC"
            elif sort_clean in ("duration_desc", "duration (long-short)"):
                order_clause = "duration_minutes DESC"
            elif sort_clean in ("pass_score_asc", "passing score (low-high)", "passing score (%)"):
                order_clause = "passing_score ASC"
            elif sort_clean in ("pass_score_desc", "passing score (high-low)"):
                order_clause = "passing_score DESC"
            elif sort_clean in ("id_desc", "id (high-low)"):
                order_clause = "id DESC"
            else:
                order_clause = "id ASC"

            sql += f" ORDER BY {order_clause}"
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
