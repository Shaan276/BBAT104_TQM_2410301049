"""
Authentication & Role Management Module (FR-01)
Supports Admin (Teacher) and Student session contexts.
"""

from typing import Optional, Dict, Any, List
from src.database.connection import get_db_connection


class AuthService:
    """Manages role-based sessions and user lookup without external overhead."""

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Look up user record by username."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, created_at FROM users WHERE username = ?", (username.strip().lower(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Look up user record by user ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def list_users(role: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all users or filter by role."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            if role:
                cursor.execute("SELECT id, username, role, created_at FROM users WHERE role = ? ORDER BY id", (role,))
            else:
                cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY id")
            return [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def create_user(username: str, role: str) -> int:
        """Create a new user with sanitized credentials."""
        cleaned_username = username.strip().lower()
        cleaned_role = role.strip().upper()
        if cleaned_role not in ("ADMIN", "STUDENT"):
            raise ValueError("Role must be ADMIN or STUDENT")
        if not cleaned_username:
            raise ValueError("Username cannot be empty")

        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, role) VALUES (?, ?)",
                    (cleaned_username, cleaned_role)
                )
                user_id = cursor.lastrowid
                from src.modules.logger_service import LoggerService
                LoggerService.log_audit("ADD_USER", f"Created user '{cleaned_username}' with role {cleaned_role}")
                return user_id
        finally:
            conn.close()
