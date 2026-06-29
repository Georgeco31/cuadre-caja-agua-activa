# 00 - Definicion Base

## Nombre del proyecto

Cuadre de Caja Agua Activa

## Objetivo

Crear una app web responsive para registrar y ordenar el cuadre diario de caja del negocio Agua Activa.

El sistema debe permitir documentar el conteo de monedas y billetes, registrar gastos hechos con dinero de caja, calcular totales de forma automatica y preparar la base para guardar cierres diarios e historial en una base de datos.

## Alcance de este bloque

Este Bloque 0 solo deja creada la base documental y la estructura inicial del repositorio.

Incluye:

- README inicial del proyecto.
- Documentacion del alcance del MVP.
- Reglas de negocio.
- Modelo de datos inicial documentado.
- Roadmap por bloques.
- Estructura de carpetas base.
- Archivos iniciales seguros como `.gitignore`, `.env.example` y `docker-compose.yml` placeholder.

No incluye:

- App Next.js completa.
- App FastAPI completa.
- Modelos SQLAlchemy reales.
- Migraciones Alembic.
- Endpoints.
- Pantallas.
- Base de datos real.
- Instalacion de dependencias.

## Arquitectura esperada

```text
Frontend Next.js -> API FastAPI -> PostgreSQL
```

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

## MVP

El MVP debe enfocarse solamente en:

- Registro de cuadre diario.
- Separacion de monedas y billetes.
- Registro de gastos.
- Calculo automatico de totales.
- Guardado futuro en base de datos.
- Consulta futura de historial.
- Correcciones con trazabilidad.

## Fuera del MVP

No incluir:

- Facturacion.
- Inventario.
- Clientes.
- Rutas de reparto.
- Ventas.
- WhatsApp.
- Reportes avanzados.
- Multiples cajas o turnos.

## Principios del proyecto

- Avanzar por bloques pequeños.
- Priorizar exactitud y orden antes que diseño avanzado.
- Mantener separada la documentacion, frontend, backend y configuracion.
- No agregar funcionalidades fuera del MVP.
- No inventar datos del negocio.
- Documentar decisiones antes de implementar funcionalidad compleja.
