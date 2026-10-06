"""
Quiz Execution & Zero-Latency Auto-Grading Engine (FR-04)
Pre-loads questions into memory for instant transitions and commits graded attempts atomically.
"""

import time
from typing import Dict, Any, List, Tuple
from src.database.connection import get_db_connection
from src.modules.cache_manager import global_cache
from src.config import SLA_MAX_LOAD_QUIZ_LATENCY_MS, SLA_MAX_SUBMIT_LATENCY_MS


class QuizEngine:
    """Core assessment runner delivering sub-100ms submission and grading."""

    @staticmethod
    def load_quiz_session(quiz_id: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]], float, bool]:
        """
        Pre-load quiz header and all questions into memory.
        Returns: (quiz_info, questions_list, latency_ms, within_sla)
        """
        start_time = time.perf_counter()
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
            quiz_row = cursor.fetchone()
            if not quiz_row:
                raise ValueError(f"Quiz ID {quiz_id} not found")

            # Utilize idx_questions_quiz_id
            cursor.execute(
                """SELECT id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks
                   FROM questions WHERE quiz_id = ? ORDER BY id ASC""",
                (quiz_id,)
            )
            questions = [dict(r) for r in cursor.fetchall()]

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            within_sla = elapsed_ms <= SLA_MAX_LOAD_QUIZ_LATENCY_MS
            return dict(quiz_row), questions, round(elapsed_ms, 3), within_sla
        finally:
            conn.close()

    @staticmethod
    def submit_attempt(quiz_id: int, user_id: int, user_answers: Dict[int, str]) -> Tuple[Dict[str, Any], float, bool]:
        """
        Grade user answers and atomically record attempt in database.
        user_answers: mapping of question_id -> selected_option ('A', 'B', 'C', 'D')
        Returns: (result_summary, latency_ms, within_sla)
        """
        start_time = time.perf_counter()
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # 1. Fetch quiz passing score
            cursor.execute("SELECT title, passing_score FROM quizzes WHERE id = ?", (quiz_id,))
            quiz_row = cursor.fetchone()
            if not quiz_row:
                raise ValueError(f"Quiz ID {quiz_id} not found")
            quiz_title, passing_score = quiz_row[0], quiz_row[1]

            # 2. Fetch answer keys
            cursor.execute("SELECT id, correct_option, marks FROM questions WHERE quiz_id = ?", (quiz_id,))
            questions = cursor.fetchall()
            total_questions = len(questions)

            if total_questions == 0:
                raise ValueError("Cannot submit attempt for a quiz with no questions")

            correct_count = 0
            earned_marks = 0
            total_marks = 0
            item_details = []

            for q_id, correct_opt, marks in questions:
                total_marks += marks
                selected = user_answers.get(q_id, "NONE")
                is_correct = 1 if selected.upper() == correct_opt.upper() else 0
                if is_correct:
                    correct_count += 1
                    earned_marks += marks
                item_details.append((q_id, selected, is_correct))

            score_percentage = round((earned_marks / total_marks * 100.0) if total_marks > 0 else 0.0, 1)
            status = "PASSED" if score_percentage >= passing_score else "FAILED"

            # Compute preliminary latency before database commit
            calc_latency_ms = (time.perf_counter() - start_time) * 1000.0

            # 3. Atomic Database Commit
            with conn:
                cursor.execute(
                    """INSERT INTO attempts 
                       (quiz_id, user_id, total_questions, correct_answers, score_percentage, status, latency_ms)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (quiz_id, user_id, total_questions, correct_count, score_percentage, status, round(calc_latency_ms, 2))
                )
                attempt_id = cursor.lastrowid

                # Insert question breakdown records
                answer_records = [
                    (attempt_id, q_id, selected, is_correct)
                    for q_id, selected, is_correct in item_details
                ]
                cursor.executemany(
                    """INSERT INTO attempt_answers (attempt_id, question_id, selected_option, is_correct)
                       VALUES (?, ?, ?, ?)""",
                    answer_records
                )

            # Invalidate cached metrics
            global_cache.invalidate("dashboard_metrics")

            total_elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            within_sla = total_elapsed_ms <= SLA_MAX_SUBMIT_LATENCY_MS

            summary = {
                "attempt_id": attempt_id,
                "quiz_id": quiz_id,
                "quiz_title": quiz_title,
                "total_questions": total_questions,
                "correct_answers": correct_count,
                "earned_marks": earned_marks,
                "total_marks": total_marks,
                "score_percentage": score_percentage,
                "passing_score": passing_score,
                "status": status,
                "latency_ms": round(total_elapsed_ms, 3),
                "within_sla": within_sla,
                "sla_limit_ms": SLA_MAX_SUBMIT_LATENCY_MS
            }
            return summary, round(total_elapsed_ms, 3), within_sla
        finally:
            conn.close()
