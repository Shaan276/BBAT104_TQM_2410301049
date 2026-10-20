"""
Dashboard View (Quality Goal Q05 - Feature 3: Cached Dashboard)
Displays high-speed in-memory cached performance metrics and SLA compliance badges.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any
from src.modules.quiz_crud import QuizCRUD
from src.modules.logger_service import LoggerService
from src.database.connection import get_db_connection
from src.modules.cache_manager import global_cache
from src.config import (
    THEME_COLOR_PRIMARY, THEME_COLOR_ACCENT, THEME_COLOR_SUCCESS,
    THEME_COLOR_WARNING, THEME_COLOR_BG, SLA_MAX_CACHE_READ_MS
)


class DashboardView(ttk.Frame):
    """Cached operational metrics dashboard view."""

    def __init__(
        self,
        parent: tk.Widget,
        get_current_user: Optional[Callable[[], Dict[str, Any]]] = None,
        on_navigate: Optional[Callable[[str], None]] = None
    ):
        super().__init__(parent)
        self.get_current_user = get_current_user
        self.on_navigate = on_navigate
        self._build_ui()
        self.update_role_view()

    def _build_ui(self) -> None:
        self.configure(style="TFrame")

        # Top Buttons Bar (no cache status text — just action buttons)
        self.banner_frame = tk.Frame(self, bg="#EFF6FF", bd=1, relief=tk.SOLID)
        self.banner_frame.pack(fill=tk.X, padx=20, pady=(15, 10))

        self.btn_refresh = tk.Button(
            self.banner_frame,
            text="🔄 Invalidate & Refresh Cache",
            font=("Segoe UI", 9, "bold"),
            bg=THEME_COLOR_PRIMARY,
            fg="white",
            relief=tk.FLAT,
            padx=10,
            command=lambda: self.refresh_metrics(force=True)
        )
        self.btn_refresh.pack(side=tk.RIGHT, padx=15, pady=6)

        self.btn_clear_data = tk.Button(
            self.banner_frame,
            text="🗑️ Clear All Data",
            font=("Segoe UI", 9, "bold"),
            bg="#DC2626",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            command=self._confirm_clear_all_data
        )
        self.btn_clear_data.pack(side=tk.RIGHT, padx=(0, 6), pady=6)

        self.btn_audit = tk.Button(
            self.banner_frame,
            text="📋 Audit Logs",
            font=("Segoe UI", 9, "bold"),
            bg="#0D9488",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            command=self._open_audit_modal
        )
        self.btn_audit.pack(side=tk.RIGHT, padx=(0, 6), pady=6)

        self.btn_toggle_view = tk.Button(
            self.banner_frame,
            text="👤 My Scores",
            font=("Segoe UI", 9, "bold"),
            bg="#3B82F6",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            command=self._toggle_view_mode
        )
        # Only shown for students — packed conditionally in update_role_view

        # Metric Cards Container
        self.cards_frame = tk.Frame(self, bg=THEME_COLOR_BG)
        self.cards_frame.pack(fill=tk.X, padx=20, pady=10)

        # 6 Metric Cards
        self.card_quizzes = self._create_card(self.cards_frame, "Total Active Quizzes", "0", THEME_COLOR_PRIMARY)
        self.card_questions = self._create_card(self.cards_frame, "Question Bank Size", "0", THEME_COLOR_PRIMARY)
        self.card_attempts = self._create_card(self.cards_frame, "Total Submissions", "0", THEME_COLOR_PRIMARY)
        self.card_avg_score = self._create_card(self.cards_frame, "Cohort Average Score", "0.0%", THEME_COLOR_ACCENT)
        self.card_pass_rate = self._create_card(self.cards_frame, "Overall Pass Rate", "0.0%", THEME_COLOR_SUCCESS)
        self.card_latency = self._create_card(self.cards_frame, "Avg Submission Latency", "0.0 ms", THEME_COLOR_WARNING)

        # Layout cards in a 2x3 grid
        cards = [self.card_quizzes, self.card_questions, self.card_attempts,
                 self.card_avg_score, self.card_pass_rate, self.card_latency]
        for idx, card in enumerate(cards):
            r = idx // 3
            c = idx % 3
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            self.cards_frame.grid_columnconfigure(c, weight=1)

        # Quick Actions & Quality Summary Section
        actions_frame = tk.LabelFrame(
            self,
            text=" TQM Response Time Optimization (Q05 Mandate) ",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=THEME_COLOR_PRIMARY,
            padx=15,
            pady=10
        )
        actions_frame.pack(fill=tk.X, padx=20, pady=(5, 5))

        summary_text = (
            "• Deming 85/15 Rule: Database I/O bottlenecks removed via in-memory caching and B-Tree indexing.\n"
            f"• Cache SLA: ≤ {SLA_MAX_CACHE_READ_MS} ms (USL). The '🔄 Invalidate & Refresh Cache' button above forces a fresh DB read — discarding any cached values.\n"
            "• Quick Navigation: Instant zero-redraw view swapping using pre-mounted containers (Alt+D/Q/M/R).\n"
            "• Poka-Yoke: Atomic quiz submissions prevent double-counting. Invalid inputs are blocked before reaching the database."
        )
        tk.Label(actions_frame, text=summary_text, font=("Segoe UI", 9), bg="white",
                 fg="#475569", justify=tk.LEFT).pack(anchor="w", pady=(0, 8))

        btn_box = tk.Frame(actions_frame, bg="white")
        btn_box.pack(anchor="w")

        tk.Button(btn_box, text="🚀 Browse Quizzes (Alt+Q)", font=("Segoe UI", 10, "bold"),
                  bg=THEME_COLOR_ACCENT, fg="white", relief=tk.FLAT, padx=15, pady=5,
                  command=lambda: self._navigate("quizzes")).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(btn_box, text="📊 Historical Reports (Alt+R)", font=("Segoe UI", 10, "bold"),
                  bg=THEME_COLOR_PRIMARY, fg="white", relief=tk.FLAT, padx=15, pady=5,
                  command=lambda: self._navigate("reports")).pack(side=tk.LEFT)

    def _create_card(self, parent: tk.Widget, title: str, value: str, color: str) -> tk.Frame:
        """Helper to create a modern statistic card."""
        frame = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID)
        lbl_t = tk.Label(frame, text=title.upper(), font=("Segoe UI", 8, "bold"), fg="#64748B", bg="white")
        lbl_t.pack(anchor="w", padx=12, pady=(10, 2))
        lbl_v = tk.Label(frame, text=value, font=("Segoe UI", 18, "bold"), fg=color, bg="white")
        lbl_v.pack(anchor="w", padx=12, pady=(0, 10))
        frame._title_label = lbl_t
        frame._value_label = lbl_v  # Store reference for quick update
        return frame

    def _toggle_view_mode(self) -> None:
        """Toggle between Personal Student scores and Institutional Cohort metrics."""
        curr = getattr(self, "view_mode", "cohort")
        self.view_mode = "personal" if curr == "cohort" else "cohort"
        self.refresh_metrics(force=False)

    def refresh_metrics(self, force: bool = False) -> None:
        """Fetch metrics and update UI labels."""
        user = self.get_current_user() if self.get_current_user else None
        if not hasattr(self, "view_mode"):
            self.view_mode = "personal" if (user and user.get("role") == "STUDENT") else "cohort"

        user_id = user["id"] if (self.view_mode == "personal" and user) else None
        metrics, latency_ms, is_hit = QuizCRUD.get_dashboard_metrics(force_refresh=force, user_id=user_id)

        if self.view_mode == "personal":
            uname = user['username'].upper() if user else 'STUDENT'
            self.card_quizzes._title_label.config(text="AVAILABLE QUIZZES")
            self.card_questions._title_label.config(text="QUESTION BANK")
            self.card_attempts._title_label.config(text=f"MY SUBMISSIONS ({uname})")
            self.card_avg_score._title_label.config(text="MY AVERAGE SCORE")
            self.card_pass_rate._title_label.config(text="MY PASS RATE")
            self.card_latency._title_label.config(text="MY SUBMISSION LATENCY")
            if self.btn_toggle_view.winfo_ismapped():
                self.btn_toggle_view.config(text="👥 Switch to Cohort View", bg="#475569")
            mode_desc = f"👤 Personal Dashboard ({user['username'] if user else 'Student'})"
        else:
            self.card_quizzes._title_label.config(text="TOTAL ACTIVE QUIZZES")
            self.card_questions._title_label.config(text="QUESTION BANK SIZE")
            self.card_attempts._title_label.config(text="TOTAL SUBMISSIONS (ALL)")
            self.card_avg_score._title_label.config(text="COHORT AVERAGE SCORE")
            self.card_pass_rate._title_label.config(text="OVERALL PASS RATE")
            self.card_latency._title_label.config(text="AVG SUBMISSION LATENCY")
            if self.btn_toggle_view.winfo_ismapped():
                self.btn_toggle_view.config(text="👤 Switch to My Scores", bg="#2563EB")
            mode_desc = "👑 Institutional Cohort Dashboard (All Students)"

        self.card_quizzes._value_label.config(text=str(metrics["total_quizzes"]))
        self.card_questions._value_label.config(text=str(metrics["total_questions"]))
        self.card_attempts._value_label.config(text=str(metrics["total_attempts"]))
        self.card_avg_score._value_label.config(text=f"{metrics['average_score']}%")
        self.card_pass_rate._value_label.config(text=f"{metrics['pass_rate_percent']}%")
        self.card_latency._value_label.config(text=f"{metrics['avg_submission_latency_ms']} ms")

    def _navigate(self, view_name: str) -> None:
        if self.on_navigate:
            self.on_navigate(view_name)

    def _confirm_clear_all_data(self) -> None:
        """Wipe all attempts, audit logs, and error logs — then reset the cache."""
        user = self.get_current_user() if self.get_current_user else None
        if not user or user.get("role") != "ADMIN":
            messagebox.showwarning("Admin Only", "Only administrators can clear data.")
            return

        confirmed = messagebox.askyesno(
            "⚠️ Clear All Data",
            "This will permanently delete:\n\n"
            "  • All student quiz attempts\n"
            "  • All audit logs\n"
            "  • All error logs\n\n"
            "Quizzes, questions and user accounts will be KEPT.\n\n"
            "Are you sure you want to start fresh?"
        )
        if not confirmed:
            return

        try:
            conn = get_db_connection()
            with conn:
                conn.execute("DELETE FROM attempt_answers")
                conn.execute("DELETE FROM attempts")
                conn.execute("DELETE FROM audit_logs")
                conn.execute("DELETE FROM error_logs")
            conn.close()

            # Clear the in-memory cache so metrics reset immediately
            global_cache.invalidate()

            messagebox.showinfo(
                "✅ Data Cleared",
                "All attempts, audit logs, and error logs have been deleted.\n"
                "Quizzes, questions, and users are untouched.\n\n"
                "The dashboard will now reload fresh numbers."
            )
            self.refresh_metrics(force=True)

        except Exception as e:
            messagebox.showerror("Error", f"Could not clear data:\n{e}")

    def update_role_view(self) -> None:
        """Update audit button styling and toggle button visibility based on user role."""
        user = self.get_current_user() if self.get_current_user else None
        if not user or not hasattr(self, "btn_audit"):
            return
        if user.get("role") == "ADMIN":
            self.btn_audit.config(text="📋 Audit Logs (Admin)", bg="#0D9488")
            self.btn_clear_data.pack(side=tk.RIGHT, padx=(0, 6), pady=6)
            self.view_mode = "cohort"
            # Admins always see cohort — hide the personal toggle
            self.btn_toggle_view.pack_forget()
        else:
            self.btn_audit.config(text="🔒 Audit Logs (Admin Only)", bg="#64748B")
            self.btn_clear_data.pack_forget()
            self.view_mode = "personal"
            # Students can toggle between their personal scores and cohort
            self.btn_toggle_view.pack(side=tk.RIGHT, padx=(0, 6), pady=6)
        self.refresh_metrics(force=False)

    def _open_audit_modal(self) -> None:
        user = self.get_current_user() if self.get_current_user else None
        if user and user.get("role") != "ADMIN":
            messagebox.showwarning(
                "Access Restricted",
                f"🔒 Confidential Audit Trail!\n\n"
                f"Active User: {user.get('username')} ({user.get('role')})\n\n"
                "System audit logs are restricted to ADMINISTRATORS.\n"
                "Please switch to an ADMIN account to view system logs."
            )
            return

        modal = tk.Toplevel(self)
        modal.title("System Audit Logs — What Happened & Who Did It")
        modal.geometry("920x540")
        modal.transient(self)
        modal.grab_set()

        # Header
        hdr = tk.Frame(modal, bg="#1E3A5F", padx=15, pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(
            hdr,
            text="📋  System Audit Log — Every action recorded with user, time & latency",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#1E3A5F"
        ).pack(side=tk.LEFT)

        # Legend row
        legend = tk.Frame(modal, bg="#F0F9FF", padx=15, pady=6)
        legend.pack(fill=tk.X)
        tk.Label(legend, text="How to read this log:", font=("Segoe UI", 9, "bold"), bg="#F0F9FF", fg="#0369A1").pack(side=tk.LEFT)
        for color, meaning in [("#D1FAE5", "Quiz / question authored"), ("#DBEAFE", "Student took a quiz"),
                                ("#FEF9C3", "Cache / search action"), ("#FEE2E2", "Error / rejected input"),
                                ("#F3F4F6", "Other system event")]:
            dot = tk.Label(legend, text="  ●  ", bg=color, fg=color, font=("Segoe UI", 13))
            dot.pack(side=tk.LEFT, padx=(8, 0))
            tk.Label(legend, text=meaning, font=("Segoe UI", 9), bg="#F0F9FF", fg="#374151").pack(side=tk.LEFT)

        # Treeview
        tree_frame = tk.Frame(modal, padx=15, pady=5)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("when", "who", "what_happened", "speed")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        tree.heading("when",          text="🕐 When")
        tree.heading("who",           text="👤 Who")
        tree.heading("what_happened", text="📝 What Happened")
        tree.heading("speed",         text="⚡ Speed")

        tree.column("when",          width=155, anchor="center")
        tree.column("who",           width=110, anchor="w")
        tree.column("what_happened", width=520, anchor="w")
        tree.column("speed",         width=90,  anchor="center")

        # Color tags
        tree.tag_configure("quiz_action",   background="#D1FAE5")   # green — authoring
        tree.tag_configure("attempt_action",background="#DBEAFE")   # blue  — quiz taken
        tree.tag_configure("cache_action",  background="#FEF9C3")   # yellow — cache/search
        tree.tag_configure("error_action",  background="#FEE2E2")   # red   — errors
        tree.tag_configure("other",         background="#F9FAFB")   # grey  — misc

        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Readable action descriptions
        ACTION_DESCRIPTIONS = {
            "CREATE_QUIZ":     "📚 Admin created a new quiz",
            "UPDATE_QUIZ":     "✏️  Admin edited a quiz",
            "DELETE_QUIZ":     "🗑️  Admin deleted a quiz (all questions removed)",
            "CREATE_QUESTION": "➕ Question added to quiz",
            "UPDATE_QUESTION": "✏️  Question edited",
            "DELETE_QUESTION": "🗑️  Question removed from quiz",
            "SUBMIT_ATTEMPT":  "📝 Student submitted a quiz attempt",
            "FAST_SEARCH":     "🔍 Search performed on quiz catalog",
            "CACHE_REFRESH":   "🔄 Dashboard cache was cleared & reloaded",
            "CACHE_HIT":       "⚡ Dashboard loaded instantly from memory (cache hit)",
            "CACHE_MISS":      "💾 Dashboard reloaded from database (cache miss)",
            "ADD_USER":        "👤 New user account created",
            "LOGIN":           "🔑 User logged in / session switched",
        }

        def get_tag(action: str) -> str:
            if any(k in action for k in ("QUIZ", "QUESTION")):
                return "quiz_action"
            if "ATTEMPT" in action:
                return "attempt_action"
            if any(k in action for k in ("CACHE", "SEARCH")):
                return "cache_action"
            if any(k in action for k in ("ERROR", "REJECT", "BLOCK")):
                return "error_action"
            return "other"

        logs = LoggerService.get_audit_logs(limit=200)
        for log in logs:
            action_raw = log["action"]
            readable_action = ACTION_DESCRIPTIONS.get(action_raw, f"🔧 {action_raw.replace('_', ' ').title()}")
            detail = log["detail"]
            who = log.get("username") or "system"
            speed = f"{log.get('latency_ms', 0.0):.2f} ms"
            tag = get_tag(action_raw)

            # Build human-readable "what happened" column
            what = f"{readable_action}  —  {detail}"

            tree.insert("", tk.END, values=(
                log["created_at"],
                who,
                what,
                speed
            ), tags=(tag,))

        # Footer
        foot = tk.Frame(modal, bg="#F8FAFC", padx=15, pady=8)
        foot.pack(fill=tk.X)
        tk.Label(foot, text=f"Showing last {len(logs)} events, newest first.",
                 font=("Segoe UI", 9, "italic"), fg="#64748B", bg="#F8FAFC").pack(side=tk.LEFT)
        tk.Button(foot, text="Close", font=("Segoe UI", 10), bg="#E2E8F0",
                  padx=15, pady=4, command=modal.destroy).pack(side=tk.RIGHT)
