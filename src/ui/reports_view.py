"""
Paginated Reports View (Quality Goal Q05 - Feature 5: Paginated Reports)
Streams historical attempt records using server-side LIMIT/OFFSET chunking with live latency display.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from src.modules.paginator import ReportPaginator
from src.config import (
    THEME_COLOR_PRIMARY, THEME_COLOR_ACCENT, THEME_COLOR_SUCCESS,
    THEME_COLOR_DANGER, THEME_COLOR_WARNING, DEFAULT_PAGE_SIZE,
    PAGE_SIZE_OPTIONS, SLA_MAX_PAGE_CHUNK_MS
)


class ReportsView(ttk.Frame):
    """Paginated attempt history audit view."""

    def __init__(self, parent: tk.Widget, on_latency_update: Optional[Callable[[float, bool], None]] = None):
        super().__init__(parent)
        self.on_latency_update = on_latency_update
        self.current_page = 1
        self.page_size = DEFAULT_PAGE_SIZE

        self._build_ui()
        self.refresh_reports()

    def _build_ui(self) -> None:
        # Filter & Page Size Header
        header = tk.Frame(self, bg="white", pady=10, padx=15)
        header.pack(fill=tk.X)

        tk.Label(header, text="Filter Student:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_user = tk.Entry(header, font=("Segoe UI", 10), width=20, bd=1, relief=tk.SOLID)
        self.entry_user.pack(side=tk.LEFT, padx=(0, 15))
        self.entry_user.bind("<KeyRelease>", lambda e: self._reset_page_and_refresh())

        tk.Label(header, text="Rows per page:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_size = ttk.Combobox(header, values=PAGE_SIZE_OPTIONS, state="readonly", width=6)
        self.combo_size.set(str(self.page_size))
        self.combo_size.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_size.bind("<<ComboboxSelected>>", self._on_change_page_size)

        btn_apply = tk.Button(
            header, text="Apply Filter", font=("Segoe UI", 9, "bold"),
            bg=THEME_COLOR_PRIMARY, fg="white", relief=tk.FLAT, padx=10,
            command=self._reset_page_and_refresh
        )
        btn_apply.pack(side=tk.LEFT)

        # SLA Benchmark Telemetry Bar
        self.lbl_telemetry = tk.Label(
            self,
            text=f"⚡ Paginated Chunk Latency: 0.0 ms (USL: ≤ {SLA_MAX_PAGE_CHUNK_MS} ms)",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg=THEME_COLOR_ACCENT,
            padx=10,
            pady=4
        )
        self.lbl_telemetry.pack(fill=tk.X, padx=15, pady=(0, 8))

        # Records Treeview
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        cols = ("id", "username", "quiz", "score", "status", "latency", "date")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("id", text="Attempt ID")
        self.tree.heading("username", text="Student")
        self.tree.heading("quiz", text="Quiz Title")
        self.tree.heading("score", text="Score (%)")
        self.tree.heading("status", text="Result")
        self.tree.heading("latency", text="Submission Latency")
        self.tree.heading("date", text="Attempt Timestamp")

        self.tree.column("id", width=80, anchor="center")
        self.tree.column("username", width=120, anchor="w")
        self.tree.column("quiz", width=260, anchor="w")
        self.tree.column("score", width=100, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("latency", width=140, anchor="center")
        self.tree.column("date", width=160, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pagination Footer Controls
        footer = tk.Frame(self, bg="white", pady=10, padx=15)
        footer.pack(fill=tk.X)

        self.btn_first = tk.Button(
            footer, text="⏮ First", font=("Segoe UI", 9), bg=THEME_COLOR_PRIMARY, fg="white",
            relief=tk.FLAT, padx=8, command=self._go_first
        )
        self.btn_first.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_prev = tk.Button(
            footer, text="◀ Prev", font=("Segoe UI", 9), bg=THEME_COLOR_PRIMARY, fg="white",
            relief=tk.FLAT, padx=8, command=self._go_prev
        )
        self.btn_prev.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_page_info = tk.Label(
            footer, text="Page 1 of 1 (0 records)", font=("Segoe UI", 10, "bold"), bg="white", fg="#475569"
        )
        self.lbl_page_info.pack(side=tk.LEFT, padx=10)

        self.btn_next = tk.Button(
            footer, text="Next ▶", font=("Segoe UI", 9), bg=THEME_COLOR_PRIMARY, fg="white",
            relief=tk.FLAT, padx=8, command=self._go_next
        )
        self.btn_next.pack(side=tk.LEFT, padx=(10, 5))

        self.btn_last = tk.Button(
            footer, text="Last ⏭", font=("Segoe UI", 9), bg=THEME_COLOR_PRIMARY, fg="white",
            relief=tk.FLAT, padx=8, command=self._go_last
        )
        self.btn_last.pack(side=tk.LEFT)

    def refresh_reports(self) -> None:
        """Fetch chunked records and update latency badge."""
        query_user = self.entry_user.get()
        data = ReportPaginator.get_paginated_attempts(
            page=self.current_page,
            page_size=self.page_size,
            username_query=query_user
        )

        self.tree.delete(*self.tree.get_children())
        for r in data["records"]:
            self.tree.insert("", tk.END, values=(
                f"#{r['id']}",
                r["username"],
                r["quiz_title"],
                f"{r['score_percentage']}% ({r['correct_answers']}/{r['total_questions']})",
                r["status"],
                f"{r['latency_ms']:.2f} ms",
                r["created_at"]
            ))

        self.current_page = data["page"]
        total_pages = data["total_pages"]
        total_records = data["total_records"]
        self.total_pages = total_pages

        self.lbl_page_info.config(
            text=f"Page {self.current_page} of {total_pages} (Total {total_records} records)"
        )

        self.btn_first.config(state=tk.NORMAL if data["has_prev"] else tk.DISABLED)
        self.btn_prev.config(state=tk.NORMAL if data["has_prev"] else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if data["has_next"] else tk.DISABLED)
        self.btn_last.config(state=tk.NORMAL if data["has_next"] else tk.DISABLED)

        status_tag = "[SLA PASS]" if data["within_sla"] else "[SLA DEFECT]"
        color = THEME_COLOR_SUCCESS if data["within_sla"] else THEME_COLOR_DANGER
        self.lbl_telemetry.config(
            text=f"⚡ Paginated Chunk Latency: {data['latency_ms']} ms {status_tag} | LIMIT {self.page_size} (USL: ≤ {SLA_MAX_PAGE_CHUNK_MS} ms)",
            fg=color
        )

        if self.on_latency_update:
            self.on_latency_update(data["latency_ms"], data["within_sla"])

    def _reset_page_and_refresh(self) -> None:
        self.current_page = 1
        self.refresh_reports()

    def _on_change_page_size(self, event=None) -> None:
        try:
            self.page_size = int(self.combo_size.get())
            self._reset_page_and_refresh()
        except ValueError:
            pass

    def _go_first(self) -> None:
        self.current_page = 1
        self.refresh_reports()

    def _go_prev(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_reports()

    def _go_next(self) -> None:
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh_reports()

    def _go_last(self) -> None:
        self.current_page = self.total_pages
        self.refresh_reports()
