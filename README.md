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
│   └── 03-reglas-negocio.md
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

Todavia no se ha creado registro de gastos desde frontend, historial visual, correcciones desde interfaz, cookies ni refresh tokens.

## Documentacion

- `docs/00-definicion-base.md`: definicion base del proyecto y alcance del MVP.
- `docs/01-roadmap.md`: roadmap por bloques pequeños.
- `docs/02-modelo-datos.md`: modelo de datos inicial documentado.
- `docs/03-reglas-negocio.md`: reglas de negocio del MVP.

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
