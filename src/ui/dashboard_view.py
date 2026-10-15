"""
Dashboard View (Quality Goal Q05 - Feature 3: Cached Dashboard)
Displays high-speed in-memory cached performance metrics and SLA compliance badges.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from src.modules.quiz_crud import QuizCRUD
from src.config import (
    THEME_COLOR_PRIMARY, THEME_COLOR_ACCENT, THEME_COLOR_SUCCESS,
    THEME_COLOR_WARNING, THEME_COLOR_BG, SLA_MAX_CACHE_READ_MS
)


class DashboardView(ttk.Frame):
    """Cached operational metrics dashboard view."""

    def __init__(self, parent: tk.Widget, on_navigate: Optional[Callable[[str], None]] = None):
        super().__init__(parent)
        self.on_navigate = on_navigate
        self._build_ui()

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
        frame._value_label = lbl_v  # Store reference for quick update
        return frame

    def refresh_metrics(self, force: bool = False) -> None:
        """Fetch metrics and update UI labels."""
        metrics, latency_ms, is_hit = QuizCRUD.get_dashboard_metrics(force_refresh=force)
        
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
            text=f"{cache_mode} | Response: {latency_ms:.3f} ms {status_tag} (USL: ≤ {SLA_MAX_CACHE_READ_MS} ms)",
            fg=THEME_COLOR_SUCCESS if sla_pass else THEME_COLOR_WARNING
        )

    def _navigate(self, view_name: str) -> None:
        if self.on_navigate:
            self.on_navigate(view_name)
