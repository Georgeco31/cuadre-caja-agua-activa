# Backend - Agua Activa ERP

API FastAPI de Agua Activa ERP.

Este backend incluye la base tecnica de FastAPI, PostgreSQL, modelos SQLAlchemy
2.0, migraciones Alembic, autenticacion de administrador con JWT, el modulo
operativo de caja, los modulos base de clientes, productos, empleados, rutas,
vehiculos y proveedores, ventas de contado y a credito, cobros sobre cartera, inventario
manual, produccion aplicada a inventario, carga de camion, retorno, actividad
comercial, cierre financiero por ruta, el reporte comparativo de rutas contra
caja, el registro trazable del dinero de ruta recibido en un cuadre abierto, el
resumen operativo diario, el reporte mensual operativo de solo lectura y el
registro administrativo de compras, listas de precios, gastos operativos
generales con categorías y plantillas recurrentes, control de asistencia,
anticipos, préstamos y abonos de empleados, roles de pago base, clasificacion
productiva, formulas con costos estimados, consumo controlado de insumos y
exportaciones Excel y PDF autenticadas de solo lectura. El
frontend vive en `apps/web`. Todavia no incluye conciliacion automatica,
ingreso automatico por denominaciones, cobros masivos, inventario automatico
por ventas, liquidacion fisica de ruta, consumo automatico de insumos, pago real de nomina,
mantenimiento, combustible, cookies ni refresh tokens.

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

## Dinero de ruta recibido en caja

La tabla `route_cash_receipts` registra que el efectivo de un cierre financiero
activo fue recibido en un cuadre abierto. El registro conserva snapshots del
cierre, ruta y vehiculo, usa importes `Numeric(14, 2)` y admite anulacion
logica con motivo. Solo puede existir un recibo activo por cierre.

Endpoints autenticados:

- `POST /api/v1/route-cash-receipts`
- `GET /api/v1/route-cash-receipts`
- `GET /api/v1/route-cash-receipts/{receipt_id}`
- `POST /api/v1/route-cash-receipts/{receipt_id}/void`
- `GET /api/v1/route-closures/{closure_id}/cash-receipt`
- `GET /api/v1/cash-sessions/{cash_session_id}/route-cash-receipts`

Crear o anular estos registros no modifica denominaciones, conteos, gastos,
resumen oficial de caja, cierres de ruta, inventario, ventas, cobros ni cuentas
por cobrar. Un cierre de ruta con recibo activo no puede anularse hasta que se
anule primero el recibo. El cierre de un cuadre no se bloquea por rutas
pendientes en este bloque.

## Resumen operativo diario

El endpoint autenticado de solo lectura
`GET /api/v1/reports/daily-operational-summary?date=YYYY-MM-DD` consolida para
una fecha el cuadre oficial de caja, produccion y merma, cargas y retornos,
cierres financieros, dinero de rutas registrado en caja, ventas, cobros,
productos agrupados y alertas operativas. Si no se envia `date`, usa la fecha
actual del servidor.

Los importes y cantidades usan `Decimal`/`Numeric`, los registros anulados se
cuentan pero no participan en los totales principales y el total general de
ingresos es solo una referencia operativa. La consulta reutiliza el resumen
oficial de caja y no crea ni modifica cuadres, conteos, gastos, inventario,
produccion, rutas, ventas o cobros. Este bloque no necesita migracion.

## Reporte mensual operativo

El endpoint autenticado de solo lectura
`GET /api/v1/reports/monthly-operational-summary?year=YYYY&month=M` consolida
todo el mes seleccionado. Incluye caja, produccion y merma, ventas, cobros,
cargas, retornos, cierres financieros, dinero de ruta registrado en caja, una
fila por cada dia y un resumen de alertas operativas. Si no se envian `year` y
`month`, usa el año y mes actuales del servidor.

Los registros anulados se cuentan por separado y no participan en los totales
principales. El saldo pendiente corresponde al saldo actual de las ventas a
credito activas creadas durante el mes. El promedio diario contado se calcula
sobre los dias que tienen cuadre de caja. La consulta no crea ni modifica
ningun dato y no necesita migracion.

## Panel gerencial base

El endpoint autenticado de solo lectura
`GET /api/v1/reports/management-dashboard` acepta `date_from` y `date_to`.
Cuando no se envia ningun filtro usa el mes calendario actual del servidor,
en coherencia con el reporte mensual operativo. Si se envia solo una fecha,
esa fecha se usa como inicio y fin.

La respuesta consolida caja, ventas, cartera, gastos operativos, compras,
produccion, inventario actual, rutas, nómina, series simples para gráficos y
alertas gerenciales. Los registros anulados no participan en los totales
principales. Los importes y cantidades se calculan con `Decimal` y se
serializan con el formato decimal habitual de la API.

El saldo vencido usa ventas a crédito activas del rango, con saldo actual y
fecha de vencimiento anterior a la fecha actual. El inventario es una foto
actual y la alerta de stock bajo aplica la regla informativa `stock total <= 5`
porque todavía no existe un mínimo oficial por producto. Para gastos y compras,
un estado `partial` se incluye como pendiente porque esos modelos no almacenan
el monto pagado parcial.

El panel no crea ni modifica registros, no ejecuta conciliaciones y no requiere
migracion. La revisión Alembic permanece en `0025_materials`.

## Exportaciones Excel

El prefijo autenticado `GET /api/v1/reports/exports` ofrece archivos `.xlsx`
para:

- `management-dashboard.xlsx`
- `monthly-summary.xlsx`
- `sales.xlsx`
- `receivables.xlsx`
- `operating-expenses.xlsx`
- `purchases.xlsx`
- `inventory.xlsx`
- `production.xlsx`
- `routes.xlsx`
- `payroll.xlsx`

Los archivos se generan en memoria con `BytesIO` y `openpyxl`, se responden
mediante `StreamingResponse` y no crean ni modifican registros. Las
exportaciones usan los servicios de lectura y los cálculos oficiales ya
existentes. Un rango sin datos produce un libro válido con encabezados y el
mensaje `Sin datos`. Este bloque no agrega migraciones ni seeds; Alembic
permanece en `0025_materials`.

## Exportaciones PDF

El mismo prefijo autenticado ofrece cinco resúmenes ejecutivos:

- `management-dashboard.pdf`
- `monthly-summary.pdf`
- `daily-operational-summary.pdf`
- `receivables.pdf`
- `payroll.pdf`

Los documentos se generan en memoria con `BytesIO` y ReportLab, se responden
mediante `StreamingResponse` con `application/pdf` y nunca se guardan en disco.
El formato elegido es A4 horizontal, con tablas ajustadas, fecha de generación
y numeración de páginas. Panel gerencial, resumen mensual y resumen diario
reutilizan sus servicios oficiales; cartera y nómina reutilizan sus consultas
de lectura y excluyen anulados de los totales principales. Un período sin
actividad genera un PDF válido con el mensaje `Sin datos`. Excel conserva el
detalle operativo y PDF funciona como resumen ejecutivo o impresión. No se
agregan migraciones ni seeds y Alembic permanece en `0025_materials`.

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

## Autenticacion y roles

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

`POST /api/v1/auth/login` devuelve el token y el rol. `GET /api/v1/auth/me`
devuelve `id`, `username`, `role` e `is_active`. Los roles permitidos son
`operator` y `admin_auditor`; la autorizacion consulta el usuario actual en la
base de datos y no depende solo del contenido del JWT.

`/api/v1/users` permite al `admin_auditor` listar y crear cuentas, cambiar rol
o estado y renovar contraseñas. Las contraseñas requieren al menos ocho
caracteres, se almacenan con hash y nunca se devuelven. El sistema impide
desactivar o degradar al último administrador activo.

Los endpoints de cuadres, denominaciones, reportes, clientes, productos,
proveedores, compras, empleados, roles de pago, rutas, vehiculos, ventas y
cobros requieren el header `Authorization: Bearer ...`. Este bloque no
implementa cookies, refresh tokens ni registro publico.

Las operaciones normales admiten ambos roles. Correcciones, anulaciones,
ajustes directos, administracion de precios, panel gerencial, exportaciones
completas y usuarios requieren `admin_auditor`. La matriz completa esta en
`../../docs/22-matriz-permisos-roles.md`.

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
- `PATCH /api/v1/products/{product_id}/production-classification`
- `PATCH /api/v1/products/{product_id}/deactivate`
- `PATCH /api/v1/products/{product_id}/activate`

El listado acepta `search`, `is_active`, `category`, `unit` y `product_kind`.
La busqueda general consulta nombre, SKU, categoria y presentacion.

`product_kind` clasifica el producto como `finished_good`, `raw_material`,
`supply`, `packaging`, `service` u `other`; los productos existentes quedan
como `finished_good`. `sku` es unico cuando se registra. `default_price` y
`cost_estimate` usan `Numeric(12, 2)` y no admiten valores negativos. Los
productos no se eliminan fisicamente: se inactivan y reactivan mediante
`is_active`. La clasificacion no crea ventas, movimientos, producciones ni
datos falsos.

## Proveedores y compras base

La migracion `0019_purchases` crea `suppliers`, `purchases` y
`purchase_items`. Los endpoints autenticados de proveedores son:

- `POST /api/v1/suppliers`
- `GET /api/v1/suppliers`
- `GET /api/v1/suppliers/{supplier_id}`
- `PATCH /api/v1/suppliers/{supplier_id}`
- `PATCH /api/v1/suppliers/{supplier_id}/deactivate`
- `PATCH /api/v1/suppliers/{supplier_id}/activate`

El nombre es obligatorio y la identificacion es unica cuando se informa. El
listado acepta `search`, `is_active` y `supplier_type`. Los proveedores no se
eliminan fisicamente.

Los endpoints autenticados de compras son:

- `POST /api/v1/purchases`
- `GET /api/v1/purchases`
- `GET /api/v1/purchases/{purchase_id}`
- `POST /api/v1/purchases/{purchase_id}/void`

Una compra exige proveedor activo, fecha y al menos un item. El producto del
item es opcional; si se informa debe existir y estar activo, y se guardan sus
snapshots. Sin producto, la descripcion es obligatoria. Cantidad, costo,
descuento e impuesto se procesan con `Decimal` y columnas `Numeric`. El backend
calcula el subtotal del item como `cantidad * costo - descuento`, suma el
impuesto para su total y consolida los importes oficiales de la compra sin
confiar en totales del cliente.

El listado acepta `date_from`, `date_to`, `status`, `payment_status`,
`supplier_id`, `product_id` y `search`. La anulacion exige motivo y conserva la
compra y sus items. Crear o anular una compra no crea movimientos de inventario,
cuadres, gastos, ventas, cobros ni pagos a proveedores. Los seeds no crean
proveedores o compras.

## Gastos operativos generales

La migracion `0021_op_expenses` crea
`operating_expense_categories`, `operating_expenses` y
`recurring_operating_expenses` sin insertar datos. El modulo usa
`Numeric(14, 2)`/`Decimal`, exige importes mayores a cero y protege todos sus
endpoints con Bearer token.

Categorías:

- `POST /api/v1/operating-expenses/categories`
- `GET /api/v1/operating-expenses/categories`
- `GET /api/v1/operating-expenses/categories/{category_id}`
- `PATCH /api/v1/operating-expenses/categories/{category_id}`
- `PATCH /api/v1/operating-expenses/categories/{category_id}/deactivate`
- `PATCH /api/v1/operating-expenses/categories/{category_id}/activate`

Gastos y resumen:

- `POST /api/v1/operating-expenses`
- `GET /api/v1/operating-expenses`
- `GET /api/v1/operating-expenses/{expense_id}`
- `PATCH /api/v1/operating-expenses/{expense_id}`
- `POST /api/v1/operating-expenses/{expense_id}/void`
- `GET /api/v1/operating-expenses/summary`

Plantillas recurrentes:

- `POST /api/v1/operating-expenses/recurring`
- `GET /api/v1/operating-expenses/recurring`
- `GET /api/v1/operating-expenses/recurring/{template_id}`
- `PATCH /api/v1/operating-expenses/recurring/{template_id}`
- `PATCH /api/v1/operating-expenses/recurring/{template_id}/deactivate`
- `PATCH /api/v1/operating-expenses/recurring/{template_id}/activate`
- `POST /api/v1/operating-expenses/recurring/{template_id}/create-expense`

El proveedor es opcional, pero cuando se informa debe existir y estar activo.
La categoría también debe existir y estar activa al crear un gasto o generar
uno desde una plantilla. Los estados de pago son `unpaid`, `paid` y `partial`;
el método `cash`, `transfer`, `card`, `check`, `other` o `unknown` es solo
informativo. Las plantillas nunca generan gastos por cron: cada gasto requiere
la acción manual `create-expense`.

El resumen excluye anulados de los importes principales, los cuenta en
`voided_count` y agrupa los gastos activos por categoría, proveedor y estado
de pago. Como este bloque no registra abonos reales, cada grupo de pago suma el
monto completo de los gastos que tienen ese estado. Crear, editar, generar o
anular un gasto operativo no modifica caja, gastos del cuadre, bancos,
inventario, compras, pagos a proveedores, ventas, cobros, producción ni rutas.

## Empleados

El modulo base usa la tabla `employees` y los endpoints:

- `POST /api/v1/employees`
- `GET /api/v1/employees`
- `GET /api/v1/employees/{employee_id}`
- `PATCH /api/v1/employees/{employee_id}`
- `PATCH /api/v1/employees/{employee_id}/deactivate`
- `PATCH /api/v1/employees/{employee_id}/activate`

El listado acepta `search`, `is_active`, `employee_type` y `job_position`. La busqueda general consulta nombres, identificacion, telefonos, cargo y tipo interno.

`identification` es unico cuando se registra y permite valores nulos.
`base_salary` usa `Numeric(12, 2)` y no admite valores negativos. Los empleados
no se eliminan fisicamente: se inactivan y pueden registrar
`termination_date`; al reactivarlos se limpia esa fecha. El módulo no relaciona
empleados con usuarios del sistema, rutas o camiones.

## Control administrativo de empleados

Las tablas `employee_attendance`, `employee_advances`, `employee_loans` y
`employee_loan_payments` agregan el control administrativo del Bloque 48. Los
endpoints autenticados son:

- `POST|GET /api/v1/employees/attendance`
- `GET|PATCH /api/v1/employees/attendance/{attendance_id}`
- `POST|GET /api/v1/employees/advances`
- `GET /api/v1/employees/advances/{advance_id}`
- `POST /api/v1/employees/advances/{advance_id}/void`
- `POST|GET /api/v1/employees/loans`
- `GET /api/v1/employees/loans/{loan_id}`
- `POST /api/v1/employees/loans/{loan_id}/void`
- `POST /api/v1/employees/loans/{loan_id}/payments`
- `GET /api/v1/employees/loan-payments`
- `POST /api/v1/employees/loan-payments/{payment_id}/void`
- `GET /api/v1/employees/{employee_id}/account-summary`

Los montos y horas usan `Numeric`/`Decimal`. Cada empleado admite una sola
asistencia por fecha. Los anticipos, préstamos y abonos se conservan al
anularse; anular un abono revierte el saldo del préstamo. No se puede abonar
por encima del saldo, abonar a préstamos pagados o anulados, ni anular un
préstamo con pagos activos.

Este control no crea datos en seeds y no modifica caja, bancos, gastos del
cuadre o gastos operativos.

## Roles de pago base

Las tablas `payroll_runs`, `payroll_items`,
`payroll_item_advance_deductions` y `payroll_item_loan_deductions` congelan el
cálculo administrativo del Bloque 49. Los endpoints autenticados son:

- `POST /api/v1/payroll/runs/preview`
- `POST /api/v1/payroll/runs`
- `GET /api/v1/payroll/runs`
- `GET /api/v1/payroll/runs/{payroll_run_id}`
- `POST /api/v1/payroll/runs/{payroll_run_id}/void`
- `GET /api/v1/employees/{employee_id}/payroll-summary`

El preview no persiste datos. Al crear, el backend usa el sueldo base completo
del empleado sin prorratearlo, conserva la asistencia del período como
referencia y calcula ingresos, descuentos y neto con `Decimal`/`Numeric`. El
neto negativo se bloquea.

Los anticipos seleccionados se descuentan completos. Los préstamos admiten un
monto parcial, pero la regla simple del MVP impide usar el mismo préstamo en
más de un rol activo. Los anticipos tampoco pueden repetirse en roles activos.
Anular el rol libera ambas referencias para roles futuros.

Crear o anular un rol no modifica `employee_advances`, `employee_loans`, no
crea `employee_loan_payments`, no paga sueldos y no crea movimientos de caja,
banco, gastos del cuadre o gastos operativos.

## Rutas de entrega

El modulo base usa la tabla `delivery_routes` y los endpoints:

- `POST /api/v1/delivery-routes`
- `GET /api/v1/delivery-routes`
- `GET /api/v1/delivery-routes/{route_id}`
- `PATCH /api/v1/delivery-routes/{route_id}`
- `PATCH /api/v1/delivery-routes/{route_id}/deactivate`
- `PATCH /api/v1/delivery-routes/{route_id}/activate`

El listado acepta `search`, `is_active`, `zone` y `sector`. La busqueda general consulta nombre, codigo, zona, sector y dias de atencion.

`code` es unico cuando se registra y permite valores nulos. `expected_daily_cash` usa `Numeric(12, 2)` y no admite valores negativos. Las rutas no se eliminan fisicamente: se inactivan y reactivan mediante `is_active`. Chofer y vehiculo son referencias de texto; no existen relaciones formales con empleados o camiones. La administracion de rutas no mueve inventario por si sola; el modulo separado de cargas referencia rutas activas.

## Vehiculos

El modulo base usa la tabla `vehicles` y los endpoints:

- `POST /api/v1/vehicles`
- `GET /api/v1/vehicles`
- `GET /api/v1/vehicles/{vehicle_id}`
- `PATCH /api/v1/vehicles/{vehicle_id}`
- `PATCH /api/v1/vehicles/{vehicle_id}/deactivate`
- `PATCH /api/v1/vehicles/{vehicle_id}/activate`

El listado acepta `search`, `is_active`, `vehicle_type` y `fuel_type`. La busqueda general consulta nombre, placa, codigo, tipo, marca y modelo.

`code` y `plate` son unicos cuando se registran y permiten valores nulos. `year`, cuando existe, debe estar entre 1900 y 2100. Los vehiculos no se eliminan fisicamente: se inactivan y reactivan mediante `is_active`. El chofer es una referencia de texto; no existen relaciones formales con empleados o rutas. La administracion de vehiculos no mueve inventario por si sola; una carga puede referenciar un vehiculo activo y su ubicacion de inventario.

## Ventas de contado

El modulo comercial base usa las tablas `sales` y `sale_items` y los endpoints autenticados:

- `POST /api/v1/sales/cash`
- `GET /api/v1/sales`
- `GET /api/v1/sales/{sale_id}`
- `POST /api/v1/sales/{sale_id}/void`

El listado acepta `date_from`, `date_to`, `status`, `customer_id`, `payment_method`, `sale_type`, `route_load_id` y `search`. La busqueda consulta el numero interno de venta y el nombre de cliente guardado como snapshot.

Cada venta contiene al menos un producto activo. Si no se envia `unit_price`, se usa el `default_price` del producto. El servicio calcula subtotales y total con `Decimal`, guarda snapshots del cliente y los productos y genera un numero interno unico. Sin cliente se registra `Consumidor final`.

Las ventas no se eliminan fisicamente. La anulacion exige un motivo, cambia el estado a `voided` y conserva los items. Una venta de contado guarda `paid_amount = total_amount`, `balance_amount = 0` y `credit_status = none`. `route_load_id` es opcional y solo permite cargas activas. Esta asociacion no modifica la carga, el cuadre de caja ni inventario, y los seeds no crean ventas falsas.

## Ventas a credito

El credito reutiliza `sales` y `sale_items` y agrega los campos `paid_amount`, `balance_amount`, `credit_status` y `due_date`. Endpoints autenticados:

- `POST /api/v1/sales/credit`
- `GET /api/v1/sales?sale_type=credit`
- `GET /api/v1/sales/{sale_id}`
- `POST /api/v1/sales/{sale_id}/void`
- `GET /api/v1/sales/credit/customer/{customer_id}/balance`

La venta exige un cliente existente, activo y con `credit_allowed = true`. Cuando `credit_limit` es mayor a cero, la deuda activa del cliente mas el nuevo total no puede superarlo; el valor cero significa que no existe un limite definido. La validacion bloquea la fila del cliente durante la transaccion para mantener consistente el limite ante solicitudes concurrentes.

Una venta nueva queda con `sale_type = credit`, `paid_amount = 0`, `balance_amount = total_amount` y `credit_status = pending`. Al anularla conserva sus items, cambia a `status = voided` y `credit_status = voided`, y su saldo deja de contar como deuda activa.

El resumen de balance considera todas las ventas a credito activas, incluidas las ya pagadas, y excluye ventas anuladas. Devuelve el total vendido, el total pagado y el saldo vigente.

## Cobros y abonos

La tabla `credit_payments` registra pagos sobre una sola venta a credito. Endpoints autenticados:

- `POST /api/v1/sales/{sale_id}/payments`
- `GET /api/v1/sales/{sale_id}/payments`
- `GET /api/v1/credit-payments`
- `POST /api/v1/credit-payments/{payment_id}/void`

El listado general acepta `date_from`, `date_to`, `customer_id`, `sale_id`, `route_load_id`, `status` y `payment_method`. Los importes usan `Numeric(14, 2)` y los metodos permitidos son `cash`, `transfer`, `card` y `other`.

Un abono solo se registra sobre una venta a credito activa con saldo pendiente. El servicio bloquea la fila de la venta, deriva el cliente desde esa venta, impide sobrepagos, incrementa `paid_amount`, reduce `balance_amount` y cambia `credit_status` a `paid` cuando el saldo llega a cero.

La anulacion exige motivo, conserva el registro con `status = voided` y restaura los importes de la venta. Una venta con abonos activos no puede anularse hasta anular primero esos abonos. `route_load_id` es opcional y solo permite cargas activas. La asociacion no modifica automaticamente caja, inventario, rutas o bancos; los seeds no crean cobros falsos.

## Cuentas por cobrar

El modulo de consulta reutiliza `customers`, `sales`, `sale_items` y `credit_payments`; no requiere una tabla ni una migracion adicional. Sus endpoints autenticados y de solo lectura son:

- `GET /api/v1/receivables/summary`
- `GET /api/v1/receivables/customers`
- `GET /api/v1/receivables/customers/{customer_id}/statement`
- `GET /api/v1/receivables/overdue`

El resumen general devuelve clientes con saldo, total vendido a credito, total pagado y saldo pendiente. El listado por cliente acepta `search`, `only_with_balance`, `is_active`, `date_from` y `date_to`; la busqueda consulta nombre y telefonos del cliente.

El estado de cuenta acepta `date_from`, `date_to` e `include_paid`. Devuelve los datos del cliente, totales oficiales, ventas a credito y el historial de pagos de esas ventas. Los filtros de fecha se aplican a la fecha de venta para mantener conciliados el detalle y sus totales. El listado de vencidos incluye ventas activas con fecha de vencimiento anterior a hoy y saldo mayor a cero.

Los totales consideran solamente ventas a credito activas. Excluyen ventas anuladas y no cuentan pagos anulados; estos ultimos pueden conservarse en el historial para trazabilidad. El modulo no registra pagos ni modifica caja, inventario, rutas o bancos.

## Inventario base

La migracion `0011_inventory` crea `inventory_locations`, `inventory_stocks` e `inventory_movements`. El stock usa `Numeric(14, 3)` y los costos usan `Numeric(14, 2)`; no se usan valores flotantes. Endpoints autenticados:

- `POST /api/v1/inventory/locations`
- `GET /api/v1/inventory/locations`
- `GET /api/v1/inventory/locations/{location_id}`
- `PATCH /api/v1/inventory/locations/{location_id}`
- `PATCH /api/v1/inventory/locations/{location_id}/deactivate`
- `PATCH /api/v1/inventory/locations/{location_id}/activate`
- `GET /api/v1/inventory/stocks`
- `POST /api/v1/inventory/movements`
- `GET /api/v1/inventory/movements`
- `GET /api/v1/inventory/movements/{movement_id}`
- `POST /api/v1/inventory/movements/{movement_id}/void`

Las ubicaciones aceptan los tipos `warehouse`, `vehicle`, `production_area` y `other`. Su codigo es opcional y unico cuando existe; se inactivan sin eliminacion fisica. El stock conserva una sola fila por producto y ubicacion.

Los movimientos `entry` y `adjustment_in` aumentan stock; `exit` y `adjustment_out` lo reducen. El servicio bloquea las filas relacionadas, impide cantidades negativas, calcula `total_cost` cuando existe costo unitario y guarda snapshots del producto. La anulacion exige motivo, conserva el movimiento como `voided` y aplica el efecto inverso sin permitir stock negativo.

El inventario puede moverse mediante operaciones manuales, una aplicacion explicita de produccion, una carga de camion o un retorno de ruta explicito. Ventas, caja y cobros no crean ni modifican stock automaticamente, y los seeds no crean ubicaciones, stocks, movimientos, aplicaciones, cargas o retornos falsos.

## Produccion y envasado base

La migracion `0012_production` crea `production_batches` y `production_items`. Las cantidades producidas y la merma usan `Numeric(14, 3)` y se procesan con `Decimal`. Endpoints autenticados:

- `POST /api/v1/production/batches`
- `GET /api/v1/production/batches`
- `GET /api/v1/production/batches/{batch_id}`
- `POST /api/v1/production/batches/{batch_id}/void`
- `POST /api/v1/production/batches/{batch_id}/apply-inventory`
- `GET /api/v1/production/batches/{batch_id}/inventory-application`
- `POST /api/v1/production/inventory-applications/{application_id}/void`

Cada produccion exige una fecha y al menos un producto existente y activo. El backend genera un numero interno unico, conserva snapshots de SKU, nombre y presentacion, y acepta cantidades producidas mayores a cero y merma entre cero y la cantidad producida. El listado permite filtrar por `date_from`, `date_to`, `status`, `product_id` y `search`.

La migracion `0013_prod_inventory` agrega `production_inventory_applications` y `production_inventory_application_items`. Crear una produccion sigue sin modificar inventario. La accion `apply-inventory` exige una ubicacion activa, calcula `quantity_produced - quantity_waste`, omite items con neto cero y crea entradas y stock en una sola transaccion. Solo puede existir una aplicacion activa por lote.

La anulacion de una aplicacion exige motivo, anula sus movimientos y revierte el stock sin permitir cantidades negativas. Todos los registros se conservan. Un lote con aplicacion activa no puede anularse hasta revertirla; un movimiento vinculado tampoco puede anularse directamente desde inventario mientras la aplicacion siga activa. Los seeds no crean producciones ni aplicaciones falsas y este flujo no modifica caja, ventas, cobros o rutas.

## Formulas y costos estimados de produccion

La migracion `0024_recipes` agrega la clasificacion productiva a `products` y
crea `production_recipes` y `production_recipe_items`. Cantidades, costos y
porcentajes se procesan con `Decimal` y columnas `Numeric`; los items conservan
snapshots de SKU, nombre, clasificacion y presentacion.

Endpoints autenticados:

- `POST /api/v1/production/recipes`
- `GET /api/v1/production/recipes`
- `GET /api/v1/production/recipes/{recipe_id}`
- `PATCH /api/v1/production/recipes/{recipe_id}`
- `PATCH /api/v1/production/recipes/{recipe_id}/activate`
- `PATCH /api/v1/production/recipes/{recipe_id}/deactivate`
- `POST /api/v1/production/recipes/{recipe_id}/void`
- `POST /api/v1/production/recipes/{recipe_id}/items`
- `PATCH /api/v1/production/recipe-items/{item_id}`
- `PATCH /api/v1/production/recipe-items/{item_id}/deactivate`
- `PATCH /api/v1/production/recipe-items/{item_id}/activate`
- `GET /api/v1/production/recipes/{recipe_id}/cost-estimate`

El backend calcula `total_cost`, `estimated_material_cost` y
`estimated_cost_per_unit`; el estimador puede escalar cantidades y costos para
otra cantidad de salida. Una formula se crea inactiva, puede existir sin items,
pero necesita al menos un item activo para activarse. Formulas e items se
anulan o desactivan sin borrado fisico.

Este modulo es exclusivamente informativo: no modifica stock, no crea
`inventory_movements`, no cambia caja, compras, ventas o producciones
existentes y no actualiza automaticamente el costo del producto terminado.
Los seeds no crean formulas ni items.

## Consumo controlado de insumos de produccion

La migracion `0025_materials` crea
`production_material_consumptions` y
`production_material_consumption_items`. Crear una produccion o definir una
formula no consume inventario. El operador debe seleccionar una ubicacion
origen y una formula activa para cada producto del lote, revisar la vista
previa y confirmar el consumo.

Endpoints autenticados:

- `POST /api/v1/production/batches/{batch_id}/material-consumption/preview`
- `POST /api/v1/production/batches/{batch_id}/material-consumption`
- `GET /api/v1/production/batches/{batch_id}/material-consumption`
- `GET /api/v1/production/material-consumptions`
- `GET /api/v1/production/material-consumptions/{consumption_id}`
- `POST /api/v1/production/material-consumptions/{consumption_id}/void`

La cantidad usa `quantity_produced`, incluida la produccion dañada o merma, y
se escala contra `recipe.output_quantity`. Despues se suma
`waste_percentage`. El backend usa `Decimal`, valida el stock agregado por
insumo y crea un movimiento `exit` por cada item activo de formula dentro de
una sola transaccion. Solo puede existir un consumo activo por produccion.

El consumo conserva snapshots de producto y formula, costos y referencias a
los movimientos. Su anulacion exige motivo, anula los movimientos y devuelve
el stock sin borrar historial. Una produccion con consumo activo no puede
anularse y sus movimientos no se pueden anular directamente desde inventario.
Este flujo no modifica caja, compras, ventas, formulas, productos ni el lote
de produccion. Los seeds no crean consumos falsos.

## Carga de camion

La migracion `0014_route_loads` crea `route_loads` y `route_load_items`. Endpoints autenticados:

- `POST /api/v1/route-loads`
- `GET /api/v1/route-loads`
- `GET /api/v1/route-loads/{load_id}`
- `GET /api/v1/route-loads/{load_id}/commercial-activity`
- `GET /api/v1/route-loads/{load_id}/settlement-summary`
- `POST /api/v1/route-loads/{load_id}/void`

Una carga exige fecha, ruta activa, vehiculo activo, origen activo, destino activo de tipo `vehicle` y al menos un producto activo. Si el destino esta vinculado a un vehiculo, debe coincidir con el seleccionado. Cada item crea una salida en el origen y una entrada en el destino usando `Numeric(14, 3)` y la logica transaccional de inventario. El listado acepta `date_from`, `date_to`, `status`, `route_id`, `vehicle_id`, `product_id` y `search`.

La anulacion exige motivo, anula ambos movimientos y revierte el traslado sin permitir stock negativo en el destino. La carga, sus items y movimientos se conservan; los movimientos de una carga activa no pueden anularse manualmente. Una carga con retorno activo exige anular primero ese retorno y una carga con ventas o cobros activos asociados no puede anularse. La consulta `commercial-activity` separa ventas de contado, ventas a credito y cobros, agrupa productos y calcula el efectivo esperado como ventas de contado mas cobros. Una carga con cierre financiero activo no admite nuevas ventas, cobros o retornos asociados, ni la anulacion de esas operaciones o de la propia carga.

La consulta `settlement-summary` reutiliza la carga, el retorno activo, la
actividad comercial y el cierre financiero activo. Calcula cargado, retornado,
vendido fisico, vendido registrado y diferencias por producto; tambien expone
ventas, cobros, efectivo esperado, entregado, diferencia y estado `pending`,
`balanced` o `with_difference`. Es de solo lectura y no mueve inventario,
ventas, cobros ni caja. No requiere una migracion adicional a 0027.

## Retorno de ruta

La migracion `0015_route_returns` crea `route_returns` y `route_return_items`. Endpoints autenticados:

- `POST /api/v1/route-returns`
- `GET /api/v1/route-returns`
- `GET /api/v1/route-returns/{return_id}`
- `POST /api/v1/route-returns/{return_id}/void`

Un retorno exige fecha, una carga activa, un destino activo que no sea de tipo `vehicle` y al menos un item perteneciente a la carga. La ruta, el vehiculo y la ubicacion origen se copian desde la carga. Cada cantidad usa `Numeric(14, 3)`, debe ser positiva, no puede superar lo cargado ni el stock disponible en el vehiculo y genera una salida del vehiculo y una entrada en el destino dentro de una sola transaccion.

Solo puede existir un retorno activo por carga; los retornos anulados se conservan como historial. La anulacion exige motivo, conserva items y movimientos, revierte el stock sin permitir negativos y habilita nuevamente la carga para otro retorno. Los movimientos de un retorno activo no pueden anularse manualmente. Este modulo no registra ventas, cobros, caja, dinero entregado, diferencias ni liquidaciones, y los seeds no crean retornos falsos.

## Cierre financiero de ruta

La migracion `0017_route_closures` crea `route_closures`. Endpoints autenticados:

- `POST /api/v1/route-closures`
- `GET /api/v1/route-closures`
- `GET /api/v1/route-closures/{closure_id}`
- `POST /api/v1/route-closures/{closure_id}/void`
- `GET /api/v1/route-loads/{load_id}/financial-closure`

El cierre exige una carga activa, fecha, efectivo entregado mayor o igual a cero y notas opcionales. El backend toma la actividad comercial oficial de la carga y congela snapshots de carga, ruta y vehiculo junto con ventas de contado, ventas a credito, cobros y efectivo esperado. El efectivo esperado es `ventas de contado + cobros`; las ventas a credito no se suman. La diferencia se calcula como `efectivo entregado - efectivo esperado`.

Solo puede existir un cierre activo por carga. El listado acepta filtros de fecha, estado, ruta, vehiculo y texto; el detalle conserva todos los importes y snapshots. La anulacion exige motivo, mantiene el cierre como historial y permite crear otro cierre para la misma carga.

Mientras exista un cierre activo se bloquean la anulacion de la carga, la creacion de ventas, cobros o retornos asociados y la anulacion de ventas, cobros o retornos ya vinculados. El cierre no crea cuadres, gastos, movimientos de caja, movimientos de inventario, ventas ni cobros, y los seeds no crean cierres falsos.

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

El reporte suma `total_coins`, `total_bills`, `total_counted`, `total_pre_count_expenses`, `total_post_count_expenses`, `total_expenses` y `final_total` desde los cuadres registrados usando los conteos y gastos guardados. `total_counted` se calcula como `total_coins + total_bills`. `total_expenses` se mantiene como alias de `total_post_count_expenses` para compatibilidad. Si no se envian fechas, la respuesta devuelve `date_from` y `date_to` como `null`. Este reporte todavia no incorpora las ventas registradas, saldos de credito ni saldo inicial de caja.

Formula oficial del resumen:

```text
total_counted = total_coins + total_bills
total_pre_count_expenses = suma(gastos before_count)
total_post_count_expenses = suma(gastos after_count)
final_total = total_counted - total_post_count_expenses
```

Endpoint comparativo de cierres de ruta contra caja general:

- `GET /api/v1/reports/route-cash-comparison`

Acepta `date_from` y `date_to`. Sin fechas consulta el dia actual; con una sola
fecha usa ese mismo dia como inicio y fin. Devuelve totales del rango y una fila
por fecha que tenga al menos un cierre de ruta activo o un cuadre de caja. Los
cierres anulados quedan excluidos.

El reporte suma el efectivo esperado, entregado y la diferencia congelada en
los cierres activos. Para caja reutiliza el resumen oficial del cuadre:
monedas, billetes, total contado, gastos posteriores al conteo y total final.
La diferencia informativa se calcula asi:

```text
cash_vs_route_delivered_difference =
    cash_total_counted - route_delivered_cash_total
```

Los estados posibles son `no_cash_session`, `no_route_closures`, `matched`,
`cash_higher_than_routes` y `routes_higher_than_cash`. Una diferencia no se
interpreta automaticamente como faltante o sobrante, porque la caja general
puede contener otros ingresos. Esta consulta no crea ni modifica cuadres,
cierres, gastos, ventas, cobros o inventario y no requiere migracion.

## Auditoria general del Bloque 44

El inventario completo de endpoints, la cadena de migraciones, las reglas
criticas y los riesgos operativos estan documentados en
`../../docs/13-auditoria-general-erp.md`.

En el corte auditado:

- OpenAPI contiene 81 plantillas de ruta y 103 operaciones HTTP.
- Solo `POST /api/v1/auth/login` y `GET /api/v1/health` son publicos.
- La revision registrada en ese corte era `0018_route_receipts`; la revision
  actual del proyecto es `0026_user_roles`.
- Las pruebas usan SQLite en memoria; deben complementarse con pruebas de
  integracion PostgreSQL antes de operacion multiusuario.
- Este bloque no crea migraciones, tablas, seeds ni cambios de logica.

Para operar con datos reales, seguir
`../../docs/14-checklist-uso-real-agua-activa.md` y
`../../docs/15-guia-piloto-datos-reales.md`.
