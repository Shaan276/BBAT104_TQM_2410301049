"""
Database Connection & Initialization Manager
Handles SQLite3 embedded persistence, WAL mode activation, and schema migration.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from src.config import DB_PATH, DATA_DIR

SCHEMA_FILE = Path(__file__).parent / "schema.sql"
INDEXES_FILE = Path(__file__).parent / "indexes.sql"


def get_db_connection(custom_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Establish a high-performance SQLite connection configured with
    Write-Ahead Logging (WAL) and foreign key constraints.
    """
    path = custom_path or DB_PATH
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    
    # Performance & Integrity Pragmas
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    
    return conn


def init_db(custom_path: Optional[Path] = None, seed: bool = True) -> None:
    """
    Initialize tables, views, and B-Tree indexes.
    Seeds sample data on first run if database is empty.
    """
    conn = get_db_connection(custom_path)
    try:
        with conn:
            if SCHEMA_FILE.exists():
                with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            
            if INDEXES_FILE.exists():
                with open(INDEXES_FILE, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            
        if seed:
            seed_initial_data(conn)
    finally:
        conn.close()


def seed_initial_data(conn: sqlite3.Connection) -> None:
    """Populate default users, categories, quizzes, and questions if empty."""
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        return

    with conn:
        # 1. Default Users
        cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES ('admin', 'ADMIN')")
        cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES ('piyush', 'STUDENT')")
        cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES ('student1', 'STUDENT')")
        
        # 2. Sample Quizzes
        quizzes = [
            ("TQM Principles & SQC Tools", "Quality Management", 10, 60),
            ("Python Performance & Indexing", "Computer Science", 15, 70),
            ("Database Systems & Response Time", "Information Technology", 10, 60),
        ]
        
        cursor.executemany(
            "INSERT INTO quizzes (title, category, duration_minutes, passing_score) VALUES (?, ?, ?, ?)",
            quizzes
        )
        
        # Quiz 1: TQM Questions
        q1_id = 1
        q1_questions = [
            (q1_id, "According to Deming's 85/15 rule, what drives 85% of quality problems?",
             "Individual worker negligence", "Systemic and process design flaws",
             "Hardware component failure", "External customer demands", "B", 2),
            (q1_id, "What is the primary objective of Poka-Yoke in software design?",
             "To eliminate errors at entry level via mistake-proofing", "To speed up network data transfer",
             "To reduce hard drive storage costs", "To enforce strict aesthetic color schemes", "A", 2),
            (q1_id, "Which SQC tool is based on the 80/20 rule to isolate vital causes?",
             "Fishbone Diagram", "Control Chart", "Pareto Analysis", "SIPOC Matrix", "C", 2),
            (q1_id, "In an FMEA matrix, what does RPN stand for?",
             "Response Performance Number", "Risk Priority Number", "Rate of Production Network", "Root Process Node", "B", 2),
            (q1_id, "What does the 'C' stand for in the SIPOC process mapping tool?",
             "Control", "Cost", "Customer", "Calculation", "C", 2),
        ]
        
        # Quiz 2: Python Performance Questions
        q2_id = 2
        q2_questions = [
            (q2_id, "Which data structure provides O(1) average lookup time in Python?",
             "List", "Dictionary (Hash Map)", "Tuple", "Linked List", "B", 2),
            (q2_id, "What is the purpose of SQLite Write-Ahead Logging (WAL) mode?",
             "To disable data integrity checks", "To allow concurrent readers alongside a writer",
             "To compress database tables into zip files", "To eliminate the need for primary keys", "B", 2),
            (q2_id, "What type of index is default in SQLite for fast range and equality queries?",
             "B-Tree Index", "Hash Index", "R-Tree Index", "Full-Text Inverted Index", "A", 2),
            (q2_id, "How can pagination prevent UI freeze when displaying thousands of records?",
             "By loading all rows into a global variable", "By chunking results using LIMIT and OFFSET",
             "By deleting older records from disk", "By slowing down cursor updates", "B", 2),
        ]
        
        # Quiz 3: Database & Response Time Questions
        q3_id = 3
        q3_questions = [
            (q3_id, "What is an Upper Specification Limit (USL) in response time monitoring?",
             "The absolute fastest possible query time", "The maximum tolerable latency before a quality defect occurs",
             "The average query execution time", "The minimum number of database columns", "B", 2),
            (q3_id, "Why does in-memory caching reduce database response times?",
             "It stores frequent query results in RAM avoiding disk I/O", "It deletes stale database indexes",
             "It converts relational data into raw text files", "It reboots the operating system", "A", 2),
            (q3_id, "Which SQL command inspects whether an index is being utilized by a query?",
             "SHOW TABLE STATUS", "EXPLAIN QUERY PLAN", "CHECK INDEX INTEGRITY", "AUDIT PERFORMANCE", "B", 2),
        ]
        
        all_questions = q1_questions + q2_questions + q3_questions
        cursor.executemany(
            """INSERT INTO questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            all_questions
        )
        
        # Sample Attempts to populate history and dashboard metrics
        sample_attempts = [
            (1, 2, 5, 5, 100.0, "PASSED", 14.2),
            (1, 3, 5, 4, 80.0, "PASSED", 19.5),
            (2, 2, 4, 3, 75.0, "PASSED", 11.8),
            (2, 3, 4, 2, 50.0, "FAILED", 22.1),
            (3, 2, 3, 3, 100.0, "PASSED", 9.4),
        ]
        cursor.executemany(
            """INSERT INTO attempts (quiz_id, user_id, total_questions, correct_answers, score_percentage, status, latency_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            sample_attempts
        )
