@echo off
echo ========================================
echo Poblando base de datos con datos de ejemplo
echo ========================================
echo.

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Ejecutando seed script...
echo (Los warnings de Unicode en Windows son normales y no afectan la funcionalidad)
echo.

python -m app.seed_data

echo.
echo ========================================
echo Proceso completado
echo ========================================
pause
