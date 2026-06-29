# Backend - Cuadre de Caja Agua Activa

API minima del proyecto Cuadre de Caja Agua Activa.

Este backend incluye la base tecnica de FastAPI, el endpoint de salud, configuracion inicial de PostgreSQL, modelos SQLAlchemy 2.0 y migraciones Alembic. Todavia no incluye autenticacion, endpoints de negocio, frontend, seeds ni logica de calculo de cuadres.

## Requisitos

- Python 3.11 o superior.
- Docker, si se desea levantar el servicio con Docker Compose.

## Instalacion local

Desde `apps/api`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

## Ejecutar pruebas

Desde `apps/api`:

```bash
pytest
```

## Levantar la API en local

Desde `apps/api`:

```bash
uvicorn app.main:app --reload
```

Luego probar:

```bash
curl http://localhost:8000/api/v1/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "service": "cuadre-caja-api"
}
```

## Levantar con Docker Compose

Desde la raiz del proyecto:

```bash
docker compose up --build api
```

Luego probar en otra terminal:

```bash
curl http://localhost:8000/api/v1/health
```

## Base de datos y migraciones

El backend usa PostgreSQL, SQLAlchemy 2.0 y Alembic.

Desde la raiz del proyecto, levantar la base de datos:

```bash
docker compose up -d db
```

Desde `apps/api`, ejecutar migraciones:

```bash
alembic upgrade head
```

Para desarrollo local fuera de Docker, usar una URL apuntando a `localhost`:

```bash
DATABASE_URL=postgresql+psycopg://cuadre_user:cuadre_password@localhost:5432/cuadre_caja
```

Dentro de Docker Compose, la API usa el host `db`:

```bash
DATABASE_URL=postgresql+psycopg://cuadre_user:cuadre_password@db:5432/cuadre_caja
```

## Variables de entorno

La API usa estas variables con valores por defecto:

- `PROJECT_NAME`
- `API_SERVICE_NAME`
- `API_V1_PREFIX`
- `ENVIRONMENT`
- `DATABASE_URL`

En este bloque no hay endpoints de negocio, autenticacion, frontend ni seeds.
