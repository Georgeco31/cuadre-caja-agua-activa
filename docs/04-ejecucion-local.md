# 04 - Ejecucion local

Esta guia deja el proyecto listo para ejecutarse localmente con Docker Compose en Agua Activa.

## Requisitos

- Docker Desktop.
- Git.
- Node.js solo si se va a desarrollar el frontend fuera de Docker.
- Python solo si se va a desarrollar el backend fuera de Docker.

## Preparar variables

Desde la raiz del proyecto, crear el archivo `.env`:

```bash
cp .env.example .env
```

Editar `.env` y cambiar al menos:

- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `ADMIN_PASSWORD`
- `AUTH_SECRET_KEY`

No usar secretos reales en `.env.example`. El archivo `.env` local no debe subirse a Git.

## Iniciar el sistema

Desde la raiz del proyecto:

```bash
./scripts/local-start.sh
```

Este comando levanta:

- `db`: PostgreSQL con volumen persistente `postgres_data`.
- `api`: FastAPI en `http://localhost:8010`.
- `web`: Next.js en `http://localhost:3000`.

## Migraciones

Aplicar migraciones dentro del entorno Docker:

```bash
./scripts/local-migrate.sh
```

## Seeds

Cargar denominaciones iniciales y usuario administrador:

```bash
./scripts/local-seed.sh
```

Los seeds son idempotentes y pueden ejecutarse mas de una vez.

## Abrir la aplicacion

Abrir el frontend:

```text
http://localhost:3000/login
```

Iniciar sesion con:

- Usuario: valor de `ADMIN_USERNAME`.
- Contrasena: valor de `ADMIN_PASSWORD`.

Probar health check de la API:

```bash
curl http://localhost:8010/api/v1/health
```

## Apagar

Apagar los contenedores:

```bash
./scripts/local-stop.sh
```

El volumen `postgres_data` se conserva. Para borrar datos locales habria que eliminar el volumen manualmente; no hacerlo sin backup.

## Desarrollo fuera de Docker

Backend:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest
```

Frontend:

```bash
cd apps/web
npm install
npm run typecheck
npm run build
```

## Archivos que no se suben a Git

- `.env`
- `backups/`
- `node_modules/`
- `.next/`
- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `*.tsbuildinfo`
