# Cuadre de Caja Agua Activa

Aplicacion web responsive para registrar el cuadre diario de caja del negocio Agua Activa.

El proyecto busca ordenar el cierre de caja diario mediante el registro de monedas, billetes, gastos realizados con dinero de caja, totales calculados, cierre diario e historial futuro. En esta etapa ya existe backend FastAPI con autenticacion JWT y una base frontend Next.js con login y dashboard inicial.

## Problema que resuelve

El cuadre de caja necesita una forma clara y consistente de registrar:

- Cantidades de monedas y billetes por denominacion.
- Gastos realizados con dinero de caja.
- Totales calculados automaticamente.
- Estado del cuadre diario.
- Correcciones con trazabilidad cuando un cuadre ya este cerrado.

## Alcance del MVP

El MVP se enfoca solamente en:

- Registro de cuadre diario.
- Separacion de monedas y billetes.
- Registro de gastos.
- Calculo automatico de totales.
- Guardado en base de datos.
- Consulta futura de historial.
- Correcciones con trazabilidad.

Quedan fuera del MVP:

- Facturacion.
- Inventario.
- Clientes.
- Rutas de reparto.
- Ventas.
- WhatsApp.
- Reportes avanzados.
- Multiples cajas o turnos.

## Stack definido

Frontend:

- Next.js
- TypeScript
- Tailwind CSS

Backend:

- FastAPI
- Python
- SQLAlchemy
- Pydantic
- Alembic

Base de datos:

- PostgreSQL

Entorno:

- Docker Compose

Pruebas:

- Pytest para backend.
- Pruebas manuales en navegador para frontend.

## Arquitectura esperada

```text
Frontend Next.js -> API FastAPI -> PostgreSQL
```

## Estructura actual

```text
cuadre-caja-agua-activa/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   ├── alembic/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   └── pyproject.toml
│   └── web/
│       ├── app/
│       ├── components/
│       ├── lib/
│       ├── types/
│       ├── Dockerfile
│       ├── README.md
│       └── package.json
├── docs/
│   ├── 00-definicion-base.md
│   ├── 01-roadmap.md
│   ├── 02-modelo-datos.md
│   ├── 03-reglas-negocio.md
│   ├── 04-ejecucion-local.md
│   └── 05-backup-restauracion.md
├── scripts/
│   ├── backup-db.sh
│   ├── local-migrate.sh
│   ├── local-seed.sh
│   ├── local-start.sh
│   ├── local-stop.sh
│   └── restore-db.sh
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Estado actual

- Bloque 0: base documental y estructura inicial.
- Bloque 1: backend FastAPI base con health endpoint.
- Bloque 2: PostgreSQL, SQLAlchemy, Alembic y modelos iniciales.
- Bloque 3: logica de negocio interna de cuadres.
- Bloque 4: endpoints API REST de cuadres y denominaciones.
- Bloque 5: seeds idempotentes de denominaciones y usuario administrador.
- Bloque 6: autenticacion admin con JWT Bearer.
- Bloque 7: frontend Next.js con login, dashboard inicial y consumo de `/api/v1/auth/me`.
- Bloque 8: pantalla frontend de cuadre diario con denominaciones, conteos, resumen y cierre.
- Bloque 9: registro y listado basico de gastos dentro del cuadre diario.
- Bloque 10: historial y detalle de cuadres con resumen, conteos y gastos.
- Bloque 11: correcciones backend sobre cuadres cerrados con trazabilidad en `correction_logs`.
- Bloque 12: interfaz frontend para correcciones controladas y consulta de logs en detalle de historial.
- Bloque 13: ejecucion local ordenada con Docker Compose, scripts y documentacion de backup/restauracion.
- Bloque 14: precarga de conteos guardados y mejora del flujo diario.
- Bloque 15: resumen acumulado de caja con filtros por fecha y estado.

Todavia no se ha creado reportes avanzados, exportaciones PDF/Excel, ventas reales, edicion desde historial, edicion de gastos, eliminacion de gastos, cookies ni refresh tokens.

## Documentacion

- `docs/00-definicion-base.md`: definicion base del proyecto y alcance del MVP.
- `docs/01-roadmap.md`: roadmap por bloques pequeños.
- `docs/02-modelo-datos.md`: modelo de datos inicial documentado.
- `docs/03-reglas-negocio.md`: reglas de negocio del MVP.
- `docs/04-ejecucion-local.md`: ejecucion local con Docker Compose.
- `docs/05-backup-restauracion.md`: backup y restauracion de PostgreSQL.

## Ejecucion local con Docker

Crear variables locales:

```bash
cp .env.example .env
```

Editar `.env` y cambiar los valores `change-me` antes de usar datos reales.

Comandos principales desde la raiz:

```bash
./scripts/local-start.sh
./scripts/local-migrate.sh
./scripts/local-seed.sh
./scripts/backup-db.sh
./scripts/restore-db.sh backups/nombre_backup.sql
./scripts/local-stop.sh
```

Abrir:

```text
http://localhost:3000/login
```

La API queda disponible en:

```text
http://localhost:8010/api/v1/health
```

Los datos de PostgreSQL se conservan en el volumen Docker `postgres_data`. Los backups locales se guardan en `backups/` y no deben subirse a Git.

## Frontend

La app web vive en `apps/web`.

Variables principales:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8010/api/v1
```

Para desarrollo:

```bash
cd apps/web
npm install
npm run dev
```

## Verificacion general

Ejecutar:

```bash
git status
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest
cd ../web
npm install
npm run build
```

Para validar Docker Compose desde la raiz:

```bash
docker compose config
```
