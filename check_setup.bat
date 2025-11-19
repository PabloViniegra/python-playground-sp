@echo off
echo ========================================
echo Verificando configuracion del proyecto
echo ========================================
echo.

echo [1/4] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [2/4] Verificando version de Python...
python --version

echo [3/4] Verificando dependencias clave...
python -c "import fastapi; print('✓ FastAPI instalado')"
python -c "import sqlalchemy; print('✓ SQLAlchemy instalado')"
python -c "import psycopg2; print('✓ psycopg2 instalado')"
python -c "import asyncpg; print('✓ asyncpg instalado')"
python -c "import alembic; print('✓ Alembic instalado')"

echo [4/4] Verificando importaciones del proyecto...
python -c "from app.main import app; print('✓ Aplicacion carga correctamente')"

echo.
echo ========================================
echo Todo esta correcto! Puedes arrancar el servidor con: start_server.bat
echo ========================================
pause
