"""
Audit & Error Logger Service (TQM Traceability & FMEA Data Feed)
Inspired by TQM core architectures:
- Tracks operational events in `audit_logs` for complete traceability.
- Records Poka-Yoke error intercepts in `error_logs` to feed FMEA and Pareto SQC analysis.
"""

from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection


class LoggerService:
    """Manages transactional audit logs and error logging for SQC tools."""

    @staticmethod
    def log_audit(action: str, detail: str, user_id: Optional[int] = None, latency_ms: float = 0.0) -> None:
        """Record an operational transaction in the audit trail."""
        try:
            conn = get_db_connection()
            with conn:
                conn.execute(
                    """INSERT INTO audit_logs (user_id, action, detail, latency_ms)
                       VALUES (?, ?, ?, ?)""",
                    (user_id, action.strip().upper(), detail.strip(), round(latency_ms, 2))
                )
            conn.close()
        except Exception:
            pass  # Non-blocking logging

    @staticmethod
    def log_error(error_code: str, problem: str, context: str = "") -> None:
        """Record a Poka-Yoke intercept or failure mode for FMEA RPN auditing."""
        try:
            conn = get_db_connection()
            with conn:
                conn.execute(
                    """INSERT INTO error_logs (error_code, problem, context)
                       VALUES (?, ?, ?)""",
                    (error_code.strip().upper(), problem.strip(), context.strip())
                )
            conn.close()
        except Exception:
            pass

    @staticmethod
    def get_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent audit transactions."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT a.id, a.user_id, u.username, a.action, a.detail, a.latency_ms, a.created_at
                   FROM audit_logs a
                   LEFT JOIN users u ON a.user_id = u.id
                   ORDER BY a.created_at DESC LIMIT ?""",
                (limit,)
            )
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_error_counts() -> List[Dict[str, Any]]:
        """Group error logs for Pareto analysis and FMEA occurrence ratings."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT error_code, problem, COUNT(*) as count, MAX(created_at) as last_seen
                   FROM error_logs
                   GROUP BY error_code, problem
                   ORDER BY count DESC"""
            )
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()
