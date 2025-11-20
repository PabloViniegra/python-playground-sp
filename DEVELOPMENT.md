# Development Guide

This guide contains instructions for developers working on the Python Playground project.

## Table of Contents

1. [Setting Up Development Environment](#setting-up-development-environment)
2. [Code Quality Tools](#code-quality-tools)
3. [Running Tests](#running-tests)
4. [Architecture Overview](#architecture-overview)
5. [Contributing Guidelines](#contributing-guidelines)

---

## Setting Up Development Environment

### 1. Install Development Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install development tools
pip install -r requirements-dev.txt
```

### 2. Install Pre-commit Hooks

Pre-commit hooks automatically run code quality checks before each commit:

```bash
pre-commit install
```

This will install hooks that run:

- Black (code formatter)
- Ruff (linter)
- isort (import sorter)
- MyPy (type checker)
- Security checks with Bandit

---

## Code Quality Tools

All configuration for linting tools is in `pyproject.toml`.

### Black - Code Formatter

Black automatically formats your Python code to a consistent style.

```bash
# Format all files in app directory
black app/

# Format specific file
black app/routes/exercises.py

# Check what would be formatted (don't modify)
black app/ --check

# Show diff of what would change
black app/ --diff
```

**Configuration:**

- Line length: 100 characters
- Target: Python 3.12

### Ruff - Fast Python Linter

Ruff is a fast Python linter that replaces Flake8, isort, and more.

```bash
# Lint all files
ruff check app/

# Auto-fix issues
ruff check app/ --fix

# Check specific file
ruff check app/services/exercise_service.py
```

**What Ruff checks:**

- Code style (PEP 8)
- Import sorting
- Unused imports/variables
- Code complexity
- Security issues
- Best practices

### isort - Import Sorter

Sorts and organizes imports automatically.

```bash
# Sort imports in all files
isort app/

# Check import sorting without modifying
isort app/ --check-only

# Show diff
isort app/ --diff
```

**Import order:**

1. Standard library imports
2. Third-party imports
3. Local application imports

### MyPy - Static Type Checker

MyPy checks type hints for correctness.

```bash
# Type check all files
mypy app/

# Type check specific file
mypy app/services/exercise_service.py

# Generate HTML report
mypy app/ --html-report ./mypy-report
```

**Configuration:**

- Strict mode enabled
- Ignores missing imports for some third-party libraries

---

## Running All Quality Checks

### Manually Run All Checks

```bash
# Run all checks at once
black app/ && ruff check app/ --fix && isort app/ && mypy app/
```

### Pre-commit Run on All Files

```bash
# Run pre-commit hooks on all files (not just staged)
pre-commit run --all-files
```

### Before Committing

Pre-commit hooks run automatically, but you can also run them manually:

```bash
# Check what would run
pre-commit run

# Run specific hook
pre-commit run black
pre-commit run ruff
```

---

## Running Tests

### Basic Test Commands

```bash
# Run all tests
pytest

# Run tests in parallel (faster)
pytest -n auto

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_exercise_service.py

# Run specific test function
pytest tests/unit/test_exercise_service.py::test_create_exercise

# Run tests with specific marker
pytest -m unit  # Only unit tests
pytest -m integration  # Only integration tests
pytest -m security  # Only security tests
```

### Test Markers

Tests are organized with markers:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests with database
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.security` - Security-focused tests
- `@pytest.mark.slow` - Slow-running tests

### Coverage

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open report (Windows)
start htmlcov/index.html

# Open report (Linux/Mac)
open htmlcov/index.html
```

**Coverage Requirements:**

- Minimum overall coverage: 80%
- Critical components (executor, services): 90%+

---

## Architecture Overview

The project follows a **layered architecture** with clear separation of concerns:

```
app/
├── config/          # Configuration and database setup
│   ├── config.py    # Application settings (Pydantic)
│   └── database.py  # SQLAlchemy async setup
│
├── models/          # Database models (SQLAlchemy ORM)
│   ├── category.py
│   ├── exercise.py
│   ├── test_case.py
│   └── example.py
│
├── schemas/         # Request/Response validation (Pydantic)
│   ├── category.py
│   ├── exercise.py
│   ├── test_case.py
│   └── execution.py
│
├── routes/          # API endpoints (thin, delegate to services)
│   ├── categories.py
│   ├── exercises.py
│   └── execution.py
│
├── services/        # Business logic (NEW - refactored layer)
│   ├── category_service.py  # Category business logic
│   ├── exercise_service.py  # Exercise business logic
│   └── executor.py          # Code execution engine
│
└── main.py          # FastAPI application entry point
```

### Service Layer Pattern

The **service layer** encapsulates business logic and keeps route handlers thin.

#### Before (Fat Routes):

```python
@router.post("/exercises")
async def create_exercise(data: ExerciseCreate, db: AsyncSession = Depends(get_db)):
    # 50 lines of business logic in the route handler
    exercise = Exercise(...)
    # Handle categories
    # Handle test cases
    # Handle examples
    # Complex validation
    # ...
```

#### After (Thin Routes with Service Layer):

```python
# Route (thin)
@router.post("/exercises")
async def create_exercise(data: ExerciseCreate, db: AsyncSession = Depends(get_db)):
    return await exercise_service.create_exercise(db, data)

# Service (business logic)
class ExerciseService:
    @staticmethod
    async def create_exercise(db: AsyncSession, data: ExerciseCreate) -> Exercise:
        # All business logic here
        # Validation
        # Database operations
        # Error handling
        pass
```

### Benefits of Service Layer

1. **Testability** - Easy to test business logic without HTTP layer
2. **Reusability** - Services can be used by multiple routes
3. **Maintainability** - Clear separation of concerns
4. **Single Responsibility** - Routes handle HTTP, services handle business logic

---

## Contributing Guidelines

### Code Style

1. **Follow PEP 8** - Black enforces this automatically
2. **Use type hints** - All functions should have type annotations
3. **Write docstrings** - Use Google style docstrings
4. **Keep functions small** - Aim for <50 lines per function
5. **DRY principle** - Don't Repeat Yourself

### Example Code Style

```python
from typing import Optional

async def get_exercise_by_id(
    db: AsyncSession, exercise_id: int
) -> Optional[Exercise]:
    """Get exercise by ID with all relationships loaded.

    Args:
        db: Database session
        exercise_id: Exercise ID

    Returns:
        Exercise object or None if not found

    Raises:
        HTTPException: 404 if exercise not found

    Example:
        >>> exercise = await get_exercise_by_id(db, 1)
        >>> print(exercise.title)
    """
    query = select(Exercise).where(Exercise.id == exercise_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
```

### Git Workflow

1. **Create a feature branch** - `git checkout -b feature/my-feature`
2. **Make small commits** - Commit often with clear messages
3. **Write tests** - Add tests for new features
4. **Run quality checks** - `pre-commit run --all-files`
5. **Push and create PR** - Wait for CI checks to pass

### Commit Messages

Follow conventional commits format:

```
feat: add exercise filtering by category
fix: resolve N+1 query in exercise list
refactor: extract service layer from routes
docs: update development guide
test: add security tests for executor
```

**Prefixes:**

- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `docs:` - Documentation
- `test:` - Tests
- `chore:` - Maintenance tasks

---

## Common Development Tasks

### Adding a New Endpoint

1. Create/update schema in `app/schemas/`
2. Add business logic in `app/services/`
3. Create route handler in `app/routes/`
4. Write tests in `tests/`
5. Update documentation

### Adding a New Model

1. Create model in `app/models/`
2. Create schemas in `app/schemas/`
3. Generate migration: `alembic revision --autogenerate -m "Add model"`
4. Review migration file
5. Apply migration: `alembic upgrade head`

### Debugging

```python
# Use ipdb for debugging (installed in dev dependencies)
import ipdb; ipdb.set_trace()

# Or Python's built-in debugger
import pdb; pdb.set_trace()

# Or use logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

---

## Useful Commands Cheat Sheet

```bash
# Code Quality
black app/                          # Format code
ruff check app/ --fix               # Lint and auto-fix
isort app/                          # Sort imports
mypy app/                           # Type check
pre-commit run --all-files          # Run all checks

# Testing
pytest                              # Run all tests
pytest -n auto                      # Run tests in parallel
pytest --cov=app                    # Run with coverage
pytest -m unit                      # Run only unit tests
pytest -k "test_exercise"           # Run tests matching pattern

# Database
alembic revision --autogenerate     # Create migration
alembic upgrade head                # Apply migrations
alembic current                     # Check current version
alembic history                     # Show migration history

# Development Server
uvicorn app.main:app --reload       # Run dev server
python app/main.py                  # Alternative way to run

# Dependencies
pip install -r requirements.txt     # Install production deps
pip install -r requirements-dev.txt # Install dev deps
pip list --outdated                 # Check outdated packages
```

---

## Troubleshooting

### Pre-commit Hook Fails

If pre-commit fails:

1. Look at the error message
2. Run the specific tool manually (e.g., `black app/`, `ruff check app/ --fix`)
3. Fix issues and try committing again
4. If issues persist, run `pre-commit run --all-files` for detailed output

### Type Check Errors

If MyPy complains about missing types:

```python
# Add type ignore comment (sparingly)
result = some_function()  # type: ignore

# Or add proper type hints
from typing import Any, Optional
result: Optional[str] = some_function()
```

### Import Errors

If you get import errors after refactoring:

1. Check `__init__.py` files exist
2. Verify imports in `__init__.py` are correct
3. Restart your IDE/language server
4. Check Python path: `python -c "import sys; print(sys.path)"`

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://beta.ruff.rs/docs/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Pytest Documentation](https://docs.pytest.org/)

---

## Questions?

If you have questions or run into issues:

1. Check this guide and the main `README.md`
2. Look at existing code for examples
3. Check the `CLAUDE.md` file for AI assistant guidelines
4. Ask the team on Slack/Discord

Happy coding! 🚀
