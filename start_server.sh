#!/bin/bash

echo "Activando entorno virtual..."
source venv/bin/activate

echo "Iniciando servidor FastAPI..."
echo "El servidor estará disponible en http://localhost:8000"
echo "Documentación interactiva en http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
