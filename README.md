# Cuadre de Caja Agua Activa

Aplicacion web responsive para registrar el cuadre diario de caja del negocio Agua Activa.

El proyecto inicio como un sistema para ordenar el cierre de caja diario mediante el registro de monedas, billetes, gastos realizados con dinero de caja, totales calculados, cierre diario, historial, correcciones y resumen acumulado.

A partir del Bloque 23, el proyecto evoluciona estrategicamente hacia **Agua Activa ERP**, un sistema interno modular para controlar produccion, inventario, ventas, caja, rutas, empleados, compras, camiones y rentabilidad. El modulo actual de caja se mantiene como el primer modulo funcional del ERP y no se elimina.

En esta etapa ya existe backend FastAPI con autenticacion JWT, frontend Next.js protegido, gastos separados por momento del conteo y documentacion operativa para prueba piloto local.

## Problema que resuelve

El cuadre de caja necesita una forma clara y consistente de registrar:

- Cantidades de monedas y billetes por denominacion.
- Gastos realizados con dinero de caja antes o despues del conteo.
- Totales calculados automaticamente.
- Estado del cuadre diario.
- Correcciones con trazabilidad cuando un cuadre ya este cerrado.

## Alcance del MVP

El MVP actual se enfoca en el modulo de caja:

- Registro de cuadre diario.
- Separacion de monedas y billetes.
- Registro de gastos antes del conteo y despues del conteo.
- Calculo automatico de totales.
- Guardado en base de datos.
- Consulta de historial con filtros.
- Correcciones con trazabilidad.
- Resumen acumulado de caja.
- Operacion local con backup y restauracion.

Quedan fuera del MVP:

- Facturacion.
- Inventario.
- Clientes.
- Rutas de reparto.
- Ventas.
- WhatsApp.
- Reportes avanzados.
- Multiples cajas o turnos.
- Exportaciones PDF/Excel.

La vision ERP documenta estos temas como modulos futuros, no como funcionalidad implementada en este bloque.

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
│   ├── 05-backup-restauracion.md
│   ├── 06-prueba-piloto-local.md
│   ├── 07-checklist-uso-diario.md
│   ├── 08-checklist-validacion-mvp.md
│   ├── 09-vision-erp-agua-activa.md
│   ├── 10-modulos-erp.md
│   ├── 11-roadmap-erp.md
│   └── 12-reglas-negocio-erp.md
├── scripts/
│   ├── backup-db.sh
│   ├── check-health.sh
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
- Bloque 16: dashboard operativo con estado del cuadre de hoy, acciones rapidas, ultimos cuadres y recordatorio de backup.
- Bloque 17: filtros de historial por fecha desde, fecha hasta y estado.
- Bloque 18: documentacion operativa, checklist de uso diario, checklist de validacion MVP y health check local.
- Bloque 20: gastos separados entre antes del conteo y despues del conteo, con total final calculado solo contra gastos posteriores al conteo.
- Bloque 23: documentacion estrategica de la vision Agua Activa ERP, modulos, roadmap y reglas generales.

Todavia no se ha creado ventas reales, clientes, inventario, rutas, compras, proveedores, empleados, roles de pago, camiones, produccion, exportaciones PDF/Excel, edicion desde historial, edicion de gastos, eliminacion de gastos, cookies ni refresh tokens.

## Documentacion

- `docs/00-definicion-base.md`: definicion base del proyecto y alcance del MVP.
- `docs/01-roadmap.md`: roadmap por bloques pequeños.
- `docs/02-modelo-datos.md`: modelo de datos inicial documentado.
- `docs/03-reglas-negocio.md`: reglas de negocio del MVP.
- `docs/04-ejecucion-local.md`: ejecucion local con Docker Compose.
- `docs/05-backup-restauracion.md`: backup y restauracion de PostgreSQL.
- `docs/06-prueba-piloto-local.md`: guia para ejecutar una prueba piloto local.
- `docs/07-checklist-uso-diario.md`: checklist operativo para el cierre diario.
- `docs/08-checklist-validacion-mvp.md`: checklist tecnico funcional del MVP.
- `docs/09-vision-erp-agua-activa.md`: vision estrategica de Agua Activa ERP.
- `docs/10-modulos-erp.md`: modulos proyectados del ERP.
- `docs/11-roadmap-erp.md`: roadmap por fases hacia Agua Activa ERP.
- `docs/12-reglas-negocio-erp.md`: reglas generales para crecer hacia ERP.

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
./scripts/check-health.sh
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

No usar `docker compose down -v` con datos reales. Para apagar sin borrar datos,
usar siempre `./scripts/local-stop.sh`.

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
npm run typecheck
npm run build
```

Para validar Docker Compose desde la raiz:

```bash
docker compose config
```

Para validar que backend y frontend responden localmente:

```bash
./scripts/check-health.sh
```
