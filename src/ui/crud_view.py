"""
CRUD Management View (Base System & Question Bank Authoring)
Enables full Create, Read, Update, and Delete operations for Quizzes and Questions.
Includes strict Poka-Yoke validation to prevent malformed data entry.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from src.modules.quiz_crud import QuizCRUD
from src.config import (
    THEME_COLOR_PRIMARY, THEME_COLOR_ACCENT, THEME_COLOR_SUCCESS,
    THEME_COLOR_DANGER, THEME_COLOR_WARNING
)


class CrudView(ttk.Frame):
    """Teacher / Admin CRUD Management View for Quizzes & Questions."""

    def __init__(self, parent: tk.Widget, on_data_changed: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.on_data_changed = on_data_changed
        self.selected_quiz_id: Optional[int] = None

        self._build_ui()
        self.refresh_quizzes()

    def _build_ui(self) -> None:
        self.configure(style="TFrame")

        # Top Information Banner
        banner = tk.Frame(self, bg="#F1F5F9", padx=15, pady=8, bd=1, relief=tk.SOLID)
        banner.pack(fill=tk.X, padx=15, pady=(10, 5))

        lbl_info = tk.Label(
            banner,
            text="🛠️ Question Bank & Assessment CRUD Center (Review 2 Deliverable | CO1 & CO2)",
            font=("Segoe UI", 10, "bold"),
            bg="#F1F5F9",
            fg=THEME_COLOR_PRIMARY
        )
        lbl_info.pack(side=tk.LEFT)

        lbl_poka = tk.Label(
            banner,
            text="🔒 Poka-Yoke Guard Active: Auto-validates keys & cascade constraints",
            font=("Segoe UI", 9),
            bg="#F1F5F9",
            fg=THEME_COLOR_SUCCESS
        )
        lbl_poka.pack(side=tk.RIGHT)

        # Split Paned Window: Left = Quizzes, Right = Questions
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#CBD5E1", sashwidth=4)
        paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # ---------------------------------------------------------
        # Left Panel: Quiz Management
        # ---------------------------------------------------------
        left_frame = tk.Frame(paned, bg="white", padx=10, pady=10)
        paned.add(left_frame, minsize=320, width=380)

        lbl_quiz_hdr = tk.Label(
            left_frame, text="1. Assessments (Quizzes)", font=("Segoe UI", 11, "bold"),
            bg="white", fg=THEME_COLOR_PRIMARY
        )
        lbl_quiz_hdr.pack(anchor="w", pady=(0, 5))

        quiz_tree_frame = tk.Frame(left_frame)
        quiz_tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.quiz_tree = ttk.Treeview(quiz_tree_frame, columns=("id", "title", "cat"), show="headings", selectmode="browse")
        self.quiz_tree.heading("id", text="ID")
        self.quiz_tree.heading("title", text="Quiz Title")
        self.quiz_tree.heading("cat", text="Category")
        self.quiz_tree.column("id", width=40, anchor="center")
        self.quiz_tree.column("title", width=180, anchor="w")
        self.quiz_tree.column("cat", width=110, anchor="w")

        q_scroll = ttk.Scrollbar(quiz_tree_frame, orient=tk.VERTICAL, command=self.quiz_tree.yview)
        self.quiz_tree.configure(yscrollcommand=q_scroll.set)
        self.quiz_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        q_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.quiz_tree.bind("<<TreeviewSelect>>", self._on_quiz_selected)

        # Quiz Action Buttons
        quiz_btn_box = tk.Frame(left_frame, bg="white")
        quiz_btn_box.pack(fill=tk.X, pady=(10, 0))

        btn_add_quiz = tk.Button(
            quiz_btn_box, text="➕ Add Quiz", font=("Segoe UI", 9, "bold"),
            bg=THEME_COLOR_PRIMARY, fg="white", relief=tk.FLAT, padx=8, pady=4,
            command=self._modal_add_quiz
        )
        btn_add_quiz.pack(side=tk.LEFT, padx=(0, 4))

        btn_edit_quiz = tk.Button(
            quiz_btn_box, text="✏️ Edit", font=("Segoe UI", 9),
            bg="#475569", fg="white", relief=tk.FLAT, padx=8, pady=4,
            command=self._modal_edit_quiz
        )
        btn_edit_quiz.pack(side=tk.LEFT, padx=4)

        btn_del_quiz = tk.Button(
            quiz_btn_box, text="🗑️ Delete", font=("Segoe UI", 9),
            bg=THEME_COLOR_DANGER, fg="white", relief=tk.FLAT, padx=8, pady=4,
            command=self._action_delete_quiz
        )
        btn_del_quiz.pack(side=tk.LEFT, padx=4)

        # ---------------------------------------------------------
        # Right Panel: Question Bank Management
        # ---------------------------------------------------------
        right_frame = tk.Frame(paned, bg="white", padx=10, pady=10)
        paned.add(right_frame, minsize=420)

        self.lbl_question_hdr = tk.Label(
            right_frame, text="2. Question Bank (Select a Quiz to View)", font=("Segoe UI", 11, "bold"),
            bg="white", fg=THEME_COLOR_PRIMARY
        )
        self.lbl_question_hdr.pack(anchor="w", pady=(0, 5))

        quest_tree_frame = tk.Frame(right_frame)
        quest_tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.quest_tree = ttk.Treeview(
            quest_tree_frame,
            columns=("id", "text", "correct", "marks"),
            show="headings",
            selectmode="browse"
        )
        self.quest_tree.heading("id", text="ID")
        self.quest_tree.heading("text", text="Question Prompt")
        self.quest_tree.heading("correct", text="Key")
        self.quest_tree.heading("marks", text="Marks")
        self.quest_tree.column("id", width=40, anchor="center")
        self.quest_tree.column("text", width=330, anchor="w")
        self.quest_tree.column("correct", width=50, anchor="center")
        self.quest_tree.column("marks", width=50, anchor="center")

        quest_scroll = ttk.Scrollbar(quest_tree_frame, orient=tk.VERTICAL, command=self.quest_tree.yview)
        self.quest_tree.configure(yscrollcommand=quest_scroll.set)
        self.quest_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        quest_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Question Action Buttons
        quest_btn_box = tk.Frame(right_frame, bg="white")
        quest_btn_box.pack(fill=tk.X, pady=(10, 0))

        self.btn_add_quest = tk.Button(
            quest_btn_box, text="➕ Add Question", font=("Segoe UI", 9, "bold"),
            bg=THEME_COLOR_SUCCESS, fg="white", relief=tk.FLAT, padx=10, pady=4,
            command=self._modal_add_question, state=tk.DISABLED
        )
        self.btn_add_quest.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_edit_quest = tk.Button(
            quest_btn_box, text="✏️ Edit Question", font=("Segoe UI", 9),
            bg="#475569", fg="white", relief=tk.FLAT, padx=8, pady=4,
            command=self._modal_edit_question, state=tk.DISABLED
        )
        self.btn_edit_quest.pack(side=tk.LEFT, padx=4)

        self.btn_del_quest = tk.Button(
            quest_btn_box, text="🗑️ Delete Question", font=("Segoe UI", 9),
            bg=THEME_COLOR_DANGER, fg="white", relief=tk.FLAT, padx=8, pady=4,
            command=self._action_delete_question, state=tk.DISABLED
        )
        self.btn_del_quest.pack(side=tk.LEFT, padx=4)

    # ---------------------------------------------------------
    # Quiz Data Handling
    # ---------------------------------------------------------
    def refresh_quizzes(self) -> None:
        """Fetch and render all quizzes."""
        quizzes = QuizCRUD.get_quizzes()
        self.quiz_tree.delete(*self.quiz_tree.get_children())
        for q in quizzes:
            self.quiz_tree.insert("", tk.END, values=(q["id"], q["title"], q["category"]))

        # Clear questions tree
        self.quest_tree.delete(*self.quest_tree.get_children())
        self.selected_quiz_id = None
        self.lbl_question_hdr.config(text="2. Question Bank (Select a Quiz to View)")
        self.btn_add_quest.config(state=tk.DISABLED)
        self.btn_edit_quest.config(state=tk.DISABLED)
        self.btn_del_quest.config(state=tk.DISABLED)

    def _on_quiz_selected(self, event=None) -> None:
        selected = self.quiz_tree.selection()
        if not selected:
            return
        item = self.quiz_tree.item(selected[0])
        quiz_id = int(item["values"][0])
        quiz_title = item["values"][1]
        self.selected_quiz_id = quiz_id

        self.lbl_question_hdr.config(text=f"2. Questions for: '{quiz_title}' (Quiz #{quiz_id})")
        self.btn_add_quest.config(state=tk.NORMAL)
        self.btn_edit_quest.config(state=tk.NORMAL)
        self.btn_del_quest.config(state=tk.NORMAL)

        self.refresh_questions()

    def refresh_questions(self) -> None:
        """Fetch and render questions for selected quiz."""
        if not self.selected_quiz_id:
            return
        questions = QuizCRUD.get_questions_by_quiz(self.selected_quiz_id)
        self.quest_tree.delete(*self.quest_tree.get_children())
        for q in questions:
            self.quest_tree.insert("", tk.END, values=(
                q["id"], q["question_text"], q["correct_option"], q["marks"]
            ))

    # ---------------------------------------------------------
    # Modals: Quiz CRUD
    # ---------------------------------------------------------
    def _modal_add_quiz(self) -> None:
        self._quiz_form_dialog("Add New Quiz", None)

    def _modal_edit_quiz(self) -> None:
        selected = self.quiz_tree.selection()
        if not selected:
            messagebox.showwarning("Select Quiz", "Please select a quiz to edit.")
            return
        quiz_id = int(self.quiz_tree.item(selected[0])["values"][0])
        quiz = QuizCRUD.get_quiz_by_id(quiz_id)
        if quiz:
            self._quiz_form_dialog("Edit Quiz", quiz)

    def _quiz_form_dialog(self, title_text: str, existing_quiz: Optional[dict]) -> None:
        modal = tk.Toplevel(self)
        modal.title(title_text)
        modal.geometry("450x340")
        modal.transient(self)
        modal.grab_set()

        form = tk.Frame(modal, padx=25, pady=20)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Title:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=6)
        e_title = tk.Entry(form, width=32)
        e_title.grid(row=0, column=1, pady=6)

        tk.Label(form, text="Category:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=6)
        e_cat = tk.Entry(form, width=32)
        e_cat.grid(row=1, column=1, pady=6)

        tk.Label(form, text="Duration (min):", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=6)
        e_dur = tk.Entry(form, width=32)
        e_dur.grid(row=2, column=1, pady=6)

        tk.Label(form, text="Pass Score (%):", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=6)
        e_pass = tk.Entry(form, width=32)
        e_pass.grid(row=3, column=1, pady=6)

        if existing_quiz:
            e_title.insert(0, existing_quiz["title"])
            e_cat.insert(0, existing_quiz["category"])
            e_dur.insert(0, str(existing_quiz["duration_minutes"]))
            e_pass.insert(0, str(existing_quiz["passing_score"]))
        else:
            e_dur.insert(0, "10")
            e_pass.insert(0, "60")

        def save() -> None:
            title = e_title.get().strip()
            cat = e_cat.get().strip()
            try:
                dur = int(e_dur.get())
                pas = int(e_pass.get())
                if existing_quiz:
                    QuizCRUD.update_quiz(existing_quiz["id"], title, cat, dur, pas)
                    messagebox.showinfo("Success", "Quiz updated successfully!")
                else:
                    QuizCRUD.create_quiz(title, cat, dur, pas)
                    messagebox.showinfo("Success", "Quiz created successfully!")
                modal.destroy()
                self.refresh_quizzes()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as err:
                messagebox.showerror("Validation Error", f"Poka-Yoke Input Rejected: {err}")

        btn_save = tk.Button(form, text="Save Assessment", font=("Segoe UI", 10, "bold"),
                             bg=THEME_COLOR_PRIMARY, fg="white", relief=tk.FLAT, padx=15, pady=5, command=save)
        btn_save.grid(row=4, column=0, columnspan=2, pady=15)

    def _action_delete_quiz(self) -> None:
        selected = self.quiz_tree.selection()
        if not selected:
            messagebox.showwarning("Select Quiz", "Please select a quiz to delete.")
            return
        item = self.quiz_tree.item(selected[0])
        quiz_id = int(item["values"][0])
        quiz_title = item["values"][1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Quiz #{quiz_id} ('{quiz_title}')?\n"
            "This will cascade delete all associated questions and student attempts!"
        )
        if confirm:
            QuizCRUD.delete_quiz(quiz_id)
            messagebox.showinfo("Deleted", "Quiz deleted successfully.")
            self.refresh_quizzes()
            if self.on_data_changed:
                self.on_data_changed()

    # ---------------------------------------------------------
    # Modals: Question CRUD
    # ---------------------------------------------------------
    def _modal_add_question(self) -> None:
        if not self.selected_quiz_id:
            return
        self._question_form_dialog("Add New Question", None)

    def _modal_edit_question(self) -> None:
        selected = self.quest_tree.selection()
        if not selected:
            messagebox.showwarning("Select Question", "Please select a question to edit.")
            return
        q_id = int(self.quest_tree.item(selected[0])["values"][0])
        questions = QuizCRUD.get_questions_by_quiz(self.selected_quiz_id)
        target = next((q for q in questions if q["id"] == q_id), None)
        if target:
            self._question_form_dialog("Edit Question", target)

    def _question_form_dialog(self, title_text: str, existing_q: Optional[dict]) -> None:
        modal = tk.Toplevel(self)
        modal.title(title_text)
        modal.geometry("540x480")
        modal.transient(self)
        modal.grab_set()

        form = tk.Frame(modal, padx=20, pady=15)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Question Prompt:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="nw", pady=4)
        txt_prompt = tk.Text(form, width=38, height=3, font=("Segoe UI", 9), bd=1, relief=tk.SOLID)
        txt_prompt.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Option A:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        e_a = tk.Entry(form, width=42)
        e_a.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Option B:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        e_b = tk.Entry(form, width=42)
        e_b.grid(row=2, column=1, pady=4)

        tk.Label(form, text="Option C:", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        e_c = tk.Entry(form, width=42)
        e_c.grid(row=3, column=1, pady=4)

        tk.Label(form, text="Option D:", font=("Segoe UI", 9, "bold")).grid(row=4, column=0, sticky="w", pady=4)
        e_d = tk.Entry(form, width=42)
        e_d.grid(row=4, column=1, pady=4)

        tk.Label(form, text="Correct Answer Key:", font=("Segoe UI", 9, "bold")).grid(row=5, column=0, sticky="w", pady=4)
        combo_key = ttk.Combobox(form, values=["A", "B", "C", "D"], state="readonly", width=8)
        combo_key.grid(row=5, column=1, sticky="w", pady=4)

        tk.Label(form, text="Marks Weightage:", font=("Segoe UI", 9, "bold")).grid(row=6, column=0, sticky="w", pady=4)
        e_marks = tk.Entry(form, width=10)
        e_marks.grid(row=6, column=1, sticky="w", pady=4)

        if existing_q:
            txt_prompt.insert("1.0", existing_q["question_text"])
            e_a.insert(0, existing_q["option_a"])
            e_b.insert(0, existing_q["option_b"])
            e_c.insert(0, existing_q["option_c"])
            e_d.insert(0, existing_q["option_d"])
            combo_key.set(existing_q["correct_option"])
            e_marks.insert(0, str(existing_q["marks"]))
        else:
            combo_key.set("A")
            e_marks.insert(0, "2")

        def save_quest() -> None:
            prompt = txt_prompt.get("1.0", tk.END).strip()
            oa = e_a.get().strip()
            ob = e_b.get().strip()
            oc = e_c.get().strip()
            od = e_d.get().strip()
            key = combo_key.get().strip()
            try:
                marks = int(e_marks.get())
                if existing_q:
                    QuizCRUD.update_question(existing_q["id"], prompt, oa, ob, oc, od, key, marks)
                    messagebox.showinfo("Success", "Question updated successfully!")
                else:
                    QuizCRUD.create_question(self.selected_quiz_id, prompt, oa, ob, oc, od, key, marks)
                    messagebox.showinfo("Success", "Question added to Question Bank!")
                modal.destroy()
                self.refresh_questions()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as err:
                messagebox.showerror("Validation Error", f"Poka-Yoke Constraint Violation: {err}")

        btn_save = tk.Button(form, text="Save Question", font=("Segoe UI", 10, "bold"),
                             bg=THEME_COLOR_SUCCESS, fg="white", relief=tk.FLAT, padx=15, pady=5, command=save_quest)
        btn_save.grid(row=7, column=0, columnspan=2, pady=15)

    def _action_delete_question(self) -> None:
        selected = self.quest_tree.selection()
        if not selected:
            messagebox.showwarning("Select Question", "Please select a question to delete.")
            return
        q_id = int(self.quest_tree.item(selected[0])["values"][0])
        confirm = messagebox.askyesno("Confirm Delete", f"Delete Question #{q_id}?")
        if confirm:
            QuizCRUD.delete_question(q_id)
            messagebox.showinfo("Deleted", "Question removed.")
            self.refresh_questions()
            if self.on_data_changed:
                self.on_data_changed()
