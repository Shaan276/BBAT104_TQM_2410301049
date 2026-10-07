"""
Dashboard View (Quality Goal Q05 - Feature 3: Cached Dashboard)
Displays high-speed in-memory cached performance metrics and SLA compliance badges.
"""

import tkinter as tk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any
from src.modules.quiz_crud import QuizCRUD
from src.modules.logger_service import LoggerService
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

        # Top Banner: TQM SLA Latency Indicator
        self.banner_frame = tk.Frame(self, bg="#EFF6FF", bd=1, relief=tk.SOLID)
        self.banner_frame.pack(fill=tk.X, padx=20, pady=(15, 10))

        self.lbl_cache_status = tk.Label(
            self.banner_frame,
            text="⚡ In-Memory Cache: Initializing...",
            font=("Segoe UI", 10, "bold"),
            bg="#EFF6FF",
            fg=THEME_COLOR_ACCENT
        )
        self.lbl_cache_status.pack(side=tk.LEFT, padx=15, pady=8)

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
            text="👥 View: Cohort",
            font=("Segoe UI", 9, "bold"),
            bg="#3B82F6",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            command=self._toggle_view_mode
        )
        self.btn_toggle_view.pack(side=tk.RIGHT, padx=(0, 6), pady=6)

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
            pady=15
        )
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        summary_text = (
            "• Deming 85/15 Rule: Database I/O bottlenecks removed via in-memory caching and B-Tree indexing.\n"
            f"• Cache Performance SLA: Target response time < 5.0 ms | Upper Specification Limit (USL) ≤ {SLA_MAX_CACHE_READ_MS} ms.\n"
            "• Quick Navigation: Instant zero-redraw view swapping using pre-mounted containers.\n"
            "• Mistake-Proofing (Poka-Yoke): Atomically commits candidate attempts to eliminate double submissions."
        )
        lbl_summary = tk.Label(
            actions_frame,
            text=summary_text,
            font=("Segoe UI", 10),
            bg="white",
            fg="#475569",
            justify=tk.LEFT
        )
        lbl_summary.pack(anchor="w", pady=(0, 15))

        btn_box = tk.Frame(actions_frame, bg="white")
        btn_box.pack(anchor="w")

        btn_catalog = tk.Button(
            btn_box,
            text="🚀 Browse Quizzes (Alt+Q)",
            font=("Segoe UI", 10, "bold"),
            bg=THEME_COLOR_ACCENT,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            command=lambda: self._navigate("quizzes")
        )
        btn_catalog.pack(side=tk.LEFT, padx=(0, 10))

        btn_reports = tk.Button(
            btn_box,
            text="📊 Historical Reports (Alt+R)",
            font=("Segoe UI", 10, "bold"),
            bg=THEME_COLOR_PRIMARY,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            command=lambda: self._navigate("reports")
        )
        btn_reports.pack(side=tk.LEFT)

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
            self.btn_toggle_view.config(text="👥 Switch to Cohort View", bg="#475569")
            mode_desc = f"👤 Personal Dashboard ({user['username'] if user else 'Student'})"
        else:
            self.card_quizzes._title_label.config(text="TOTAL ACTIVE QUIZZES")
            self.card_questions._title_label.config(text="QUESTION BANK SIZE")
            self.card_attempts._title_label.config(text="TOTAL SUBMISSIONS (ALL)")
            self.card_avg_score._title_label.config(text="COHORT AVERAGE SCORE")
            self.card_pass_rate._title_label.config(text="OVERALL PASS RATE")
            self.card_latency._title_label.config(text="AVG SUBMISSION LATENCY")
            self.btn_toggle_view.config(text="👤 Switch to My Scores", bg="#2563EB")
            mode_desc = "👑 Institutional Cohort Dashboard (All Students)"

        self.card_quizzes._value_label.config(text=str(metrics["total_quizzes"]))
        self.card_questions._value_label.config(text=str(metrics["total_questions"]))
        self.card_attempts._value_label.config(text=str(metrics["total_attempts"]))
        self.card_avg_score._value_label.config(text=f"{metrics['average_score']}%")
        self.card_pass_rate._value_label.config(text=f"{metrics['pass_rate_percent']}%")
        self.card_latency._value_label.config(text=f"{metrics['avg_submission_latency_ms']} ms")

        cache_mode = "⚡ Cache HIT (In-Memory RAM)" if is_hit else "💾 Cache MISS (Computed from SQLite)"
        sla_pass = latency_ms <= SLA_MAX_CACHE_READ_MS
        status_tag = "[SLA PASS]" if sla_pass else "[SLA DEFECT]"

        self.lbl_cache_status.config(
            text=f"{mode_desc} | {cache_mode} | Response: {latency_ms:.3f} ms {status_tag} (USL: ≤ {SLA_MAX_CACHE_READ_MS} ms)",
            fg=THEME_COLOR_SUCCESS if sla_pass else THEME_COLOR_WARNING
        )

    def _navigate(self, view_name: str) -> None:
        if self.on_navigate:
            self.on_navigate(view_name)

    def update_role_view(self) -> None:
        """Update audit button styling and view mode based on user role."""
        user = self.get_current_user() if self.get_current_user else None
        if not user or not hasattr(self, "btn_audit"):
            return
        if user.get("role") == "ADMIN":
            self.btn_audit.config(text="📋 Audit Logs (Admin)", bg="#0D9488")
            self.view_mode = "cohort"
        else:
            self.btn_audit.config(text="🔒 Audit Logs (Admin Only)", bg="#64748B")
            self.view_mode = "personal"
        self.refresh_metrics(force=False)

    def _open_audit_modal(self) -> None:
        user = self.get_current_user() if self.get_current_user else None
        if user and user.get("role") != "ADMIN":
            messagebox.showwarning(
                "Access Restricted",
                f"🔒 Confidential Audit Trail!\n\n"
                f"Active User: {user.get('username')} ({user.get('role')})\n\n"
                "System audit logs and error analytics are restricted to ADMINISTRATORS for institutional quality oversight.\n"
                "Please switch to an ADMIN account to view system logs."
            )
            return

        modal = tk.Toplevel(self)
        modal.title("TQM System Audit Trail & Defect Analytics (Traceability)")
        modal.geometry("820x480")
        modal.transient(self)
        modal.grab_set()

        hdr = tk.Frame(modal, bg="#F8FAFC", padx=15, pady=10)
        hdr.pack(fill=tk.X)
        tk.Label(
            hdr,
            text="📋 Institutional Audit Trail & Traceability (Admin View)",
            font=("Segoe UI", 11, "bold"),
            fg=THEME_COLOR_PRIMARY,
            bg="#F8FAFC"
        ).pack(side=tk.LEFT)

        tree_frame = tk.Frame(modal, padx=15, pady=5)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "user", "action", "detail", "latency", "date")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        tree.heading("id", text="ID")
        tree.heading("user", text="User")
        tree.heading("action", text="Action")
        tree.heading("detail", text="Detail")
        tree.heading("latency", text="Latency")
        tree.heading("date", text="Timestamp")

        tree.column("id", width=50, anchor="center")
        tree.column("user", width=100, anchor="w")
        tree.column("action", width=140, anchor="w")
        tree.column("detail", width=280, anchor="w")
        tree.column("latency", width=90, anchor="center")
        tree.column("date", width=140, anchor="center")

        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        logs = LoggerService.get_audit_logs(limit=100)
        for log in logs:
            tree.insert("", tk.END, values=(
                f"#{log['id']}",
                log.get("username") or "system",
                log["action"],
                log["detail"],
                f"{log.get('latency_ms', 0.0):.2f} ms",
                log["created_at"]
            ))

        btn_close = tk.Button(modal, text="Close", font=("Segoe UI", 10), bg="#E2E8F0", padx=15, pady=4, command=modal.destroy)
        btn_close.pack(pady=10)
