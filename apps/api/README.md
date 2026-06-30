# Backend - Cuadre de Caja Agua Activa

API minima del proyecto Cuadre de Caja Agua Activa.

Este backend incluye la base tecnica de FastAPI, el endpoint de salud, configuracion inicial de PostgreSQL, modelos SQLAlchemy 2.0, migraciones Alembic, logica de cuadres, endpoints API del MVP, seeds iniciales, autenticacion basica de administrador con JWT y correcciones controladas sobre cuadres cerrados. El frontend vive en `apps/web`. Todavia no incluye cookies ni refresh tokens.

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
curl http://localhost:8010/api/v1/health
```

Con la configuracion local del proyecto, Docker Compose publica la API en `API_PORT`, por defecto `8010`.

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
DATABASE_URL=postgresql+psycopg://cuadre_user:change-me@db:5432/cuadre_caja
```

Desde la raiz del proyecto tambien se puede usar:

```bash
./scripts/local-migrate.sh
./scripts/local-seed.sh
```

## Variables de entorno

La API usa estas variables con valores por defecto:

- `PROJECT_NAME`
- `API_SERVICE_NAME`
- `API_V1_PREFIX`
- `ENVIRONMENT`
- `DATABASE_URL`
- `BACKEND_CORS_ORIGINS`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_IS_ACTIVE`
- `AUTH_SECRET_KEY`
- `AUTH_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

`ADMIN_PASSWORD=change-me` es solo un marcador local. Debe cambiarse antes de usar datos reales.

`BACKEND_CORS_ORIGINS` permite al frontend local comunicarse con la API desde el navegador. Valor local sugerido:

```bash
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

## Logica interna de cuadres

La logica de negocio vive en `app/services` y usa repositorios de `app/repositories`.

Funciones principales:

- Crear un cuadre por fecha.
- Evitar cuadres duplicados por fecha.
- Registrar o actualizar conteos por denominacion.
- Listar conteos por cuadre con datos de denominacion.
- Calcular subtotales desde denominacion y cantidad.
- Registrar gastos con montos `Decimal`.
- Listar gastos por cuadre.
- Calcular resumen diario.
- Cerrar un cuadre y bloquear cambios directos cuando esta cerrado.
- Registrar correcciones justificadas sobre cuadres cerrados con trazabilidad de total anterior y total nuevo.

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

## Autenticacion de administrador

La API usa autenticacion Bearer con JWT para los endpoints de negocio. `GET /api/v1/health` y `POST /api/v1/auth/login` son publicos.

Variables principales:

- `AUTH_SECRET_KEY`
- `AUTH_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Ejemplo de login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Ejemplo de uso del token:

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN_AQUI"
```

Los endpoints de cuadres y denominaciones requieren el header `Authorization: Bearer ...`. Este bloque no implementa cookies, refresh tokens ni registro publico.

Endpoints de gastos dentro de un cuadre:

- `GET /api/v1/cash-sessions/{cash_session_id}/expenses`
- `POST /api/v1/cash-sessions/{cash_session_id}/expenses`

El listado devuelve solo gastos del cuadre solicitado. No existen endpoints de edicion o eliminacion de gastos.

Endpoint de conteos dentro de un cuadre:

- `GET /api/v1/cash-sessions/{cash_session_id}/count-items`

El listado devuelve solo conteos del cuadre solicitado e incluye datos basicos de la denominacion para consulta en el frontend.

## Correcciones de cuadres cerrados

Los endpoints normales de conteos y gastos siguen rechazando cambios cuando el cuadre esta cerrado. Para ajustes posteriores al cierre existen endpoints especificos de correccion:

- `POST /api/v1/cash-sessions/{cash_session_id}/corrections/count-items`
- `POST /api/v1/cash-sessions/{cash_session_id}/corrections/expenses`
- `GET /api/v1/cash-sessions/{cash_session_id}/corrections`

Las correcciones solo se permiten en cuadres con estado `closed` y requieren un motivo no vacio. La API calcula los subtotales y totales desde backend, registra `previous_total` y `new_total` en `correction_logs`, y mantiene el cuadre cerrado.
