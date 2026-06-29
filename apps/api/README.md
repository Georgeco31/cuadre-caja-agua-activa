# Backend - Cuadre de Caja Agua Activa

API minima del proyecto Cuadre de Caja Agua Activa.

Este backend incluye la base tecnica de FastAPI, el endpoint de salud, configuracion inicial de PostgreSQL, modelos SQLAlchemy 2.0, migraciones Alembic, logica de cuadres, endpoints API del MVP y seeds iniciales. Todavia no incluye login, autenticacion, frontend ni correcciones avanzadas.

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
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_IS_ACTIVE`

`ADMIN_PASSWORD=admin123` es solo un ejemplo local. Debe cambiarse en cualquier entorno real.

## Logica interna de cuadres

La logica de negocio vive en `app/services` y usa repositorios de `app/repositories`.

Funciones principales:

- Crear un cuadre por fecha.
- Evitar cuadres duplicados por fecha.
- Registrar o actualizar conteos por denominacion.
- Calcular subtotales desde denominacion y cantidad.
- Registrar gastos con montos `Decimal`.
- Calcular resumen diario.
- Cerrar un cuadre y bloquear cambios directos cuando esta cerrado.

Los endpoints API usan estos servicios; la logica de negocio no debe duplicarse dentro de las rutas.

## Seeds iniciales

Los seeds cargan:

- Denominaciones iniciales de monedas y billetes.
- Usuario administrador inicial con `password_hash`.

Antes de ejecutar seeds, levantar la base de datos y aplicar migraciones:

```bash
docker compose up -d db
cd apps/api
alembic upgrade head
```

Ejecutar seeds desde `apps/api`:

```bash
python -m app.seeds.run
```

Con Docker Compose, desde la raiz del proyecto:

```bash
docker compose run --rm api python -m app.seeds.run
```

Los seeds son idempotentes: pueden ejecutarse varias veces sin duplicar denominaciones ni usuario admin.

Este bloque no implementa login, JWT, cookies ni rutas protegidas.
