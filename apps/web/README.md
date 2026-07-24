# Frontend - Agua Activa ERP

App web Next.js para Agua Activa ERP.

Este frontend incluye login, panel operativo, modulo de caja, historial, reporte acumulado, resumen operativo diario, correcciones controladas, los modulos base de clientes, productos, empleados, rutas y vehiculos, ventas de contado y a credito, cobros sobre cartera, reportes de cuentas por cobrar, inventario manual, produccion aplicada a inventario, carga de camion, retorno, actividad comercial, cierre financiero por ruta, comparacion informativa de rutas contra caja y registro trazable del dinero de ruta recibido en caja. Todavia no incluye conciliacion automatica, ingreso automatico por denominaciones, cobros masivos, inventario automatico por ventas, liquidacion fisica de inventario de ruta, consumo de insumos, nomina, mantenimiento, combustible, edicion de gastos, cookies ni refresh tokens.

## Requisitos

- Node.js 20 o superior.
- Backend FastAPI levantado.

## Variables

Crear `.env.local` en `apps/web` si se desea cambiar la URL de la API:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8010/api/v1
```

Si el backend se levanta con Docker en el puerto por defecto del proyecto:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8010/api/v1
```

## Instalación

Desde `apps/web`:

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

Abrir:

```text
http://localhost:3000/login
```

Rutas principales:

- `/login`
- `/dashboard`
- `/dashboard/daily-summary`
- `/dashboard/cash-session`
- `/dashboard/history`
- `/dashboard/history/[cashSessionId]`
- `/dashboard/reports`
- `/dashboard/route-cash-comparison`
- `/dashboard/route-cash-receipts`
- `/dashboard/customers`
- `/dashboard/products`
- `/dashboard/employees`
- `/dashboard/delivery-routes`
- `/dashboard/vehicles`
- `/dashboard/inventory`
- `/dashboard/production`
- `/dashboard/route-loads`
- `/dashboard/route-returns`
- `/dashboard/route-activity`
- `/dashboard/route-closures`
- `/dashboard/sales/cash`
- `/dashboard/sales/credit`
- `/dashboard/receivables`
- `/dashboard/receivables/reports`
- `/dashboard/receivables/reports/[customerId]`

## Build

```bash
npm run build
```

## Docker Compose

Desde la raiz del proyecto:

```bash
./scripts/local-start.sh
```

La web queda disponible en:

```text
http://localhost:3000/login
```

## Flujo actual

- Login en `/login`.
- Dashboard protegido en `/dashboard`.
- El dashboard consulta el usuario actual desde `GET /api/v1/auth/me`.
- El dashboard consulta el cuadre de hoy desde `GET /api/v1/cash-sessions/by-date/{session_date}`.
- El dashboard ofrece acceso a `/dashboard/daily-summary` para consultar caja, produccion, rutas, ventas, cobros y alertas de una fecha.
- Si existe cuadre de hoy, el dashboard muestra el resumen oficial desde `GET /api/v1/cash-sessions/{id}/summary`.
- El dashboard muestra acciones rapidas hacia caja, historial, reportes, clientes, productos, empleados, rutas, vehiculos, inventario, produccion, carga de camion, ventas de contado, ventas a credito, cobros y cuentas por cobrar.
- El dashboard muestra los últimos cuadres registrados desde `GET /api/v1/cash-sessions` y el total final desde el resumen oficial de cada cuadre.
- El dashboard muestra un recordatorio de backup para el cierre del día o fin de pruebas.
- La pantalla de cuadre diario muestra un selector de fecha con la fecha actual por defecto.
- Al cambiar la fecha, la pantalla consulta `GET /api/v1/cash-sessions/by-date/{session_date}` y limpia los datos visibles de la fecha anterior.
- Si no existe cuadre para la fecha seleccionada, muestra la opcion para crearlo con `POST /api/v1/cash-sessions`.
- Si existe cuadre para la fecha seleccionada, lo carga sin crear duplicados.
- La pantalla de cuadre diario precarga montos contados desde el `subtotal` guardado en `GET /api/v1/cash-sessions/{id}/count-items`.
- Si no hay conteo guardado para una denominación, el input muestra `0.00`.
- El operador ingresa monto contado por denominación; el frontend convierte ese monto a `quantity` antes de enviar al backend.
- El historial lista cuadres desde `GET /api/v1/cash-sessions`.
- El historial permite filtrar por fecha desde, fecha hasta y estado usando `date_from`, `date_to` y `status`.
- El detalle consulta resumen, conteos y gastos del cuadre.
- Denominaciones cargadas desde `GET /api/v1/denominations`.
- Conteos enviados con `POST /api/v1/cash-sessions/{id}/count-items`; el backend sigue recibiendo `quantity` y calculando `subtotal`.
- Conteos listados desde `GET /api/v1/cash-sessions/{id}/count-items`.
- Gastos listados desde `GET /api/v1/cash-sessions/{id}/expenses`.
- Gastos antes del conteo registrados con `POST /api/v1/cash-sessions/{id}/expenses` usando `expense_timing: "before_count"`.
- Gastos despues del conteo registrados con `POST /api/v1/cash-sessions/{id}/expenses` usando `expense_timing: "after_count"`.
- Resumen cargado desde `GET /api/v1/cash-sessions/{id}/summary`.
- El resumen muestra gastos antes del conteo como control y gastos despues del conteo como el monto que se resta del total contado.
- Cierre de cuadre con `POST /api/v1/cash-sessions/{id}/close`.
- Antes de cerrar, el frontend muestra una confirmación con el resumen oficial actual.
- Resumen acumulado cargado desde `GET /api/v1/reports/cash-summary`.
- La pantalla `/dashboard/route-cash-comparison` consulta `GET /api/v1/reports/route-cash-comparison`, permite filtrar por fecha y muestra totales oficiales, comparación diaria y el detalle de cada cierre activo.
- La diferencia entre total contado en caja y efectivo entregado por rutas es informativa: caja puede incluir ventas de oficina, dinero previo, otros ingresos o ajustes.
- El reporte Rutas vs caja es de solo lectura; no crea ni modifica cuadres, cierres, gastos, ventas, cobros o inventario.
- La pantalla `/dashboard/route-cash-receipts` registra que el efectivo de un cierre activo fue recibido dentro de un cuadre abierto, sugiere el monto entregado, muestra la diferencia oficial, permite filtrar el historial y anular con motivo.
- El registro de dinero de ruta es solo trazabilidad: no crea cuadres, no cambia monedas, billetes, gastos ni el total contado, y tampoco modifica cierres, inventario, ventas o cobros.
- La pantalla `/dashboard/daily-summary` consulta `GET /api/v1/reports/daily-operational-summary`, permite seleccionar una fecha y presenta tarjetas, alertas, productos agrupados y listas resumidas de cargas, retornos, cierres y registros de dinero de ruta.
- El resumen operativo diario es de solo lectura: no ofrece formularios de alta, edicion, anulacion o cierre y no calcula totales oficiales en el navegador.
- Correcciones listadas desde `GET /api/v1/cash-sessions/{id}/corrections`.
- Conteos corregidos desde `POST /api/v1/cash-sessions/{id}/corrections/count-items`.
- Gastos correctivos registrados desde `POST /api/v1/cash-sessions/{id}/corrections/expenses`.
- La pantalla `/dashboard/customers` lista clientes desde `GET /api/v1/customers` y permite buscar por nombre, telefono, sector o tipo.
- El alta usa `POST /api/v1/customers` y la edicion usa `PATCH /api/v1/customers/{id}`.
- La inactivacion y reactivacion usan `PATCH /api/v1/customers/{id}/deactivate` y `PATCH /api/v1/customers/{id}/activate`; no se eliminan clientes fisicamente.
- El formulario de clientes muestra tipos en español y conserva los valores internos `household`, `store`, `business`, `distributor` y `other`.
- La pantalla `/dashboard/products` lista productos desde `GET /api/v1/products` y permite buscar por nombre, SKU, categoria o presentacion.
- El alta usa `POST /api/v1/products` y la edicion usa `PATCH /api/v1/products/{id}`.
- La inactivacion y reactivacion usan `PATCH /api/v1/products/{id}/deactivate` y `PATCH /api/v1/products/{id}/activate`; no se eliminan productos fisicamente.
- El catalogo muestra presentacion, precio base, costo estimado, retornabilidad y estado, sin crear ventas ni movimientos de inventario.
- La pantalla `/dashboard/employees` lista empleados desde `GET /api/v1/employees` y permite buscar por nombre, identificacion, telefono, cargo o tipo.
- El alta usa `POST /api/v1/employees` y la edicion usa `PATCH /api/v1/employees/{id}`.
- La inactivacion y reactivacion usan `PATCH /api/v1/employees/{id}/deactivate` y `PATCH /api/v1/employees/{id}/activate`; no se eliminan empleados fisicamente.
- El formulario muestra tipos y frecuencias de pago en español, conserva sus valores internos en ingles y envia el sueldo base como decimal seguro.
- El modulo de empleados no registra anticipos, pagos, roles de pago, nomina, asistencia, rutas ni camiones.
- La pantalla `/dashboard/delivery-routes` lista rutas desde `GET /api/v1/delivery-routes` y permite buscar por nombre, codigo, zona, sector o dias de atencion.
- El alta usa `POST /api/v1/delivery-routes` y la edicion usa `PATCH /api/v1/delivery-routes/{id}`.
- La inactivacion y reactivacion usan `PATCH /api/v1/delivery-routes/{id}/deactivate` y `PATCH /api/v1/delivery-routes/{id}/activate`; no se eliminan rutas fisicamente.
- El listado muestra zona, sector, dias de atencion, referencias textuales de chofer/vehiculo y efectivo diario esperado.
- La administracion de rutas no mueve inventario. El modulo separado de carga de camion puede seleccionar rutas activas.
- La pantalla `/dashboard/vehicles` lista vehiculos desde `GET /api/v1/vehicles` y permite buscar por nombre, placa, codigo, tipo, marca o modelo.
- El alta usa `POST /api/v1/vehicles` y la edicion usa `PATCH /api/v1/vehicles/{id}`.
- La inactivacion y reactivacion usan `PATCH /api/v1/vehicles/{id}/deactivate` y `PATCH /api/v1/vehicles/{id}/activate`; no se eliminan vehiculos fisicamente.
- El formulario muestra tipos de vehiculo y combustible en español, conservando los valores internos en ingles.
- La administracion de vehiculos no mueve inventario. El modulo separado de carga puede seleccionar un vehiculo activo y su ubicacion.
- La pantalla `/dashboard/sales/cash` carga clientes y productos activos y lista solamente ventas con `sale_type=cash` desde `GET /api/v1/sales`.
- El formulario permite consumidor final o cliente existente, varios productos, cantidad, precio unitario ajustable, método de pago, notas y una carga de ruta activa opcional.
- El alta usa `POST /api/v1/sales/cash`; el frontend muestra un total estimado y conserva como oficial el total calculado por el backend.
- El listado permite filtrar por fecha, estado, cliente, método de pago y buscar por número de venta o snapshot del cliente.
- El detalle muestra los snapshots e importes de cada item. La anulación usa `POST /api/v1/sales/{id}/void`, exige motivo y conserva la venta visible como anulada.
- La pantalla `/dashboard/sales/credit` carga clientes y productos activos y lista solamente ventas con `sale_type=credit`.
- El formulario de credito exige un cliente existente. Los clientes sin credito habilitado se muestran deshabilitados y no se ofrece consumidor final.
- El formulario permite varios productos, cantidad, precio unitario ajustable, fecha de vencimiento opcional, notas y una carga de ruta activa opcional.
- El alta usa `POST /api/v1/sales/credit`; el frontend muestra el total y saldo pendiente estimados y conserva como oficiales los importes calculados por el backend.
- El listado de credito muestra total, pagado, saldo pendiente, vencimiento y estado de credito; permite filtrar, consultar el detalle y anular con motivo.
- La pantalla `/dashboard/receivables` lista ventas a credito activas con saldo pendiente y permite filtrar por cliente.
- El formulario exige una venta, fecha, metodo y monto mayor a cero que no supere el saldo visible; ofrece usar el saldo total como monto y permite asociar una carga de ruta activa de forma opcional.
- El alta usa `POST /api/v1/sales/{id}/payments` y refresca la cartera y el historial con los importes oficiales del backend.
- El historial usa `GET /api/v1/credit-payments`, muestra metodos y estados en español y permite anular un abono con motivo mediante `POST /api/v1/credit-payments/{id}/void`.
- La pantalla `/dashboard/receivables/reports` muestra el resumen oficial de cartera y permite filtrar clientes por texto, fecha de venta, estado activo y presencia de saldo pendiente.
- La ruta `/dashboard/receivables/reports/[customerId]` muestra el estado de cuenta del cliente con sus ventas a credito, vencimientos, estados e historial de abonos.
- Los totales de cartera provienen del backend y estas pantallas no registran ni modifican ventas o pagos.
- La pantalla `/dashboard/inventory` muestra stock oficial por producto y ubicacion, permite crear y editar ubicaciones, e inactivarlas o reactivarlas sin borrado fisico.
- El formulario de inventario registra entradas, salidas, ajustes positivos y ajustes negativos mediante `POST /api/v1/inventory/movements`.
- El historial permite filtrar y anular movimientos con motivo. Despues de cada alta o anulacion vuelve a consultar stock y movimientos oficiales desde la API.
- El frontend no calcula el stock ni los costos oficiales y no crea movimientos automaticos desde ventas, caja, cobros o rutas.
- La pantalla `/dashboard/production` carga productos activos, permite agregar varios productos con cantidad producida, merma y observacion por item, y registra el lote mediante `POST /api/v1/production/batches`.
- El historial de produccion permite filtrar por texto, fechas, estado y producto, consultar los snapshots de cada item y anular un registro con motivo mediante `POST /api/v1/production/batches/{id}/void`.
- Crear produccion no modifica inventario. En el detalle, la pantalla muestra la cantidad neta, el estado de aplicacion y las ubicaciones activas.
- La aplicacion exige ubicacion y confirmacion, usa `POST /api/v1/production/batches/{id}/apply-inventory` y vuelve a consultar el lote y su trazabilidad.
- Una aplicacion activa muestra ubicacion, fecha y movimientos generados. Puede anularse con motivo mediante `POST /api/v1/production/inventory-applications/{id}/void`; la API revierte el stock oficial.
- Una produccion anulada no puede aplicarse. Una produccion con aplicacion activa exige anular primero esa aplicacion.
- La pantalla `/dashboard/route-loads` carga rutas, vehiculos, ubicaciones y productos activos, muestra stock oficial disponible en el origen y registra una carga mediante `POST /api/v1/route-loads`.
- Cada carga traslada inventario desde el origen hacia una ubicacion tipo `vehicle`. El listado permite filtrar, consultar movimientos vinculados y anular con motivo mediante `POST /api/v1/route-loads/{id}/void`.
- Despues de crear o anular una carga, la pantalla vuelve a consultar cargas y stock oficial. No calcula stock, registra ventas, cobros, dinero entregado, devoluciones, liquidaciones ni cierres de ruta.
- La pantalla `/dashboard/route-returns` lista retornos y carga las cargas activas que todavia no tienen un retorno activo.
- Al seleccionar una carga muestra ruta, vehiculo, ubicacion origen, productos, cantidad cargada y stock oficial en el vehiculo. El usuario elige un destino activo no vehicular y registra solo las cantidades que regresan.
- El alta usa `POST /api/v1/route-returns`; el listado permite filtrar, consultar movimientos vinculados y anular con motivo mediante `POST /api/v1/route-returns/{id}/void`.
- Despues de crear o anular un retorno, la pantalla vuelve a consultar retornos, cargas y stock oficial. No registra ventas, cobros, caja, dinero entregado, diferencias, liquidaciones ni cierres de ruta.
- La pantalla `/dashboard/route-activity` consulta `GET /api/v1/route-loads/{id}/commercial-activity`, muestra ventas de contado, ventas a credito, cobros, productos agrupados y los totales oficiales del backend.
- Las ventas y los cobros pueden asociarse opcionalmente a una carga activa, pero no modifican automaticamente caja, inventario, rutas o bancos. La actividad de ruta no liquida dinero ni cierra la ruta.
- La pantalla `/dashboard/route-closures` permite seleccionar una carga activa sin cierre financiero, consultar su actividad comercial oficial, ingresar el efectivo entregado y registrar el cierre mediante `POST /api/v1/route-closures`.
- La diferencia mostrada durante la captura es solo una estimacion visual. El efectivo esperado, la diferencia y los snapshots persistidos siempre son calculados por el backend.
- El historial permite filtrar por texto, fecha, estado, ruta y vehiculo, consultar el detalle de importes congelados y anular un cierre con motivo. Un cierre anulado se conserva y la carga vuelve a quedar disponible para otro cierre.
- El cierre financiero bloquea operaciones comerciales vinculadas a la carga mientras esta activo. No crea cuadres, gastos, movimientos de caja o inventario, ventas ni cobros.
- Token JWT guardado en `localStorage` para el MVP inicial.
- Logout elimina el token y vuelve a `/login`.

En el detalle de historial, los gastos se muestran separados entre antes del conteo y despues del conteo. Las correcciones solo se habilitan para cuadres con estado `closed`. Despues de cada correccion, el frontend vuelve a consultar el resumen oficial, los listados afectados y los logs de correccion desde la API.

La pantalla `/dashboard/reports` muestra el resumen acumulado de caja basado en cuadres registrados, incluyendo total en monedas, total en billetes, total contado, gastos antes del conteo y gastos despues del conteo. Todavia no incorpora ventas, cobros, saldos de credito ni saldo inicial de caja.

La pantalla `/dashboard/route-cash-comparison` compara por fecha los cierres
financieros activos de ruta con el cuadre general. Los totales y estados
provienen del backend, los cierres anulados no se incluyen y los días sin caja
o sin rutas se identifican sin tratarlos como un error contable definitivo.

El uso de `localStorage` es una solución simple para desarrollo. No reemplaza una estrategia completa de seguridad para producción.
