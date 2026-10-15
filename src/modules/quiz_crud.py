"""
Quiz & Question CRUD Module (FR-02 & FR-03)
Provides full persistence lifecycle and synchronizes with in-memory cache invalidation.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from src.database.connection import get_db_connection
from src.modules.cache_manager import global_cache


class QuizCRUD:
    """Manages question bank authoring and quiz formulation."""

    # -------------------------------------------------------------
    # Quiz Operations
    # -------------------------------------------------------------
    @staticmethod
    def create_quiz(title: str, category: str, duration_minutes: int = 10, passing_score: int = 60) -> int:
        """Create a new quiz assessment."""
        if not title.strip() or not category.strip():
            raise ValueError("Title and Category are mandatory")
        if duration_minutes <= 0 or passing_score <= 0:
            raise ValueError("Duration and Passing Score must be positive")

        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO quizzes (title, category, duration_minutes, passing_score)
                       VALUES (?, ?, ?, ?)""",
                    (title.strip(), category.strip(), duration_minutes, passing_score)
                )
                quiz_id = cursor.lastrowid
                global_cache.invalidate("dashboard_metrics")
                return quiz_id
        finally:
            conn.close()

    @staticmethod
    def get_quizzes(category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all quizzes, optionally filtered by category."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            if category and category.lower() != "all":
                cursor.execute(
                    "SELECT * FROM quizzes WHERE category = ? ORDER BY id DESC",
                    (category.strip(),)
                )
            else:
                cursor.execute("SELECT * FROM quizzes ORDER BY id DESC")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_quiz_by_id(quiz_id: int) -> Optional[Dict[str, Any]]:
        """Fetch single quiz by ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def update_quiz(quiz_id: int, title: str, category: str, duration_minutes: int, passing_score: int, is_active: int = 1) -> bool:
        """Update existing quiz settings."""
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE quizzes 
                       SET title = ?, category = ?, duration_minutes = ?, passing_score = ?, is_active = ?
                       WHERE id = ?""",
                    (title.strip(), category.strip(), duration_minutes, passing_score, is_active, quiz_id)
                )
                updated = cursor.rowcount > 0
                if updated:
                    global_cache.invalidate("dashboard_metrics")
                return updated
        finally:
            conn.close()

    @staticmethod
    def delete_quiz(quiz_id: int) -> bool:
        """Cascade delete quiz and all child questions/attempts."""
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
                deleted = cursor.rowcount > 0
                if deleted:
                    global_cache.invalidate("dashboard_metrics")
                return deleted
        finally:
            conn.close()

    @staticmethod
    def get_categories() -> List[str]:
        """Fetch distinct categories for dropdown filtering."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM quizzes ORDER BY category ASC")
            return [r[0] for r in cursor.fetchall() if r[0]]
        finally:
            conn.close()

    # -------------------------------------------------------------
    # Question Operations
    # -------------------------------------------------------------
    @staticmethod
    def create_question(
        quiz_id: int,
        question_text: str,
        option_a: str,
        option_b: str,
        option_c: str,
        option_d: str,
        correct_option: str,
        marks: int = 1
    ) -> int:
        """Add a multiple-choice question to a quiz with Poka-Yoke validation."""
        if not question_text.strip() or not option_a.strip() or not option_b.strip() or not option_c.strip() or not option_d.strip():
            raise ValueError("Question text and all four options are mandatory")
        
        corr = correct_option.strip().upper()
        if corr not in ("A", "B", "C", "D"):
            raise ValueError("Correct option must be A, B, C, or D")

        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (quiz_id, question_text.strip(), option_a.strip(), option_b.strip(), option_c.strip(), option_d.strip(), corr, marks)
                )
                qid = cursor.lastrowid
                global_cache.invalidate("dashboard_metrics")
                return qid
        finally:
            conn.close()

    @staticmethod
    def get_questions_by_quiz(quiz_id: int) -> List[Dict[str, Any]]:
        """Retrieve all questions for a quiz (uses B-Tree index idx_questions_quiz_id)."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions WHERE quiz_id = ? ORDER BY id ASC", (quiz_id,))
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def update_question(
        question_id: int,
        question_text: str,
        option_a: str,
        option_b: str,
        option_c: str,
        option_d: str,
        correct_option: str,
        marks: int = 1
    ) -> bool:
        """Update question content."""
        corr = correct_option.strip().upper()
        if corr not in ("A", "B", "C", "D"):
            raise ValueError("Correct option must be A, B, C, or D")

        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE questions 
                       SET question_text = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, correct_option = ?, marks = ?
                       WHERE id = ?""",
                    (question_text.strip(), option_a.strip(), option_b.strip(), option_c.strip(), option_d.strip(), corr, marks, question_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def delete_question(question_id: int) -> bool:
        """Delete a single question."""
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
                deleted = cursor.rowcount > 0
                if deleted:
                    global_cache.invalidate("dashboard_metrics")
                return deleted
        finally:
            conn.close()

    # -------------------------------------------------------------
    # Cached Dashboard Aggregations (Q05-F3)
    # -------------------------------------------------------------
    @staticmethod
    def get_dashboard_metrics(force_refresh: bool = False) -> Tuple[Dict[str, Any], float, bool]:
        """
        Fetch summary metrics. Checks memory cache first.
        Returns: (metrics_dict, latency_ms, is_cache_hit)
        """
        cache_key = "dashboard_metrics"
        if not force_refresh:
            cached_val, latency_ms, is_hit = global_cache.get(cache_key)
            if is_hit and cached_val is not None:
                return cached_val, latency_ms, True

        # Cache Miss: Compute from SQLite persistence layer
        start_time = time.perf_counter()
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM quizzes WHERE is_active = 1")
            total_quizzes = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM questions")
            total_questions = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*), AVG(score_percentage) FROM attempts")
            attempt_row = cursor.fetchone()
            total_attempts = attempt_row[0]
            avg_score = round(attempt_row[1] or 0.0, 1)

            cursor.execute("SELECT COUNT(*) FROM attempts WHERE status = 'PASSED'")
            passed_attempts = cursor.fetchone()[0]
            pass_rate = round((passed_attempts / total_attempts * 100.0) if total_attempts > 0 else 0.0, 1)

            cursor.execute("SELECT AVG(latency_ms) FROM attempts")
            avg_latency = round(cursor.fetchone()[0] or 0.0, 2)

            metrics = {
                "total_quizzes": total_quizzes,
                "total_questions": total_questions,
                "total_attempts": total_attempts,
                "average_score": avg_score,
                "pass_rate_percent": pass_rate,
                "avg_submission_latency_ms": avg_latency,
            }

            global_cache.set(cache_key, metrics)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return metrics, round(elapsed_ms, 3), False
        finally:
            conn.close()
