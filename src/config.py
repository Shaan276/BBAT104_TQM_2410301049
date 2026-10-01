"""
Configuration & Quality Specifications
Project: Online Quiz System [Q05: Reduce Response Time]
Student: Piyush Pilkhwal (2410301049)
Course: BBAT104 Fundamentals of TQM (Academic Session 2026-27)
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"
DB_PATH = DATA_DIR / "quiz_system.db"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Quality Goal Q05 - Performance SLAs (in milliseconds)
SLA_MAX_SEARCH_LATENCY_MS = 40.0       # Upper Specification Limit for Catalog Search
SLA_MAX_LOAD_QUIZ_LATENCY_MS = 50.0    # Upper Specification Limit for Quiz Loading
SLA_MAX_SUBMIT_LATENCY_MS = 100.0      # Upper Specification Limit for Scoring & Commit
SLA_MAX_CACHE_READ_MS = 15.0           # Upper Specification Limit for Dashboard Cache Hit
SLA_MAX_PAGE_CHUNK_MS = 50.0           # Upper Specification Limit for Paginated Report Chunk

# In-Memory Cache Settings (Q05-F3)
CACHE_DEFAULT_TTL_SECONDS = 60         # 60s Time to live before background refresh
CACHE_MAX_ENTRIES = 500

# Pagination Settings (Q05-F5)
DEFAULT_PAGE_SIZE = 10                 # Rows per page for history & audit reports
PAGE_SIZE_OPTIONS = [5, 10, 25, 50]

# UI Constants
APP_TITLE = "Online Quiz System [Q05: Reduce Response Time] - TQM BBAT104"
APP_GEOMETRY = "980x680"
THEME_COLOR_PRIMARY = "#1E293B"        # Slate Dark
THEME_COLOR_ACCENT = "#2563EB"         # Blue Accent
THEME_COLOR_SUCCESS = "#16A34A"        # Green
THEME_COLOR_WARNING = "#D97706"        # Amber
THEME_COLOR_DANGER = "#DC2626"         # Red
THEME_COLOR_BG = "#F8FAFC"             # Light Slate Background
