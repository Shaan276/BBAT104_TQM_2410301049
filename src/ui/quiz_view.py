"""
Quiz Catalog & Execution View (Quality Goal Q05 - Features 1 & 2)
Provides Fast Search across quizzes and zero-latency active test taking with timer countdown.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List, Callable
from src.modules.fast_search import FastSearchEngine
from src.modules.quiz_crud import QuizCRUD
from src.modules.quiz_engine import QuizEngine
from src.config import (
    THEME_COLOR_PRIMARY, THEME_COLOR_ACCENT, THEME_COLOR_SUCCESS,
    THEME_COLOR_DANGER, THEME_COLOR_WARNING, SLA_MAX_SEARCH_LATENCY_MS,
    SLA_MAX_LOAD_QUIZ_LATENCY_MS
)


class QuizView(ttk.Frame):
    """Integrated view for Quiz Discovery (Fast Search) and Quiz Taking."""

    def __init__(self, parent: tk.Widget, get_current_user: Callable[[], Dict[str, Any]], on_refresh_dashboard: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.get_current_user = get_current_user
        self.on_refresh_dashboard = on_refresh_dashboard

        # Active session state
        self.active_quiz: Optional[Dict[str, Any]] = None
        self.active_questions: List[Dict[str, Any]] = []
        self.current_q_index = 0
        self.user_answers: Dict[int, str] = {}
        self.time_remaining_seconds = 0
        self.timer_after_id: Optional[str] = None
        self.is_submitting = False

        self._build_ui()
        self.refresh_catalog()

    def _build_ui(self) -> None:
        # Container frames: Catalog Mode vs Quiz Taking Mode
        self.catalog_frame = tk.Frame(self, bg="white")
        self.quiz_taking_frame = tk.Frame(self, bg="white")

        self.catalog_frame.pack(fill=tk.BOTH, expand=True)

        self._build_catalog_ui()
        self._build_quiz_taking_ui()

    # -------------------------------------------------------------
    # 1. Catalog Mode (Fast Search)
    # -------------------------------------------------------------
    def _build_catalog_ui(self) -> None:
        # Search & Filter Header
        header = tk.Frame(self.catalog_frame, bg="white", pady=10, padx=15)
        header.pack(fill=tk.X)

        tk.Label(header, text="🔍 Fast Search:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_search = tk.Entry(header, font=("Segoe UI", 10), width=28, bd=1, relief=tk.SOLID)
        self.entry_search.pack(side=tk.LEFT, padx=(0, 15))
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_catalog())

        tk.Label(header, text="Category:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_category = ttk.Combobox(header, state="readonly", width=20)
        self.combo_category.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_category.bind("<<ComboboxSelected>>", lambda e: self.refresh_catalog())

        self.btn_search = tk.Button(
            header,
            text="Filter",
            font=("Segoe UI", 9, "bold"),
            bg=THEME_COLOR_PRIMARY,
            fg="white",
            relief=tk.FLAT,
            padx=10,
            command=self.refresh_catalog
        )
        self.btn_search.pack(side=tk.LEFT)

        # Sort Dropdown Option (Issue 2 - img2)
        tk.Label(header, text="Sort By:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=(12, 5))
        self.combo_sort = ttk.Combobox(
            header,
            values=[
                "ID (Low-High)", "ID (High-Low)",
                "Title (A-Z)", "Title (Z-A)",
                "Category (A-Z)",
                "Duration (Short-Long)", "Duration (Long-Short)",
                "Passing Score (Low-High)", "Passing Score (High-Low)"
            ],
            state="readonly",
            width=20
        )
        self.combo_sort.set("ID (Low-High)")
        self.combo_sort.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_sort.bind("<<ComboboxSelected>>", lambda e: self.refresh_catalog())

        # SLA Benchmarking Pill
        self.lbl_search_latency = tk.Label(
            self.catalog_frame,
            text=f"⚡ Indexed Search Latency: 0.0 ms (USL: ≤ {SLA_MAX_SEARCH_LATENCY_MS} ms)",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg=THEME_COLOR_ACCENT,
            padx=10,
            pady=4
        )
        self.lbl_search_latency.pack(fill=tk.X, padx=15, pady=(0, 8))

        # Treeview Catalog with Clickable Sort Headers
        tree_frame = tk.Frame(self.catalog_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        cols = ("id", "title", "category", "duration", "pass_score")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID ▲▼", command=lambda: self._sort_by_column("id"))
        self.tree.heading("title", text="Quiz Title ▲▼", command=lambda: self._sort_by_column("title"))
        self.tree.heading("category", text="Category ▲▼", command=lambda: self._sort_by_column("category"))
        self.tree.heading("duration", text="Duration (Min) ▲▼", command=lambda: self._sort_by_column("duration"))
        self.tree.heading("pass_score", text="Passing Score (%) ▲▼", command=lambda: self._sort_by_column("pass_score"))

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("title", width=340, anchor="w")
        self.tree.column("category", width=180, anchor="w")
        self.tree.column("duration", width=110, anchor="center")
        self.tree.column("pass_score", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom Action Bar
        actions_bar = tk.Frame(self.catalog_frame, bg="white", pady=10, padx=15)
        actions_bar.pack(fill=tk.X)

        self.btn_start = tk.Button(
            actions_bar,
            text="▶ Start Selected Quiz",
            font=("Segoe UI", 10, "bold"),
            bg=THEME_COLOR_SUCCESS,
            fg="white",
            relief=tk.FLAT,
            padx=18,
            pady=6,
            command=self._start_quiz_action
        )
        self.btn_start.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_add_quiz = tk.Button(
            actions_bar,
            text="➕ New Quiz / Add Question",
            font=("Segoe UI", 9, "bold"),
            bg=THEME_COLOR_PRIMARY,
            fg="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            command=self._show_new_quiz_modal
        )
        self.btn_add_quiz.pack(side=tk.LEFT)

    def _sort_by_column(self, col: str) -> None:
        """Toggle column sort order upon header click."""
        curr_dir = getattr(self, f"_sort_dir_{col}", "asc")
        new_dir = "desc" if curr_dir == "asc" else "asc"
        setattr(self, f"_sort_dir_{col}", new_dir)

        mapping = {
            "id": "ID (Low-High)" if new_dir == "asc" else "ID (High-Low)",
            "title": "Title (A-Z)" if new_dir == "asc" else "Title (Z-A)",
            "category": "Category (A-Z)",
            "duration": "Duration (Short-Long)" if new_dir == "asc" else "Duration (Long-Short)",
            "pass_score": "Passing Score (Low-High)" if new_dir == "asc" else "Passing Score (High-Low)",
        }
        if col in mapping:
            self.combo_sort.set(mapping[col])
            self.refresh_catalog()

    def refresh_catalog(self) -> None:
        """Fetch filtered quizzes and display search latency."""
        query = self.entry_search.get()
        cat = self.combo_category.get()
        sort_by = self.combo_sort.get() if hasattr(self, "combo_sort") else "id_asc"

        categories = ["All"] + QuizCRUD.get_categories()
        self.combo_category["values"] = categories
        if not self.combo_category.get():
            self.combo_category.set("All")

        rows, latency_ms, within_sla = FastSearchEngine.search_quizzes(query, cat, sort_by=sort_by)

        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["id"], r["title"], r["category"],
                f"{r['duration_minutes']} min", f"{r['passing_score']}%"
            ))

        status_tag = "[SLA PASS]" if within_sla else "[SLA DEFECT]"
        color = THEME_COLOR_SUCCESS if within_sla else THEME_COLOR_DANGER
        self.lbl_search_latency.config(
            text=f"⚡ Indexed Search Latency: {latency_ms:.3f} ms {status_tag} | Records Found: {len(rows)} (USL: ≤ {SLA_MAX_SEARCH_LATENCY_MS} ms)",
            fg=color
        )

    # -------------------------------------------------------------
    # 2. Quiz Taking Mode (Zero Latency Execution)
    # -------------------------------------------------------------
    def _build_quiz_taking_ui(self) -> None:
        # Quiz Header with Timer
        q_header = tk.Frame(self.quiz_taking_frame, bg=THEME_COLOR_PRIMARY, padx=15, pady=10)
        q_header.pack(fill=tk.X)

        self.lbl_active_title = tk.Label(
            q_header, text="Quiz Title", font=("Segoe UI", 12, "bold"), bg=THEME_COLOR_PRIMARY, fg="white"
        )
        self.lbl_active_title.pack(side=tk.LEFT)

        self.lbl_timer = tk.Label(
            q_header, text="⏱ 00:00", font=("Segoe UI", 14, "bold"), bg=THEME_COLOR_PRIMARY, fg="#FBBF24"
        )
        self.lbl_timer.pack(side=tk.RIGHT)

        # Question Navigation Breadcrumb
        self.lbl_q_progress = tk.Label(
            self.quiz_taking_frame, text="Question 1 of 5", font=("Segoe UI", 10, "bold"),
            bg="#F8FAFC", fg="#64748B", pady=6
        )
        self.lbl_q_progress.pack(fill=tk.X)

        # Question Content Card
        q_card = tk.Frame(self.quiz_taking_frame, bg="white", padx=25, pady=15)
        q_card.pack(fill=tk.BOTH, expand=True)

        self.lbl_question_text = tk.Label(
            q_card, text="Question prompt goes here?", font=("Segoe UI", 11, "bold"),
            bg="white", fg=THEME_COLOR_PRIMARY, wraplength=700, justify=tk.LEFT
        )
        self.lbl_question_text.pack(anchor="w", pady=(5, 15))

        self.var_option = tk.StringVar(value="")

        # Poka-Yoke: Set tristatevalue="UNSET" to prevent all radiobuttons from defaulting to selected
        self.radio_opts = []
        for opt_key in ("A", "B", "C", "D"):
            rb = tk.Radiobutton(
                q_card,
                text=f"Option {opt_key}",
                variable=self.var_option,
                value=opt_key,
                tristatevalue="UNSET",
                font=("Segoe UI", 10),
                bg="white",
                activebackground="white",
                command=self._on_select_option
            )
            rb.pack(anchor="w", pady=4, padx=10)
            self.radio_opts.append(rb)

        # Navigation Bar
        nav_frame = tk.Frame(self.quiz_taking_frame, bg="white", padx=20, pady=15)
        nav_frame.pack(fill=tk.X)

        self.btn_prev = tk.Button(
            nav_frame, text="◀ Previous", font=("Segoe UI", 9, "bold"),
            bg=THEME_COLOR_PRIMARY, fg="white", relief=tk.FLAT, padx=12, pady=5,
            command=self._prev_question
        )
        self.btn_prev.pack(side=tk.LEFT)

        self.btn_next = tk.Button(
            nav_frame, text="Next ▶", font=("Segoe UI", 9, "bold"),
            bg=THEME_COLOR_PRIMARY, fg="white", relief=tk.FLAT, padx=12, pady=5,
            command=self._next_question
        )
        self.btn_next.pack(side=tk.LEFT, padx=10)

        self.btn_submit = tk.Button(
            nav_frame, text="✓ Submit Assessment", font=("Segoe UI", 10, "bold"),
            bg=THEME_COLOR_SUCCESS, fg="white", relief=tk.FLAT, padx=18, pady=5,
            command=self._submit_quiz_action
        )
        self.btn_submit.pack(side=tk.RIGHT)

        self.btn_cancel = tk.Button(
            nav_frame, text="Cancel / Exit", font=("Segoe UI", 9),
            bg="#94A3B8", fg="white", relief=tk.FLAT, padx=10, pady=5,
            command=self._exit_quiz_taking
        )
        self.btn_cancel.pack(side=tk.RIGHT, padx=10)

    # -------------------------------------------------------------
    # Session Execution Logic
    # -------------------------------------------------------------
    def _start_quiz_action(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Quiz", "Please select a quiz from the list to start.")
            return

        quiz_id = int(self.tree.item(selected[0])["values"][0])
        quiz_info, questions, latency_ms, within_sla = QuizEngine.load_quiz_session(quiz_id)

        if not questions:
            messagebox.showinfo("Empty Quiz", "This quiz does not have any questions authored yet.")
            return

        self.active_quiz = quiz_info
        self.active_questions = questions
        self.current_q_index = 0
        self.user_answers = {}
        self.is_submitting = False
        self.time_remaining_seconds = quiz_info["duration_minutes"] * 60

        # Switch to Quiz Taking Mode
        self.catalog_frame.pack_forget()
        self.quiz_taking_frame.pack(fill=tk.BOTH, expand=True)

        self.lbl_active_title.config(text=f"{quiz_info['title']} ({quiz_info['category']})")
        self._render_current_question()
        self._start_timer()

    def _render_current_question(self) -> None:
        q = self.active_questions[self.current_q_index]
        total_q = len(self.active_questions)

        self.lbl_q_progress.config(text=f"Question {self.current_q_index + 1} of {total_q} | Marks: {q['marks']}")
        self.lbl_question_text.config(text=f"Q{self.current_q_index + 1}. {q['question_text']}")

        # Set option text
        self.radio_opts[0].config(text=f"A) {q['option_a']}")
        self.radio_opts[1].config(text=f"B) {q['option_b']}")
        self.radio_opts[2].config(text=f"C) {q['option_c']}")
        self.radio_opts[3].config(text=f"D) {q['option_d']}")

        # Restore previously marked answer
        q_id = q["id"]
        self.var_option.set(self.user_answers.get(q_id, ""))

        # Button states
        self.btn_prev.config(state=tk.NORMAL if self.current_q_index > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_q_index < total_q - 1 else tk.DISABLED)

    def _on_select_option(self) -> None:
        if not self.active_questions:
            return
        q_id = self.active_questions[self.current_q_index]["id"]
        self.user_answers[q_id] = self.var_option.get()

    def _prev_question(self) -> None:
        if self.current_q_index > 0:
            self.current_q_index -= 1
            self._render_current_question()

    def _next_question(self) -> None:
        if self.current_q_index < len(self.active_questions) - 1:
            self.current_q_index += 1
            self._render_current_question()

    def _start_timer(self) -> None:
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
        self._tick_timer()

    def _tick_timer(self) -> None:
        if self.time_remaining_seconds <= 0:
            self.lbl_timer.config(text="⏱ 00:00")
            messagebox.showinfo("Time Expired", "Assessment time limit reached! Auto-submitting answers now.")
            self._submit_quiz_action(forced=True)
            return

        mins = self.time_remaining_seconds // 60
        secs = self.time_remaining_seconds % 60
        self.lbl_timer.config(text=f"⏱ {mins:02d}:{secs:02d}")
        self.time_remaining_seconds -= 1
        self.timer_after_id = self.after(1000, self._tick_timer)

    def _submit_quiz_action(self, forced: bool = False) -> None:
        # Poka-Yoke: Intercept double submission
        if self.is_submitting:
            return

        if not forced:
            unanswered = len(self.active_questions) - len(self.user_answers)
            if unanswered > 0:
                confirm = messagebox.askyesno(
                    "Unanswered Questions",
                    f"You have {unanswered} unanswered question(s).\nDo you want to proceed and submit anyway?"
                )
                if not confirm:
                    return

        self.is_submitting = True
        self.btn_submit.config(state=tk.DISABLED, text="Processing...")
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)

        user = self.get_current_user()
        summary, latency_ms, within_sla = QuizEngine.submit_attempt(
            self.active_quiz["id"], user["id"], self.user_answers
        )

        if self.on_refresh_dashboard:
            self.on_refresh_dashboard()

        # Display result dialog
        status_color = "green" if summary["status"] == "PASSED" else "red"
        sla_tag = "PASS" if within_sla else "DEFECT"
        res_msg = (
            f"Assessment: {summary['quiz_title']}\n"
            f"Status: {summary['status']}\n"
            f"Score: {summary['score_percentage']}% ({summary['correct_answers']}/{summary['total_questions']} correct)\n"
            f"Passing Threshold: {summary['passing_score']}%\n\n"
            f"⚡ Transaction Latency: {latency_ms:.3f} ms [SLA {sla_tag}]\n"
            f"Upper Specification Limit (USL): ≤ {summary['sla_limit_ms']} ms"
        )
        messagebox.showinfo("Quiz Results", res_msg)

        self._exit_quiz_taking()

    def _exit_quiz_taking(self) -> None:
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.active_quiz = None
        self.active_questions = []
        self.btn_submit.config(state=tk.NORMAL, text="✓ Submit Assessment")
        self.quiz_taking_frame.pack_forget()
        self.catalog_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_catalog()

    # -------------------------------------------------------------
    # 3. Quick Creation Modal
    # -------------------------------------------------------------
    def _show_new_quiz_modal(self) -> None:
        modal = tk.Toplevel(self)
        modal.title("Create New Quiz (Poka-Yoke Form)")
        modal.geometry("450x380")
        modal.transient(self)
        modal.grab_set()

        tk.Label(modal, text="Create New Assessment", font=("Segoe UI", 11, "bold"), fg=THEME_COLOR_PRIMARY).pack(pady=10)

        form = tk.Frame(modal, padx=20)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Quiz Title:").grid(row=0, column=0, sticky="w", pady=4)
        e_title = tk.Entry(form, width=30)
        e_title.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Category:").grid(row=1, column=0, sticky="w", pady=4)
        e_cat = tk.Entry(form, width=30)
        e_cat.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Duration (Minutes):").grid(row=2, column=0, sticky="w", pady=4)
        e_dur = tk.Entry(form, width=30)
        e_dur.insert(0, "10")
        e_dur.grid(row=2, column=1, pady=4)

        tk.Label(form, text="Passing Score (%):").grid(row=3, column=0, sticky="w", pady=4)
        e_pass = tk.Entry(form, width=30)
        e_pass.insert(0, "60")
        e_pass.grid(row=3, column=1, pady=4)

        def save() -> None:
            title = e_title.get()
            cat = e_cat.get()
            try:
                dur = int(e_dur.get())
                pas = int(e_pass.get())
                qid = QuizCRUD.create_quiz(title, cat, dur, pas)
                messagebox.showinfo("Success", f"Quiz '{title}' created successfully (ID: {qid})!")
                modal.destroy()
                self.refresh_catalog()
                if self.on_refresh_dashboard:
                    self.on_refresh_dashboard()
            except Exception as err:
                messagebox.showerror("Error", f"Failed to create quiz: {err}")

        btn_save = tk.Button(modal, text="Save Quiz", font=("Segoe UI", 10, "bold"), bg=THEME_COLOR_PRIMARY, fg="white", command=save)
        btn_save.pack(pady=15)
