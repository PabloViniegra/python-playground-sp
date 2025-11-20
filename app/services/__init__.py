"""Services package.

This package contains all business logic services for the application.
Services encapsulate business logic and data access, keeping route handlers thin.
"""

from app.services.category_service import CategoryService, category_service
from app.services.executor import CodeExecutor, code_executor
from app.services.exercise_service import ExerciseService, exercise_service

__all__ = [
    # Executor
    "code_executor",
    "CodeExecutor",
    # Exercise service
    "exercise_service",
    "ExerciseService",
    # Category service
    "category_service",
    "CategoryService",
]
