"""API Routes package.

This package contains all the FastAPI route handlers for the application.
Each module corresponds to a resource or functionality:

- categories: CRUD operations for exercise categories
- exercises: CRUD operations for exercises
- execution: Code execution endpoint for running user-submitted code
"""

from app.routes import categories, execution, exercises

__all__ = ["categories", "exercises", "execution"]
