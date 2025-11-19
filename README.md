# Python Playground API

Backend API para Python Playground - Plataforma interactiva de ejercicios de Python.

## Inicio Rápido

### 1. Configurar el entorno

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y configúralo:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales de base de datos:

```env
# IMPORTANTE: Para asyncpg usa 'ssl=require', NO 'sslmode=require'
DATABASE_URL=postgresql://usuario:password@host/database?sslmode=require
DATABASE_URL_ASYNC=postgresql+asyncpg://usuario:password@host/database?ssl=require
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
CODE_EXECUTION_TIMEOUT=5
```

**Nota importante sobre SSL:**
- `DATABASE_URL` (psycopg2): usa `?sslmode=require`
- `DATABASE_URL_ASYNC` (asyncpg): usa `?ssl=require` (asyncpg NO soporta `sslmode`)

### 3. Ejecutar migraciones

```bash
# Aplicar migraciones a la base de datos
alembic upgrade head
```

### 4. (Opcional) Poblar la base de datos

**Opción A - Usando el script (Windows):**
```bash
seed_database.bat
```

**Opción B - Manualmente:**
```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar seed
python -m app.seed_data
```

### 5. Iniciar el servidor

**Opción A - Usando el script (Windows):**
```bash
start_server.bat
```

**Opción B - Manualmente:**
```bash
# Activar entorno virtual
venv\Scripts\activate

# Iniciar servidor
python -m uvicorn app.main:app --reload
```

### 6. Acceder a la aplicación

- **API:** http://localhost:8000
- **Documentación Swagger:** http://localhost:8000/docs
- **Documentación ReDoc:** http://localhost:8000/redoc

## Estructura del Proyecto

```
app/
├── config/          # Configuración y base de datos
├── models/          # Modelos SQLAlchemy
├── schemas/         # Schemas Pydantic
├── routes/          # Endpoints de la API
├── services/        # Lógica de negocio
└── main.py          # Punto de entrada de la aplicación

alembic/             # Migraciones de base de datos
├── versions/        # Archivos de migración
└── env.py          # Configuración de Alembic
```

## Comandos Útiles

### Migraciones con Alembic

```bash
# Ver estado actual
alembic current

# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

### Desarrollo

```bash
# Verificar configuración
check_setup.bat

# Ejecutar tests
pytest

# Poblar base de datos con datos de ejemplo
seed_database.bat
# o manualmente:
python -m app.seed_data
```

## Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para Python
- **PostgreSQL** - Base de datos relacional
- **Alembic** - Migraciones de base de datos
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI

## Documentación Completa

Para más detalles sobre la arquitectura, configuración y desarrollo, consulta [CLAUDE.md](CLAUDE.md).

## Características Principales

- ✅ CRUD completo de ejercicios
- ✅ Sistema de categorías
- ✅ Casos de prueba automatizados
- ✅ Ejecución de código en sandbox
- ✅ Niveles de dificultad
- ✅ Migraciones de base de datos
- ✅ Documentación interactiva automática

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'psycopg2'"

Asegúrate de activar el entorno virtual antes de ejecutar el servidor:
```bash
venv\Scripts\activate
```

### Error: "connect() got an unexpected keyword argument 'sslmode'"

Este error ocurre al ejecutar el seed o al usar conexiones async. La causa es que `asyncpg` no acepta `sslmode` en la URL.

**Solución:** En `.env`, cambia `DATABASE_URL_ASYNC`:
```env
# ❌ INCORRECTO
DATABASE_URL_ASYNC=postgresql+asyncpg://user:pass@host/db?sslmode=require

# ✅ CORRECTO
DATABASE_URL_ASYNC=postgresql+asyncpg://user:pass@host/db?ssl=require
```

### Error de conexión a base de datos

Verifica que las variables `DATABASE_URL` y `DATABASE_URL_ASYNC` en `.env` sean correctas y que la base de datos esté accesible.

### El servidor no arranca

Ejecuta `check_setup.bat` para verificar que todo está correctamente configurado.

### Warnings de Unicode al ejecutar seed

Los warnings de encoding Unicode en Windows son normales y no afectan la funcionalidad. Los datos se insertan correctamente si ves el mensaje "SUCCESS - Database seeded successfully!".
