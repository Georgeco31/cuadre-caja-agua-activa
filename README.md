# Cuadre de Caja Agua Activa

Aplicacion web responsive para registrar el cuadre diario de caja del negocio Agua Activa.

El proyecto busca ordenar el cierre de caja diario mediante el registro de monedas, billetes, gastos realizados con dinero de caja, totales calculados, cierre diario e historial futuro. En esta etapa solo se define la base documental y la estructura inicial del repositorio.

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
- Guardado futuro en base de datos.
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

## Estructura inicial

```text
cuadre-caja-agua-activa/
├── apps/
│   ├── api/
│   │   └── .gitkeep
│   └── web/
│       └── .gitkeep
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

Bloque 0: base documental y estructura inicial.

Todavia no se ha creado una app Next.js, una app FastAPI, modelos SQLAlchemy, migraciones Alembic, endpoints, pantallas ni base de datos funcional.

## Documentacion

- `docs/00-definicion-base.md`: definicion base del proyecto y alcance del MVP.
- `docs/01-roadmap.md`: roadmap por bloques pequeños.
- `docs/02-modelo-datos.md`: modelo de datos inicial documentado.
- `docs/03-reglas-negocio.md`: reglas de negocio del MVP.

## Verificacion del Bloque 0

Ejecutar:

```bash
git status
```

Confirmar que solo existen archivos de documentacion, estructura base y configuracion inicial segura.
