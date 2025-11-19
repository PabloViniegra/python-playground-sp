# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python Playground is an interactive Python exercise platform with a FastAPI backend. The application allows users to solve Python coding exercises with automated test case validation through sandboxed code execution.

## Running the Application

### Opción 1: Usando el script de inicio (Recomendado para Windows)
```bash
start_server.bat
```

### Opción 2: Manualmente activando el entorno virtual
En Windows:
```bash
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

En Linux/Mac:
```bash
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

### Opción 3: Usando el entry point de Python
```bash
venv\Scripts\activate
python app/main.py
```

**IMPORTANTE:** Siempre debes activar el entorno virtual antes de ejecutar la aplicación. Si intentas ejecutar sin activar el venv, obtendrás errores de módulos no encontrados.

### Verificar la configuración
Antes de arrancar el servidor por primera vez, puedes verificar que todo está correctamente configurado:
```bash
check_setup.bat
```

### Acceso a la aplicación
- API: `http://localhost:8000`
- Documentación interactiva (Swagger): `http://localhost:8000/docs`
- Documentación alternativa (ReDoc): `http://localhost:8000/redoc`

## Environment Setup

1. Create a virtual environment: `python -m venv venv`
2. Activate it (Windows): `venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` file with required variables (see Configuration below)

## Configuration

The application uses `.env` for configuration (see `app/config/config.py:4-26`).

### Required Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Important variables:**
- `DATABASE_URL` - Synchronous PostgreSQL connection string (for psycopg2)
  - Uses `sslmode=require` for SSL connections
  - Example: `postgresql://user:pass@host/db?sslmode=require`

- `DATABASE_URL_ASYNC` - Async PostgreSQL connection string (for asyncpg)
  - **CRITICAL:** Use `ssl=require` instead of `sslmode=require`
  - asyncpg does NOT support `sslmode` or `channel_binding` parameters
  - Example: `postgresql+asyncpg://user:pass@host/db?ssl=require`

- `SECRET_KEY` - Secret key for encryption (change in production!)
- `CODE_EXECUTION_TIMEOUT` - Timeout in seconds for code execution (default: 5)

### Common Configuration Issues

**Error: "connect() got an unexpected keyword argument 'sslmode'"**
- This means you're using `sslmode=require` in `DATABASE_URL_ASYNC`
- Solution: Change to `ssl=require` for asyncpg connections
- The sync URL (DATABASE_URL) should still use `sslmode=require`

## Architecture

### Core Components

**API Layer** (`app/routes/`)
- `categories.py` - Category management endpoints
- `exercises.py` - Exercise CRUD endpoints
- `execution.py` - Code execution endpoint (POST `/api/execute`)

**Data Models** (`app/models/`)
- `Exercise` - Main exercise entity with title, description, difficulty level
- `TestCase` - Test cases linked to exercises with input/output data
- `Example` - Example solutions for exercises
- `Category` - Exercise categorization (many-to-many with exercises)
- Junction table: `exercise_categories` for many-to-many relationship

**Schemas** (`app/schemas/`) - Pydantic models for request/response validation

**Services** (`app/services/`)
- `executor.py` - CodeExecutor class handles sandboxed Python code execution

### Code Execution Flow

The code execution system (`app/services/executor.py:12-184`) works as follows:

1. **Security validation** - Blacklist check against dangerous imports (os, subprocess, etc.) and statements (eval, exec, open, etc.)
2. **Wrapper generation** - Creates a temporary Python script that imports user code, runs test cases, and outputs JSON results
3. **Sandboxed execution** - Runs in subprocess with timeout limit (configurable via settings)
4. **Result parsing** - Parses JSON output containing pass/fail status for each test case

The executor is accessed via the singleton `code_executor` instance.

### Database

Uses SQLAlchemy with async support:
- Sync engine for migrations/admin tasks
- Async engine (`AsyncSession`) for API requests
- Database dependency: `get_db()` provides async session with auto-commit/rollback

Import path corrections:
- Configuration: `from app.config.config import settings`
- Database: `from app.config.database import get_db, Base`
- Models: `from app.models import Exercise, Category, TestCase, Example`

Note: Some files incorrectly import from `app.core.*` instead of `app.config.*` (see `app/main.py:4` and `app/routes/execution.py:7`). Use `app.config.*` for new code.

## Testing

Run tests with pytest:
```bash
pytest
```

For async tests, the project includes `pytest-asyncio` for handling async test functions.

## Database Migrations

The project uses Alembic for database migrations. Configuration is complete and ready to use.

### Initial Setup (Already Done)
The database has been initialized with the following tables:
- `categories` - Exercise categories
- `exercises` - Main exercises table with difficulty levels
- `test_cases` - Test cases for exercises with input/output data
- `examples` - Example solutions for exercises
- `exercise_categories` - Junction table for many-to-many relationship

### Common Alembic Commands

**Check current migration status:**
```bash
alembic current
```

**Create a new migration after model changes:**
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply all pending migrations:**
```bash
alembic upgrade head
```

**Rollback to previous migration:**
```bash
alembic downgrade -1
```

**View migration history:**
```bash
alembic history
```

### Configuration Details
- `alembic/env.py` - Configured to import models and use settings from `app.config.config`
- `alembic.ini` - Database URL is loaded dynamically from `.env` file
- Migration files are stored in `alembic/versions/`

### Important Notes
- Always create migrations using `--autogenerate` to detect model changes
- Review generated migrations before applying them
- Never modify existing migrations that have been applied to production
- Keep migrations in version control
