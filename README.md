# Agua Activa ERP

Aplicacion web responsive y modular para la operacion interna del negocio Agua Activa.

El proyecto inicio como un sistema para ordenar el cierre de caja diario mediante el registro de monedas, billetes, gastos realizados con dinero de caja, totales calculados, cierre diario, historial, correcciones y resumen acumulado.

A partir del Bloque 23, el proyecto evoluciona estrategicamente hacia **Agua Activa ERP**, un sistema interno modular para controlar produccion, inventario, ventas, caja, rutas, empleados, compras, camiones y rentabilidad. El modulo actual de caja se mantiene como el primer modulo funcional del ERP y no se elimina.

En esta etapa ya existe backend FastAPI con autenticacion JWT, frontend Next.js protegido, modulo operativo de caja, modulos base de clientes, productos, empleados, rutas y vehiculos, registro comercial de ventas de contado y a credito, cartera de cobros y cuentas por cobrar, inventario base, produccion, carga y retorno de camion, consulta de actividad comercial y cierre financiero asociado a una ruta.

## Problema que resuelve

El cuadre de caja necesita una forma clara y consistente de registrar:

- Cantidades de monedas y billetes por denominacion.
- Gastos realizados con dinero de caja antes o despues del conteo.
- Totales calculados automaticamente.
- Estado del cuadre diario.
- Correcciones con trazabilidad cuando un cuadre ya este cerrado.

## Alcance actual

El sistema mantiene el modulo de caja como base operativa e incorpora clientes, productos, empleados, rutas, vehiculos y ventas como primeros modulos nuevos del ERP:

- Registro de cuadre diario.
- Separacion de monedas y billetes.
- Registro de gastos antes del conteo y despues del conteo.
- Calculo automatico de totales.
- Guardado en base de datos.
- Consulta de historial con filtros.
- Correcciones con trazabilidad.
- Resumen acumulado de caja.
- Operacion local con backup y restauracion.
- Registro, consulta, busqueda y edicion de clientes.
- Activacion e inactivacion de clientes sin borrado fisico.
- Registro, consulta, busqueda y edicion de productos.
- Precio base, costo estimado y presentacion por producto.
- Activacion e inactivacion de productos sin borrado fisico.
- Registro, consulta, busqueda y edicion de empleados.
- Datos base de cargo, tipo, sueldo referencial y frecuencia de pago.
- Activacion e inactivacion de empleados sin borrado fisico.
- Registro, consulta, busqueda y edicion de rutas de entrega.
- Zonas, sectores, dias de atencion y referencias operativas por ruta.
- Activacion e inactivacion de rutas sin borrado fisico.
- Registro, consulta, busqueda y edicion de vehiculos.
- Placa, tipo, marca, modelo, combustible y capacidad referencial por vehiculo.
- Activacion e inactivacion de vehiculos sin borrado fisico.
- Registro de ventas de contado con cliente opcional o consumidor final.
- Uno o varios productos por venta, con snapshots y calculos oficiales en backend.
- Consulta, filtros, detalle y anulacion logica de ventas con motivo.
- Registro de ventas a credito solo para clientes activos y habilitados.
- Control de limite, saldo pendiente y resumen de deuda activa por cliente.
- Registro de abonos parciales o pagos totales sobre ventas a credito.
- Historial y anulacion logica de abonos con restauracion del saldo.
- Resumen general de cuentas por cobrar y listado de clientes con saldo pendiente.
- Estado de cuenta por cliente con ventas a credito y abonos registrados.
- Ubicaciones de inventario activables e inactivables sin borrado fisico.
- Stock actual por producto y ubicacion mediante entradas, salidas y ajustes manuales.
- Historial y anulacion trazable de movimientos con reversion del stock.
- Registro de produccion y envasado con uno o varios productos activos.
- Cantidades producidas, merma, snapshots y anulacion logica con motivo.
- Aplicacion explicita de produccion a una ubicacion de inventario.
- Entradas de stock por cantidad neta y anulacion transaccional trazable.
- Carga explicita de productos desde una ubicacion origen hacia el inventario de un vehiculo.
- Salida y entrada vinculadas a ruta, vehiculo y carga, con anulacion reversible.
- Retorno trazable de productos desde el vehiculo hacia una ubicacion no vehicular.
- Asociacion opcional de ventas y cobros a una carga activa y consulta de sus totales comerciales.
- Cierre financiero de una carga con importes oficiales congelados, efectivo entregado y diferencia.
- Historial y anulacion trazable del cierre, con bloqueo de operaciones vinculadas mientras permanezca activo.
- Comparacion informativa, por fecha o rango, entre cierres activos de ruta y el cuadre general de caja.

Quedan fuera del MVP:

- Facturacion.
- Descuento automatico de inventario por ventas.
- Conciliacion automatica de cobros con caja o bancos.
- Ingreso automatico o conciliacion contable del cierre de ruta con caja o bancos.
- Liquidacion fisica del inventario restante de una ruta.
- Mantenimiento, combustible, kilometraje y rentabilidad por vehiculo.
- WhatsApp.
- Reportes avanzados.
- Multiples cajas o turnos.
- Exportaciones PDF/Excel.

La vision ERP documenta esos temas como modulos futuros. Los Bloques 24 al 39 implementan las bases de clientes, productos, empleados, rutas, vehiculos, ventas de contado y a credito, cobros, reportes de cartera, inventario manual, produccion aplicada a inventario, carga, retorno, actividad comercial y cierre financiero de ruta. Registrar una produccion no mueve stock por si solo; una carga o retorno explicito si traslada stock entre ubicaciones. Asociar ventas y abonos a una carga, o registrar su cierre financiero, no modifica automaticamente caja, inventario ni bancos.

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
- Bloque 24: modulo base de clientes con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 25: catalogo base de productos y precios con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 26: modulo base de empleados con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 27: modulo base de rutas de entrega con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 28: modulo base de vehiculos con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 29: modulo base de ventas de contado con detalle, calculos backend, filtros y anulacion logica.
- Bloque 30: modulo base de ventas a credito con limite por cliente, saldo pendiente y anulacion logica.
- Bloque 31: modulo base de cobros y abonos con pagos parciales o totales, historial y anulacion reversible.
- Bloque 32: estado de cuenta y reporte de cuentas por cobrar con resumen, filtros y detalle por cliente.
- Bloque 33: inventario base por ubicacion con stock, movimientos manuales y anulacion reversible.
- Bloque 34: produccion y envasado base con detalle por producto, snapshots, filtros y anulacion logica.
- Bloque 35: aplicacion explicita y reversible de produccion a inventario con trazabilidad por movimiento.
- Bloque 36: carga de camion desde inventario origen hacia una ubicacion de vehiculo, asociada a ruta y reversible.
- Bloque 37: retorno de productos desde una carga activa hacia una ubicacion no vehicular, trazable y reversible.
- Bloque 38: asociacion opcional de ventas y cobros a cargas activas con consulta comercial consolidada por ruta.
- Bloque 39: cierre financiero de ruta con snapshots comerciales, efectivo entregado, diferencia, historial, anulacion y bloqueos operativos.
- Bloque 40: reporte de solo lectura que compara cierres activos de ruta con el cuadre general de caja por fecha o rango.

Todavia no se han creado recibos de cobro, cobros masivos, anticipos de clientes, facturacion electronica, ingreso automatico o conciliacion contable del cierre de ruta con caja o bancos, descuento de inventario por ventas, liquidacion fisica del inventario de ruta, compras, proveedores, anticipos a empleados, roles de pago, nomina, mantenimiento, combustible, kilometraje, asignaciones formales, consumo de insumos, mapas, geolocalizacion, exportaciones PDF/Excel, edicion avanzada de ventas, edicion de gastos, eliminacion de gastos, cookies ni refresh tokens.

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
