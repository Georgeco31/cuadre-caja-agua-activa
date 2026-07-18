# Backend - Agua Activa ERP

API FastAPI de Agua Activa ERP.

Este backend incluye la base tecnica de FastAPI, PostgreSQL, modelos SQLAlchemy 2.0, migraciones Alembic, autenticacion de administrador con JWT, el modulo operativo de caja y los modulos base de clientes, productos, empleados, rutas y vehiculos. El frontend vive en `apps/web`. Todavia no incluye ventas, inventario, produccion, nomina, mantenimiento, combustible, cobros o cierres de ruta, cookies ni refresh tokens.

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
- Registrar gastos con montos `Decimal` y momento `before_count` o `after_count`.
- Listar gastos por cuadre.
- Calcular resumen diario.
- Calcular resumen acumulado de caja desde cuadres registrados.
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

Los endpoints de cuadres, denominaciones, reportes, clientes, productos, empleados, rutas y vehiculos requieren el header `Authorization: Bearer ...`. Este bloque no implementa cookies, refresh tokens ni registro publico.

## Clientes

El modulo base de clientes usa la tabla `customers` y los endpoints:

- `POST /api/v1/customers`
- `GET /api/v1/customers`
- `GET /api/v1/customers/{customer_id}`
- `PATCH /api/v1/customers/{customer_id}`
- `PATCH /api/v1/customers/{customer_id}/deactivate`
- `PATCH /api/v1/customers/{customer_id}/activate`

El listado acepta `search`, `is_active`, `customer_type` y `sector`. La busqueda general consulta nombre, telefonos, sector y tipo de cliente.

`primary_phone` es unico cuando se registra, `credit_limit` usa `Numeric(12, 2)` y no admite valores negativos. Los clientes no se eliminan fisicamente: se inactivan y reactivan mediante `is_active`. Este modulo no crea ventas, creditos, cobros, abonos, rutas relacionadas ni datos falsos en seeds.

## Productos y precios

El catalogo base usa la tabla `products` y los endpoints:

- `POST /api/v1/products`
- `GET /api/v1/products`
- `GET /api/v1/products/{product_id}`
- `PATCH /api/v1/products/{product_id}`
- `PATCH /api/v1/products/{product_id}/deactivate`
- `PATCH /api/v1/products/{product_id}/activate`

El listado acepta `search`, `is_active`, `category` y `unit`. La busqueda general consulta nombre, SKU, categoria y presentacion.

`sku` es unico cuando se registra. `default_price` y `cost_estimate` usan `Numeric(12, 2)` y no admiten valores negativos. Los productos no se eliminan fisicamente: se inactivan y reactivan mediante `is_active`. Este modulo no crea ventas, inventario, produccion, historial de precios, precios especiales ni productos falsos en seeds.

## Empleados

El modulo base usa la tabla `employees` y los endpoints:

- `POST /api/v1/employees`
- `GET /api/v1/employees`
- `GET /api/v1/employees/{employee_id}`
- `PATCH /api/v1/employees/{employee_id}`
- `PATCH /api/v1/employees/{employee_id}/deactivate`
- `PATCH /api/v1/employees/{employee_id}/activate`

El listado acepta `search`, `is_active`, `employee_type` y `job_position`. La busqueda general consulta nombres, identificacion, telefonos, cargo y tipo interno.

`identification` es unico cuando se registra y permite valores nulos. `base_salary` usa `Numeric(12, 2)` y no admite valores negativos. Los empleados no se eliminan fisicamente: se inactivan y pueden registrar `termination_date`; al reactivarlos se limpia esa fecha. Este modulo no relaciona empleados con usuarios del sistema y no crea anticipos, pagos, roles de pago, nomina, asistencia, rutas, camiones ni datos falsos en seeds.

## Rutas de entrega

El modulo base usa la tabla `delivery_routes` y los endpoints:

- `POST /api/v1/delivery-routes`
- `GET /api/v1/delivery-routes`
- `GET /api/v1/delivery-routes/{route_id}`
- `PATCH /api/v1/delivery-routes/{route_id}`
- `PATCH /api/v1/delivery-routes/{route_id}/deactivate`
- `PATCH /api/v1/delivery-routes/{route_id}/activate`

El listado acepta `search`, `is_active`, `zone` y `sector`. La busqueda general consulta nombre, codigo, zona, sector y dias de atencion.

`code` es unico cuando se registra y permite valores nulos. `expected_daily_cash` usa `Numeric(12, 2)` y no admite valores negativos. Las rutas no se eliminan fisicamente: se inactivan y reactivan mediante `is_active`. Chofer y vehiculo son referencias de texto; no existen relaciones formales con empleados o camiones. Este modulo no crea ventas, cobros, carga, inventario, liquidacion, cierre de ruta ni datos falsos en seeds.

## Vehiculos

El modulo base usa la tabla `vehicles` y los endpoints:

- `POST /api/v1/vehicles`
- `GET /api/v1/vehicles`
- `GET /api/v1/vehicles/{vehicle_id}`
- `PATCH /api/v1/vehicles/{vehicle_id}`
- `PATCH /api/v1/vehicles/{vehicle_id}/deactivate`
- `PATCH /api/v1/vehicles/{vehicle_id}/activate`

El listado acepta `search`, `is_active`, `vehicle_type` y `fuel_type`. La busqueda general consulta nombre, placa, codigo, tipo, marca y modelo.

`code` y `plate` son unicos cuando se registran y permiten valores nulos. `year`, cuando existe, debe estar entre 1900 y 2100. Los vehiculos no se eliminan fisicamente: se inactivan y reactivan mediante `is_active`. El chofer es una referencia de texto; no existen relaciones formales con empleados o rutas. Este modulo no crea mantenimiento, combustible, gastos, kilometraje, carga, inventario, asignaciones, rentabilidad ni datos falsos en seeds.

Endpoints de gastos dentro de un cuadre:

- `GET /api/v1/cash-sessions/{cash_session_id}/expenses`
- `POST /api/v1/cash-sessions/{cash_session_id}/expenses`

El listado devuelve solo gastos del cuadre solicitado. Cada gasto incluye `expense_timing`:

- `before_count`: gasto registrado antes del conteo. Se muestra para control, pero no se resta del total contado.
- `after_count`: gasto registrado despues del conteo. Se resta del total contado para obtener el total final.

Los gastos existentes y los nuevos gastos sin `expense_timing` explicito quedan como `after_count`. No existen endpoints de edicion o eliminacion de gastos.

Endpoint de conteos dentro de un cuadre:

- `GET /api/v1/cash-sessions/{cash_session_id}/count-items`

El listado devuelve solo conteos del cuadre solicitado e incluye datos basicos de la denominacion para consulta en el frontend.

## Correcciones de cuadres cerrados

Los endpoints normales de conteos y gastos aceptan cambios mientras el cuadre esta `open` y siguen rechazando cambios cuando el cuadre esta cerrado. Para ajustes posteriores al cierre existen endpoints especificos de correccion:

- `POST /api/v1/cash-sessions/{cash_session_id}/corrections/count-items`
- `POST /api/v1/cash-sessions/{cash_session_id}/corrections/expenses`
- `GET /api/v1/cash-sessions/{cash_session_id}/corrections`

Las correcciones solo se permiten en cuadres con estado `closed` y requieren un motivo no vacio. La API calcula los subtotales y totales desde backend, registra `previous_total` y `new_total` en `correction_logs`, y mantiene el cuadre cerrado. Los gastos correctivos se registran como `after_count`.

## Reportes

Endpoint de resumen acumulado de caja:

- `GET /api/v1/reports/cash-summary`

Filtros opcionales:

- `date_from`
- `date_to`
- `status`

El reporte suma `total_coins`, `total_bills`, `total_counted`, `total_pre_count_expenses`, `total_post_count_expenses`, `total_expenses` y `final_total` desde los cuadres registrados usando los conteos y gastos guardados. `total_counted` se calcula como `total_coins + total_bills`. `total_expenses` se mantiene como alias de `total_post_count_expenses` para compatibilidad. Si no se envian fechas, la respuesta devuelve `date_from` y `date_to` como `null`. Este reporte no representa ventas reales porque el sistema aun no registra ventas ni saldo inicial de caja.

Formula oficial del resumen:

```text
total_counted = total_coins + total_bills
total_pre_count_expenses = suma(gastos before_count)
total_post_count_expenses = suma(gastos after_count)
final_total = total_counted - total_post_count_expenses
```
