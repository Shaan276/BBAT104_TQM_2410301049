"""
Unit Tests for Base System CRUD & Role Authentication
Verifies relational integrity, Poka-Yoke input constraints, and database cascading.
"""

import pytest
import sqlite3
from src.database.connection import init_db, get_db_connection
from src.modules.auth import AuthService
from src.modules.quiz_crud import QuizCRUD


@pytest.fixture(autouse=True)
def setup_test_db():
    """Ensure database is initialized before each test suite."""
    init_db()


def test_auth_user_lookup():
    """Verify that seeded users can be retrieved by username."""
    admin = AuthService.get_user_by_username("admin")
    assert admin is not None
    assert admin["role"] == "ADMIN"

    student = AuthService.get_user_by_username("piyush")
    assert student is not None
    assert student["role"] == "STUDENT"


def test_auth_poka_yoke_invalid_role():
    """Verify Poka-Yoke validation rejects invalid user roles."""
    with pytest.raises(ValueError, match="Role must be ADMIN or STUDENT"):
        AuthService.create_user("bad_user", "GUEST")


def test_quiz_crud_lifecycle():
    """Test full Create, Read, Update, and Delete cycle for quizzes."""
    # 1. Create
    quiz_id = QuizCRUD.create_quiz(
        title="Test Agile Quality Systems",
        category="Quality Management",
        duration_minutes=12,
        passing_score=65
    )
    assert quiz_id > 0

    # 2. Read
    quiz = QuizCRUD.get_quiz_by_id(quiz_id)
    assert quiz is not None
    assert quiz["title"] == "Test Agile Quality Systems"
    assert quiz["duration_minutes"] == 12

    # 3. Update
    updated = QuizCRUD.update_quiz(
        quiz_id=quiz_id,
        title="Updated Agile Quality Systems",
        category="Quality Management",
        duration_minutes=15,
        passing_score=70
    )
    assert updated is True
    quiz_after = QuizCRUD.get_quiz_by_id(quiz_id)
    assert quiz_after["title"] == "Updated Agile Quality Systems"
    assert quiz_after["duration_minutes"] == 15

    # 4. Delete
    deleted = QuizCRUD.delete_quiz(quiz_id)
    assert deleted is True
    assert QuizCRUD.get_quiz_by_id(quiz_id) is None


def test_question_crud_and_poka_yoke():
    """Test question authoring and Poka-Yoke option validation."""
    quiz_id = QuizCRUD.create_quiz(
        title="Temp Quiz for Questions",
        category="Testing",
        duration_minutes=5,
        passing_score=50
    )

    # Valid question creation
    qid = QuizCRUD.create_question(
        quiz_id=quiz_id,
        question_text="What does CTQ stand for in TQM?",
        option_a="Critical to Quantity",
        option_b="Critical to Quality",
        option_c="Control the Queue",
        option_d="Calculate Total Quota",
        correct_option="B",
        marks=2
    )
    assert qid > 0

    questions = QuizCRUD.get_questions_by_quiz(quiz_id)
    assert len(questions) == 1
    assert questions[0]["correct_option"] == "B"

    # Poka-Yoke: Invalid option pointer should raise ValueError
    with pytest.raises(ValueError, match="Correct option must be A, B, C, or D"):
        QuizCRUD.create_question(
            quiz_id=quiz_id,
            question_text="Invalid question?",
            option_a="A", option_b="B", option_c="C", option_d="D",
            correct_option="Z"  # Invalid!
        )

    # Clean up
    QuizCRUD.delete_quiz(quiz_id)
