"""UI package exports."""
from .main_window import MainWindow
from .dashboard_view import DashboardView
from .quiz_view import QuizView
from .reports_view import ReportsView
from .crud_view import CrudView

__all__ = ["MainWindow", "DashboardView", "QuizView", "ReportsView", "CrudView"]
