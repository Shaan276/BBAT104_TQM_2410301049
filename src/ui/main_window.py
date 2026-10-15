"""
Main Window & Quick Navigation Router (Quality Goal Q05 - Feature 2: Quick Navigation)
Enforces instant view switching with pre-mounted frames and designated keyboard shortcuts.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
from src.ui.dashboard_view import DashboardView
from src.ui.quiz_view import QuizView
from src.ui.reports_view import ReportsView
from src.ui.crud_view import CrudView
from src.modules.auth import AuthService
from src.config import (
    APP_TITLE, APP_GEOMETRY, THEME_COLOR_PRIMARY, THEME_COLOR_ACCENT,
    THEME_COLOR_SUCCESS, THEME_COLOR_BG
)


class MainWindow(tk.Tk):
    """Main application frame integrating all Q05 modules and CRUD operations."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(920, 600)
        self.configure(bg=THEME_COLOR_BG)

        # Active user session
        self.current_user = AuthService.get_user_by_username("piyush") or {
            "id": 2, "username": "piyush", "role": "STUDENT"
        }

        self._apply_styles()
        self._build_header()
        self._build_nav_bar()
        self._build_content_area()
        self._build_status_bar()
        self._bind_keyboard_shortcuts()

        # Initial view
        self.show_view("dashboard")

    def _apply_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=THEME_COLOR_BG)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#E2E8F0")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=24)

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=THEME_COLOR_PRIMARY, padx=20, pady=12)
        header.pack(fill=tk.X)

        lbl_title = tk.Label(
            header,
            text="Online Quiz System — [Q05: Reduce Response Time]",
            font=("Segoe UI", 14, "bold"),
            bg=THEME_COLOR_PRIMARY,
            fg="white"
        )
        lbl_title.pack(side=tk.LEFT)

        meta_text = "BBAT104: Fundamentals of TQM | Piyush Pilkhwal (2410301049) | CSE-A"
        lbl_meta = tk.Label(
            header,
            text=meta_text,
            font=("Segoe UI", 9),
            bg=THEME_COLOR_PRIMARY,
            fg="#94A3B8"
        )
        lbl_meta.pack(side=tk.RIGHT)

    def _build_nav_bar(self) -> None:
        nav = tk.Frame(self, bg="#334155", padx=15, pady=6)
        nav.pack(fill=tk.X)

        self.nav_buttons: Dict[str, tk.Button] = {}

        def make_btn(label: str, view_id: str, shortcut: str) -> tk.Button:
            btn = tk.Button(
                nav,
                text=f"{label} ({shortcut})",
                font=("Segoe UI", 9, "bold"),
                bg="#334155",
                fg="white",
                activebackground=THEME_COLOR_ACCENT,
                activeforeground="white",
                relief=tk.FLAT,
                padx=11,
                pady=4,
                command=lambda: self.show_view(view_id)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.nav_buttons[view_id] = btn
            return btn

        make_btn("📊 Dashboard", "dashboard", "Alt+D")
        make_btn("🚀 Quizzes & Search", "quizzes", "Alt+Q")
        make_btn("🛠️ Manage CRUD", "crud", "Alt+M")
        make_btn("📑 Historical Reports", "reports", "Alt+R")

        # User Switcher Button on the right
        self.btn_user_toggle = tk.Button(
            nav,
            text=f"👤 {self.current_user['username'].upper()} ({self.current_user['role']}) - Switch",
            font=("Segoe UI", 9, "bold"),
            bg="#1E293B",
            fg="#38BDF8",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._toggle_user
        )
        self.btn_user_toggle.pack(side=tk.RIGHT, padx=4)

    def _build_content_area(self) -> None:
        self.content_container = tk.Frame(self, bg=THEME_COLOR_BG)
        self.content_container.pack(fill=tk.BOTH, expand=True)

        # Pre-mount all views for zero-redraw instant swapping (Q05-F2 Quick Navigation)
        self.views = {
            "dashboard": DashboardView(self.content_container, on_navigate=self.show_view),
            "quizzes": QuizView(
                self.content_container,
                get_current_user=lambda: self.current_user,
                on_refresh_dashboard=self._on_quiz_submitted
            ),
            "crud": CrudView(self.content_container, on_data_changed=self._on_crud_updated),
            "reports": ReportsView(self.content_container, on_latency_update=self._update_telemetry_status)
        }

    def _build_status_bar(self) -> None:
        status_bar = tk.Frame(self, bg="#E2E8F0", padx=15, pady=4)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status_user = tk.Label(
            status_bar,
            text=f"Active User: {self.current_user['username']} | Role: {self.current_user['role']}",
            font=("Segoe UI", 9),
            bg="#E2E8F0",
            fg="#334155"
        )
        self.lbl_status_user.pack(side=tk.LEFT)

        lbl_engine = tk.Label(
            status_bar,
            text="Storage: SQLite WAL Mode | 4 B-Tree Indexes Active",
            font=("Segoe UI", 9),
            bg="#E2E8F0",
            fg="#64748B"
        )
        lbl_engine.pack(side=tk.LEFT, padx=30)

        self.lbl_telemetry = tk.Label(
            status_bar,
            text="⚡ Latency Telemetry: Ready [SLA Compliant]",
            font=("Segoe UI", 9, "bold"),
            bg="#E2E8F0",
            fg=THEME_COLOR_SUCCESS
        )
        self.lbl_telemetry.pack(side=tk.RIGHT)

    def _bind_keyboard_shortcuts(self) -> None:
        """Bind Alt+D, Alt+Q, Alt+M, Alt+R, and F5 for Quick Navigation."""
        self.bind("<Alt-d>", lambda e: self.show_view("dashboard"))
        self.bind("<Alt-D>", lambda e: self.show_view("dashboard"))
        self.bind("<Alt-q>", lambda e: self.show_view("quizzes"))
        self.bind("<Alt-Q>", lambda e: self.show_view("quizzes"))
        self.bind("<Alt-m>", lambda e: self.show_view("crud"))
        self.bind("<Alt-M>", lambda e: self.show_view("crud"))
        self.bind("<Alt-r>", lambda e: self.show_view("reports"))
        self.bind("<Alt-R>", lambda e: self.show_view("reports"))
        self.bind("<F5>", lambda e: self._refresh_active_view())

    def show_view(self, view_id: str) -> None:
        """Swap visible frame instantaneously without recreation."""
        if view_id not in self.views:
            return

        for name, frame in self.views.items():
            if name == view_id:
                frame.pack(fill=tk.BOTH, expand=True)
                self.nav_buttons[name].config(bg=THEME_COLOR_ACCENT)
            else:
                frame.pack_forget()
                self.nav_buttons[name].config(bg="#334155")

        self.current_view_id = view_id
        if view_id == "dashboard":
            self.views["dashboard"].refresh_metrics()
        elif view_id == "quizzes":
            self.views["quizzes"].refresh_catalog()
        elif view_id == "crud":
            self.views["crud"].refresh_quizzes()
        elif view_id == "reports":
            self.views["reports"].refresh_reports()

    def _refresh_active_view(self) -> None:
        if hasattr(self, "current_view_id"):
            self.show_view(self.current_view_id)

    def _on_quiz_submitted(self) -> None:
        self.views["dashboard"].refresh_metrics(force=True)
        self.views["reports"].refresh_reports()

    def _on_crud_updated(self) -> None:
        self.views["dashboard"].refresh_metrics(force=True)
        self.views["quizzes"].refresh_catalog()
        self.views["reports"].refresh_reports()

    def _update_telemetry_status(self, latency_ms: float, within_sla: bool) -> None:
        tag = "[SLA PASS]" if within_sla else "[SLA DEFECT]"
        color = THEME_COLOR_SUCCESS if within_sla else "#DC2626"
        self.lbl_telemetry.config(
            text=f"⚡ Last Query Latency: {latency_ms:.2f} ms {tag}",
            fg=color
        )

    def _toggle_user(self) -> None:
        """Switch active user context between Student and Admin."""
        if self.current_user["username"] == "piyush":
            admin = AuthService.get_user_by_username("admin")
            self.current_user = admin or {"id": 1, "username": "admin", "role": "ADMIN"}
        else:
            student = AuthService.get_user_by_username("piyush")
            self.current_user = student or {"id": 2, "username": "piyush", "role": "STUDENT"}

        self.btn_user_toggle.config(
            text=f"👤 {self.current_user['username'].upper()} ({self.current_user['role']}) - Switch"
        )
        self.lbl_status_user.config(
            text=f"Active User: {self.current_user['username']} | Role: {self.current_user['role']}"
        )
        messagebox.showinfo(
            "User Session Switched",
            f"Active session updated to: {self.current_user['username']} ({self.current_user['role']})"
        )
