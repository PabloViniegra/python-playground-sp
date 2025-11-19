@echo off
echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Iniciando servidor FastAPI...
echo El servidor estara disponible en http://localhost:8000
echo Documentacion interactiva en http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
