# 38 - Matriz de permisos granulares del operador

## Estado y alcance

- Bloque: **58A cerrado; protección backend 58B y alineación frontend 58C
  implementadas; código validado en 58D y producción reconstruida en 58D-2**.
- Estado: **10 decisiones principales resueltas por George; backend protegido
  y probado en 58B; interfaz ajustada en 58C; pruebas integrales del código
  aprobadas en 58D; backend, frontend y recorrido productivo sincronizados y
  aprobados en 58D-2**.
- Fecha de corte: **2026-07-28**.
- Alcance original 58A: inventario de pantallas, endpoints y permisos
  existentes; propuesta de permisos granulares para `operator`; riesgos y
  estrategia futura.
- Actualizaciones posteriores: estado efectivo del backend de 58B, de la
  presentación frontend de 58C y de las pruebas integrales de 58D. No se
  cambiaron endpoints, payloads, autenticación, roles, migraciones, seeds, base
  de datos ni lógica de negocio en 58C o 58D.

El inventario de estado actual conservado en este documento corresponde al
corte previo a 58B. La política efectiva de backend se implementó y documentó
en [`39-bloque-58b-proteccion-backend-permisos.md`](39-bloque-58b-proteccion-backend-permisos.md).
Los asuntos no aprobados se deniegan a `operator` por defecto.

## Actualización de implementación 58B

- El backend aplica `require_admin_auditor` a las familias sensibles y usa una
  validación interna para movimientos de inventario.
- `operator` conserva cierre de caja, alta de clientes, ventas de contado y a
  crédito, cobros, producción diaria y movimientos `entry`/`exit` sin costo.
- El alcance recibido para 58B resolvió como permitidos la venta a crédito y el
  cobro; por tanto, las antiguas preguntas F-01 y F-02 dejan de ser pendientes.
- Ajustes de inventario, costos, correcciones, anulaciones, administración,
  nómina, panel gerencial y exportaciones responden `403`.
- Se agregaron 42 casos específicos por rol y la suite completa quedó en 972
  pruebas aprobadas.
- La presentación frontend se alineó después en 58C.

## Actualización de implementación 58C

- Se centralizó la decisión de acceso visual a rutas administrativas del
  dashboard y se agregó una guarda común en su `layout`.
- `operator` ve **22 destinos** justificados en lugar de los 29 anteriores:
  se retiraron gerencia, exportaciones, usuarios, precios administrativos,
  empleados, control laboral, nómina, fórmulas, consumo de insumos, resumen
  acumulado y reporte mensual.
- Una URL directa restringida muestra un mensaje claro y no monta la pantalla
  administrativa. El backend de 58B continúa siendo la autoridad real.
- En pantallas mixtas se conservaron las acciones aprobadas y se ocultaron
  correcciones, anulaciones, mutaciones de catálogos, costos, ajustes de
  inventario y otras operaciones reservadas.
- `operator` conserva caja y cierre diario, clientes, ventas, cobros,
  producción diaria e inventario `entry`/`exit` sin costo.
- `admin_auditor` conserva los **33 destinos**, los módulos administrativos y
  las descargas Excel/PDF.
- La validación manual cubrió ambos roles y los viewports `1366x768`,
  `1440x900`, `390x844` y `412x915`, sin desbordamiento horizontal ni accesos
  restringidos en la navegación móvil del operador.
- El detalle, las pantallas afectadas y la evidencia técnica están en
  [`40-bloque-58c-frontend-permisos-operador.md`](40-bloque-58c-frontend-permisos-operador.md).

## Actualización de validación 58D

- La suite específica volvió a aprobar **42 pruebas** y la suite completa
  aprobó **972 pruebas**.
- El código frontend aprobó typecheck y build de **38 rutas**.
- En navegador, `admin_auditor` conservó **33 destinos** y `operator` mostró
  **22 destinos**.
- Las siete URLs administrativas probadas con `operator` mostraron el mensaje
  de acceso restringido sin montar contenido sensible.
- Un cuadre aislado pudo crearse y cerrarse con `operator`; la corrección
  posterior recibió `403` y el detalle no mostró formularios ni logs de
  corrección.
- Los cuatro viewports aprobaron sin desbordamiento horizontal y la navegación
  móvil del operador no mostró Reportes.
- Excel y PDF administrativos respondieron `200` con tipos de contenido y
  archivos no vacíos.
- LAN, Tailscale, Docker, Alembic y la no publicación de PostgreSQL aprobaron el
  health productivo.
- Se detectó una deriva de despliegue: las imágenes productivas no contienen
  todo el código de 58B/58C.
- George autorizó 58D-2: se creó un backup verificable y se reconstruyeron
  `api` y `web` sin borrar volúmenes ni ejecutar migraciones manuales.
- El smoke backend productivo aprobó **26/26** comprobaciones. `operator`
  recibió `403` real en empleados, nómina, usuarios, precios, gerencia,
  exportaciones, correcciones y anulaciones; mantuvo `200` en los módulos
  operativos aprobados.
- `admin_auditor` conservó `200` en las familias restringidas; Excel y PDF
  productivos devolvieron contenido válido.
- Los hashes de la imagen API coinciden con el código actual y la imagen web
  nueva contiene el mensaje compilado de bloqueo de 58C.
- El recorrido visual productivo real confirmó 33 destinos para
  `admin_auditor`, 22 para `operator`, siete URLs restringidas, módulos
  operativos permitidos y los cuatro viewports sin desbordamiento horizontal.
- La descarga Excel/PDF desde la web devolvió `200`; el bottom nav móvil del
  operador no mostró Reportes.
- La deriva queda resuelta y 58D se aprueba sin reserva por despliegue.
- Evidencia completa:
  [`41-bloque-58d-pruebas-integrales-permisos.md`](41-bloque-58d-pruebas-integrales-permisos.md).
- Guía interna:
  [`42-guia-operativa-permisos-usuarios.md`](42-guia-operativa-permisos-usuarios.md).

## Objetivo

Definir una política clara para que el rol `operator` pueda ejecutar el trabajo
diario sin depender de George, pero sin alterar información crítica, cerrar o
revertir operaciones sensibles, acceder a información gerencial o administrar
configuración sin autorización y trazabilidad suficientes.

La política debe:

1. distinguir lo que el sistema permite hoy de lo que se propone permitir;
2. considerar al backend como autoridad de seguridad;
3. evitar que ocultar un botón se confunda con proteger una operación;
4. dejar a George las decisiones que dependen del puesto real del operador;
5. mantener control total para `admin_auditor`.

## Roles actuales

### `admin_auditor`

Administrador y auditor. Debe conservar acceso total a operación,
configuración, anulaciones, correcciones, reportes sensibles, exportaciones y
usuarios.

### `operator`

Usuario operativo con cuenta personal. Debe registrar y consultar la operación
asignada, pero no administrar seguridad ni ejecutar acciones críticas fuera de
la política aprobada.

## Leyenda de la propuesta

La matriz de este documento usa cinco clasificaciones:

| Código | Clasificación |
| --- | --- |
| **O** | Permitido para `operator`. |
| **T** | Permitido para `operator` con trazabilidad obligatoria. |
| **A** | Restringido a `admin_auditor`. |
| **F** | Pendiente futuro. Para 58B se deniega a `operator` y continúa disponible para `admin_auditor`. |
| **N/A** | No aplica o la acción no existe en el módulo actual. |

Categorías usadas:

- **Ver:** consultar pantalla o información.
- **Crear:** registrar una entidad u operación nueva.
- **Editar abierto:** modificar una operación aún abierta o datos todavía
  editables.
- **Cerrar:** congelar, liquidar o aplicar una operación.
- **Corregir cerrado:** cambiar una operación ya cerrada.
- **Anular:** revertir lógicamente una operación o desactivar un dato maestro.
- **Descargar:** generar o descargar Excel/PDF.
- **Administrar configuración:** cambiar roles, precios, fórmulas, catálogos u
  otros parámetros que gobiernan operaciones posteriores.

`admin_auditor` conserva todas las capacidades marcadas **O**, **T**, **A** o
**F**. Las celdas **F** solo mantienen pendiente el acceso de `operator`.

Una acción **T** debe conservar como mínimo usuario autenticado, fecha y hora,
entidad afectada y datos operativos suficientes para reconstruir lo ocurrido.
Cuando corresponda también debe exigir motivo, referencia y valores
anteriores/nuevos.

## Resumen ejecutivo

El control existente es un RBAC base de dos roles. La regla predominante del
backend es que cualquier usuario autenticado puede usar el endpoint, salvo una
lista de acciones críticas protegidas expresamente para `admin_auditor`.

Hallazgos principales del corte:

- existen **36 archivos de página** bajo `apps/web/app/dashboard`;
- todas esas páginas comprueban un token en el cliente, con guardas repetidas
  por página;
- cuatro destinos completos son exclusivos de administrador en navegación y
  página: listas de precios, usuarios, panel gerencial y exportaciones;
- otras 16 páginas adaptan acciones puntuales por rol, principalmente para
  ocultar anulaciones, ajustes, correcciones o descargas;
- existen **31 módulos de endpoints** y **206 operaciones HTTP decoradas**;
- dos operaciones son públicas (`/auth/login` y `/health`), 145 requieren un
  usuario activo, 58 exigen `admin_auditor` y una restringe condicionalmente
  los ajustes directos de inventario;
- el backend ya devuelve `403` para usuarios inactivos y para operaciones con
  `require_admin_auditor`;
- George resolvió diez decisiones principales: cierre de caja, correcciones,
  anulaciones de ventas/cobros, precios, descargas, panel gerencial, producción
  diaria, inventario operativo y gestión de empleados;
- cierre de caja, registro de producción diaria y movimientos operativos
  `entry`/`exit` quedan permitidos con trazabilidad;
- correcciones cerradas, anulaciones, precios, Excel/PDF, panel gerencial,
  gestión de empleados, anticipos, préstamos y nómina quedan en
  `admin_auditor`;
- aplicar producción al inventario, consumir insumos, registrar compras y otros
  asuntos no respondidos permanecen pendientes futuros y deben denegarse a
  `operator` en 58B;
- las mutaciones críticas que la interfaz oculta por rol tienen respaldo
  backend, pero hay diferencias de **lectura** protegidas solo visualmente:
  `operator` no entra a la pantalla de precios aunque puede consultar listas
  por API, y no ve las secciones de categorías/plantillas de gastos aunque sus
  endpoints de lectura aceptan a cualquier usuario autenticado;
- el riesgo principal sigue siendo el conjunto de capacidades sensibles que
  hoy está abierto en **ambas** capas.

## Inventario frontend

### Pantallas existentes y control actual

| Área | Pantallas | Acceso actual de `operator` | Condición de rol actual en frontend |
| --- | --- | --- | --- |
| Inicio | `/dashboard` | Sí | Oculta cuatro destinos `adminOnly`: precios, usuarios, gerencia y exportaciones. |
| Caja | `/dashboard/cash-session` | Sí | No diferencia roles; permite abrir, contar, registrar gasto y cerrar según estado. |
| Historial y correcciones | `/dashboard/history`, `/dashboard/history/[cashSessionId]` | Sí | El detalle solo carga logs y muestra formularios de corrección a `admin_auditor`. |
| Clientes | `/dashboard/customers` | Sí | Sin filtro de rol para crear, editar, activar o desactivar. |
| Productos | `/dashboard/products` | Sí | Sin filtro de rol para crear, editar, clasificar, activar o desactivar. |
| Precios | `/dashboard/pricing` | No | Comprueba `/auth/me`, muestra estado prohibido y no carga datos si no es `admin_auditor`. |
| Ventas | `/dashboard/sales/cash`, `/dashboard/sales/credit` | Sí | Crear y consultar está visible; anular solo se muestra a administrador. |
| Cartera y cobros | `/dashboard/receivables`, `/dashboard/receivables/reports`, `/dashboard/receivables/reports/[customerId]` | Sí | Registrar y consultar cobros está visible; anular cobro solo se muestra a administrador. |
| Catálogos de ruta | `/dashboard/delivery-routes`, `/dashboard/vehicles` | Sí | Sin filtro de rol para crear, editar, activar o desactivar. |
| Operación de ruta | `/dashboard/route-loads`, `/dashboard/route-returns`, `/dashboard/route-activity`, `/dashboard/route-closures`, `/dashboard/route-cash-receipts`, `/dashboard/route-cash-comparison` | Sí | Operación y consulta visibles; anulaciones de carga, retorno, cierre y recibo solo se muestran a administrador. |
| Inventario | `/dashboard/inventory` | Sí | Oculta ajustes directos y anulación de movimientos a `operator`; ubicaciones y movimientos normales siguen visibles. |
| Producción | `/dashboard/production`, `/dashboard/production/recipes`, `/dashboard/production/material-consumption` | Sí | Oculta anulaciones. Crear/aplicar producción, crear consumos y crear/editar/activar fórmulas siguen visibles al operador. |
| Proveedores y compras | `/dashboard/suppliers`, `/dashboard/purchases` | Sí | Proveedores no diferencia roles; compras oculta únicamente la anulación. |
| Gastos operativos | `/dashboard/operating-expenses` | Sí | Oculta categorías, plantillas recurrentes y anulaciones; crear y editar gastos activos sigue visible. |
| Empleados | `/dashboard/employees`, `/dashboard/employees/control`, `/dashboard/payroll` | Sí | Empleados no diferencia roles; control y nómina ocultan anulaciones, pero permiten registrar asistencia, anticipos, préstamos, abonos y roles de pago. |
| Resúmenes y reportes | `/dashboard/daily-summary`, `/dashboard/monthly-summary`, `/dashboard/reports` | Sí | El reporte mensual oculta sus botones Excel/PDF a `operator`; las consultas permanecen visibles. |
| Gerencia | `/dashboard/management` | No | Comprueba `/auth/me` y no carga el panel si no es `admin_auditor`. |
| Exportaciones | `/dashboard/exports` | No | Comprueba `/auth/me` y no presenta descargas si no es `admin_auditor`. |
| Usuarios | `/dashboard/users` | No | Comprueba `/auth/me`; toda la administración de usuarios y roles es exclusiva de administrador. |

### Naturaleza de las guardas frontend

- La navegación del dashboard filtra enlaces mediante `adminOnly`.
- Las cuatro páginas administrativas vuelven a comprobar el rol recibido de
  `/auth/me`.
- Las acciones puntuales usan el rol almacenado en el navegador o incluido en
  el JWT para decidir qué controles renderizar.
- Estas guardas mejoran la experiencia, pero no son una frontera de seguridad:
  el estado del navegador puede alterarse y una petición puede enviarse fuera
  de la UI.
- La seguridad real depende del endpoint. Los bloques futuros deben mantener
  el orden **backend primero, frontend después**.

## Inventario backend

El prefijo común es `/api/v1`. Salvo `/auth/login` y `/health`, las familias
inventariadas requieren un usuario activo. En la tabla, “autenticado” significa
que hoy acepta tanto `operator` como `admin_auditor`.

| Familia | Endpoints o acciones principales | Autorización actual |
| --- | --- | --- |
| Autenticación | `POST /auth/login`, `GET /auth/me` | Login público; `/auth/me` autenticado. Usuario inactivo recibe `403`. |
| Caja | `/cash-sessions`, conteos, gastos, resumen, recibos de ruta y `/{id}/close` | Autenticado, incluido cerrar. |
| Correcciones de caja | `/{id}/corrections/count-items`, `/{id}/corrections/expenses`, `/{id}/corrections` | Solo `admin_auditor`. El servicio exige cuadre cerrado y registra motivo/log. |
| Denominaciones | `GET /denominations` | Autenticado; no existe CRUD de configuración. |
| Clientes | CRUD, activar y desactivar bajo `/customers` | Todo autenticado. |
| Productos | CRUD, clasificación de producción, activar y desactivar bajo `/products` | Todo autenticado. |
| Precios | Listar/consultar listas y `GET /pricing/resolve` | Autenticado. |
| Configuración de precios | Crear/editar/activar/desactivar listas e ítems | Solo `admin_auditor`. |
| Ventas | Crear contado/crédito y consultar bajo `/sales` | Autenticado. |
| Anulación de venta | `POST /sales/{id}/void` | Solo `admin_auditor`. |
| Cobros | Crear/listar bajo `/sales/{id}/payments` y `/credit-payments` | Autenticado. |
| Anulación de cobro | `POST /credit-payments/{id}/void` | Solo `admin_auditor`. |
| Cartera | Resumen, vencidos y estado de cuenta bajo `/receivables` | Autenticado. |
| Rutas y vehículos | CRUD, activar y desactivar bajo `/delivery-routes` y `/vehicles` | Todo autenticado. |
| Carga, retorno, cierre y recibo de ruta | Crear y consultar bajo `/route-loads`, `/route-returns`, `/route-closures`, `/route-cash-receipts` | Autenticado. |
| Anulaciones de ruta | `/{id}/void` en las cuatro familias anteriores | Solo `admin_auditor`. |
| Actividad y comparación de ruta | Actividad comercial/financiera y `GET /reports/route-cash-comparison` | Autenticado. |
| Ubicaciones y stock | Ubicaciones, activar/desactivar y `GET /inventory/stocks` | Autenticado. |
| Movimientos de inventario | Crear/listar/consultar `/inventory/movements` | Movimientos normales autenticados; `adjustment_in` y `adjustment_out` comprueban administrador dentro del endpoint. |
| Anulación de inventario | `POST /inventory/movements/{id}/void` | Solo `admin_auditor`. |
| Producción | Crear/listar lotes y aplicar a inventario | Autenticado. |
| Anulaciones de producción | Anular lote o aplicación de inventario | Solo `admin_auditor`. |
| Fórmulas | Crear/editar/activar/desactivar fórmula e ítems; estimar costo | Autenticado. Solo `POST /production/recipes/{id}/void` exige administrador. |
| Consumo de insumos | Vista previa, crear y consultar consumos | Autenticado. Anular consumo es solo administrador. |
| Proveedores | CRUD, activar y desactivar bajo `/suppliers` | Todo autenticado. |
| Compras | Crear/listar/consultar bajo `/purchases` | Autenticado. Anular es solo administrador. |
| Gastos operativos | Crear, editar, consultar y crear desde plantilla | Autenticado. Anular es solo administrador. |
| Configuración de gastos | Crear/editar/activar/desactivar categorías y plantillas | Solo `admin_auditor`; lectura autenticada. |
| Empleados | CRUD, activar y desactivar bajo `/employees` | Todo autenticado. |
| Control de empleados | Asistencia, anticipos, préstamos, abonos y resumen | Crear/editar/consultar autenticado. Anular anticipo, préstamo o abono es solo administrador. |
| Nómina | Vista previa, crear y consultar roles de pago | Autenticado. Anular rol es solo administrador. |
| Reportes operativos | Caja, comparación de ruta, resumen diario y resumen mensual bajo `/reports` | Autenticado. |
| Panel gerencial | `GET /reports/management-dashboard` | Solo `admin_auditor`. |
| Excel/PDF | 10 exportaciones `.xlsx` y 5 exportaciones `.pdf` bajo `/reports/exports` | Todas solo `admin_auditor`. |
| Usuarios | Listar, crear, editar, activar/desactivar y cambiar contraseña bajo `/users` | Router completo solo `admin_auditor`. |

### Reglas de estado observadas en servicios

El permiso por rol no sustituye las reglas de negocio existentes:

- `cash_count_service` y `expense_service` exigen que el cuadre esté abierto
  antes de escribir conteos o gastos;
- `correction_service` solo corrige cuadres cerrados, exige motivo y crea un log
  con total anterior, total nuevo y `created_by`;
- `route_cash_receipts` exige un cierre activo, un cuadre abierto y ausencia de
  otro recibo activo para el mismo cierre;
- las creaciones transaccionales principales conservan `created_by`;
- las anulaciones exigen un motivo y conservan estado/fecha, pero debe auditarse
  en 58B si cada modelo también identifica de forma explícita al usuario que
  anuló;
- permitir una acción a `operator` nunca debe omitir estas validaciones ni
  reutilizar un permiso de creación como permiso de cierre, corrección o
  anulación.

## Permisos efectivos y respuestas `403`

### Protecciones reales de backend

Las siguientes capacidades están protegidas actualmente por
`require_admin_auditor` o por una comprobación equivalente:

- todo el router de usuarios;
- correcciones y logs de cuadres cerrados;
- creación y mantenimiento de listas e ítems de precios;
- panel gerencial;
- todas las exportaciones Excel/PDF;
- administración de categorías y plantillas de gastos operativos;
- ajustes directos y anulaciones de inventario;
- anulaciones de ventas, cobros, compras y gastos;
- anulaciones de carga, retorno, cierre y recibo de ruta;
- anulaciones de producción, aplicación de inventario, fórmula y consumo de
  insumos;
- anulaciones de anticipos, préstamos, abonos y roles de pago.

Un usuario activo sin el rol requerido recibe:

```text
403
No tienes permisos para realizar esta acción.
```

Un usuario inactivo también recibe `403`, con el detalle específico de usuario
inactivo. Una petición sin credenciales válidas recibe `401`.

### Evidencia automatizada existente

`apps/api/tests/test_user_roles_endpoints.py` prueba expresamente que:

- `operator` puede crear y listar un cuadre normal;
- `operator` no puede listar ni crear usuarios;
- `operator` recibe `403` al intentar anular una venta, compra, gasto operativo
  o producción;
- `operator` recibe `403` al intentar corregir un conteo cerrado;
- `operator` recibe `403` al intentar crear una lista de precios;
- `operator` recibe `403` al consultar el panel gerencial o una exportación
  gerencial Excel.

La dependencia protege más endpoints que los cubiertos individualmente por esa
prueba. El Bloque 58D debe convertir la matriz aprobada completa en pruebas
parametrizadas positivas y negativas, sin depender solo de ejemplos.

### Restricciones solo de frontend

No se encontró una **mutación crítica** condicionada actualmente por rol en la
UI cuyo endpoint equivalente quede abierto al operador. Las correcciones,
anulaciones, ajustes, administración de precios, usuarios, gerencia y descargas
ocultas tienen respaldo backend.

Sin embargo:

- ocultar los cuatro enlaces administrativos es solo navegación; las páginas y
  endpoints deben seguir comprobando permiso;
- `/dashboard/pricing` bloquea la pantalla completa a `operator`, pero
  `GET /pricing/price-lists`, `GET /pricing/price-lists/{id}` y
  `GET /pricing/resolve` aceptan actualmente cualquier usuario autenticado;
- `/dashboard/operating-expenses` oculta las secciones de categorías y
  plantillas, pero sus endpoints `GET` de lista y detalle también aceptan
  actualmente a `operator`; las mutaciones sí son de administrador;
- el rol guardado en `localStorage` o leído del JWT solo sirve para presentación;
- varias capacidades que la propuesta considera sensibles no están restringidas
  ni en frontend ni en backend. Entre ellas están crear nómina, editar fórmulas,
  administrar empleados y ejecutar operaciones financieras u operativas que
  ahora son **A** o **F**. El cierre de caja sigue permitido, pero 58B debe
  completar su trazabilidad.

## Matriz propuesta por módulo y categoría

Esta tabla representa la política objetivo para `operator`, no el
comportamiento efectivo actual.

| Módulo o capacidad | Ver | Crear | Editar abierto | Cerrar | Corregir cerrado | Anular | Descargar | Administrar configuración |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dashboard operativo | **O** | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Caja / cash sessions | **O** | **T** | **T** | **T** | **A** | N/A | **A** | **A** |
| Conteo de denominaciones | **O** | N/A | **T** mientras caja esté abierta | N/A | **A** | N/A | **A** | N/A |
| Gastos de caja | **O** | **T** mientras caja esté abierta | N/A en el modelo actual | N/A | **A** mediante gasto correctivo | N/A en el modelo actual | **A** | N/A |
| Historial básico de cuadres | **O** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Correcciones y logs de cuadre | **A** | **A** | N/A | N/A | **A** | N/A | **A** | **A** |
| Clientes | **O** | **T** | **F** para editar datos básicos | N/A | N/A | **A** para desactivar | **A** | **A** para reglas crediticias |
| Productos | **O** | **A** | **A** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Precio resuelto durante venta | **O** | N/A | N/A | N/A | N/A | N/A | N/A | **A** |
| Listas e ítems de precios | **A** | **A** | **A** | N/A | N/A | **A** para activar/desactivar | **A** | **A** |
| Ventas de contado | **O** | **T** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Ventas a crédito | **O** | **T** | N/A en el modelo actual | N/A | N/A | **A** | **A** | **A** para límites y excepciones |
| Cobros / pagos de crédito | **O** | **T** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Cartera operativa | **O** | N/A | N/A | N/A | N/A | N/A | **A** | **A** para políticas de crédito |
| Rutas de entrega | **O** | **A** | **A** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Vehículos | **O** | **A** | **A** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Carga de camión | **O** | **F** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Retorno de ruta | **O** | **F** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Actividad comercial de ruta | **O** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Cierre financiero de ruta | **O** | N/A | N/A | **F** | N/A | **A** | **A** | N/A |
| Recepción de efectivo de ruta | **O** | **F** en caja abierta | N/A | N/A | N/A | **A** | **A** | N/A |
| Comparación ruta vs caja | **O** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Inventario y stock básico | **O** | **T** solo `entry`/`exit` | N/A | N/A | N/A | **A** | **A** | **A** para ubicaciones, `adjustment_in`/`adjustment_out` y costos |
| Producción diaria | **O** | **T** | N/A en el modelo actual | **F** para aplicar a inventario | N/A | **A** | **A** | N/A |
| Fórmulas de producción | **O** | **A** | **A** | N/A | N/A | **A** | **A** | **A** |
| Consumo de insumos | **O** | **F** | N/A en el modelo actual | N/A | N/A | **A** | **A** | **A** |
| Proveedores | **O** | **F** | **F** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Compras | **O** | **F** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Gastos operativos | **O** | **F** | **F** mientras estén activos | N/A | N/A | **A** | **A** | N/A |
| Categorías y plantillas de gastos | **O** para usar opciones activas | **A** | **A** | N/A | N/A | **A** para activar/desactivar | **A** | **A** |
| Empleados | **A** | **A** | **A** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Asistencia y control diario | **A** | **A** | **A** | N/A | N/A | N/A en el modelo actual | **A** | **A** |
| Anticipos, préstamos y abonos | **A** | **A** | N/A en el modelo actual | N/A | N/A | **A** | **A** | **A** |
| Nómina / roles de pago | **A** | **A** | N/A en el modelo actual | N/A en el modelo actual | N/A | **A** | **A** | **A** |
| Resumen diario operativo | **O** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Resumen mensual | **F** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Reporte acumulado de caja | **F** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Panel gerencial | **A** | N/A | N/A | N/A | N/A | N/A | **A** | **A** |
| Exportaciones Excel/PDF | **A** | N/A | N/A | N/A | N/A | N/A | **A** | **A** |
| Usuarios, contraseñas y roles | **A** | **A** | **A** | N/A | N/A | **A** para activar/desactivar | **A** | **A** |

## Permitido para `operator`

Las capacidades **O** son de consulta o uso operativo básico:

- iniciar sesión con cuenta personal y ver el dashboard operativo;
- ver el cuadre del día;
- ver historial y resumen básico de cuadres, sin logs ni herramientas de
  corrección;
- ver productos y resolver el precio aplicable durante una venta;
- consultar ventas de contado;
- ver cartera y estados de cuenta operativos;
- consultar actividad de ruta, cierres, recibos y comparación ruta vs caja;
- ver stock e inventario básico;
- ver producciones, fórmulas y consumos sin modificarlos cuando la acción esté
  reservada;
- ver proveedores, compras y gastos operativos necesarios para el trabajo
  asignado;
- ver el resumen diario operativo.

## Permitido para `operator` con trazabilidad obligatoria

Las capacidades **T** están aprobadas, pero 58B debe verificar que el backend
identifique al usuario y conserve la evidencia necesaria:

- abrir el cuadre del día;
- registrar o reemplazar cantidades del conteo mientras el cuadre esté abierto;
- registrar gastos de caja mientras el cuadre esté abierto;
- cerrar el cuadre diario; no puede reabrirlo ni corregirlo después;
- crear clientes y ventas de contado o a crédito;
- registrar cobros de ventas a crédito;
- registrar producción diaria, sin que esta decisión autorice aplicar la
  producción al inventario, consumir insumos, editar fórmulas o cambiar costos;
- registrar movimientos manuales operativos de inventario:
  - `entry`: entrada operativa;
  - `exit`: salida operativa;
- para inventario deben conservarse como mínimo usuario, fecha, producto,
  ubicación, tipo, cantidad, motivo o referencia y timestamp;
- `operator` no puede usar `adjustment_in` ni `adjustment_out`, anular
  movimientos, eliminar registros, administrar ubicaciones, editar costos ni
  alterar configuración.

Todos los permisos **O** y **T** continúan sujetos a reglas de estado,
validaciones de negocio y autenticación. “Con trazabilidad” no significa
“permitido sin límites”; significa que el backend autoriza la acción concreta y
registra quién la ejecutó.

## Permisos propuestos como exclusivos de `admin_auditor`

- administrar usuarios, contraseñas, activación y roles;
- acceder al panel gerencial;
- descargar cualquier Excel/PDF;
- crear, editar, activar o desactivar listas e ítems de precios;
- corregir cuadres cerrados y consultar sus logs de corrección;
- anular ventas, cobros, compras, gastos, movimientos, producciones, consumos,
  operaciones de ruta, anticipos, préstamos, abonos o roles de pago;
- registrar ajustes directos de inventario (`adjustment_in` y
  `adjustment_out`);
- anular o eliminar movimientos y administrar ubicaciones de inventario;
- crear o modificar fórmulas, insumos y costos;
- administrar categorías y plantillas de gastos;
- crear, editar o desactivar productos, rutas y vehículos;
- desactivar clientes, proveedores u otros datos maestros;
- acceder y gestionar empleados, asistencia, control laboral, anticipos,
  préstamos, abonos, nómina y roles de pago;
- cambiar políticas de crédito, límites o excepciones;
- ejecutar una acción **F** mientras no exista aprobación posterior para
  `operator`.

## Pendiente futuro

Las capacidades **F** no forman parte del permiso de `operator` para 58B. No
deben quedar abiertas por conservar el comportamiento actual:

- editar datos básicos de clientes;
- registrar carga, retorno, cierre o recepción de efectivo de ruta;
- aplicar producción al inventario;
- confirmar consumo de insumos;
- crear o editar proveedores;
- registrar compras;
- crear o editar gastos operativos fuera de caja;
- ver resumen mensual o reporte acumulado de caja;
- definir un posible directorio mínimo de empleados, separado de su gestión
  administrativa.

Una decisión futura podrá mover una capacidad **F** a **O**, **T** o **A** sin
reinterpretar las diez decisiones oficiales.

## Decisiones oficiales de George

Las diez decisiones principales están resueltas. “Sí” autoriza únicamente la
acción descrita y no permisos relacionados por proximidad.

| ID | Decisión oficial | Estado | Traducción para 58B |
| --- | --- | --- | --- |
| D-01 | El operador puede cerrar el cuadre diario. | **Resuelta: Sí** | Permiso **T** para cerrar. Sin reapertura ni corrección posterior. Registrar actor y timestamp. |
| D-02 | El operador puede corregir un cuadre cerrado. | **Resuelta: No** | Corrección y logs exclusivos de `admin_auditor`; petición directa del operador debe devolver `403`. |
| D-03 | El operador puede anular ventas. | **Resuelta: No** | Anulación exclusiva de `admin_auditor`; ocultar acción en frontend y proteger endpoint. |
| D-04 | El operador puede anular cobros. | **Resuelta: No** | Anulación exclusiva de `admin_auditor`; ocultar acción en frontend y proteger endpoint. |
| D-05 | El operador puede cambiar precios. | **Resuelta: No** | Listas, ítems, activación y cambios de precio son de administrador. El operador solo resuelve el precio vigente durante su flujo autorizado. |
| D-06 | El operador puede descargar Excel/PDF. | **Resuelta: No** | Todos los endpoints de exportación y sus controles visuales son de administrador. |
| D-07 | El operador puede ver el panel gerencial. | **Resuelta: No** | Página, navegación y endpoint gerencial exclusivos de administrador. |
| D-08 | El operador puede registrar producción diaria. | **Resuelta: Sí** | Permiso **T** para crear la producción. No incluye aplicar a inventario, consumir insumos, anular, editar fórmulas ni cambiar costos. |
| D-09 | El operador puede modificar inventario manualmente. | **Resuelta: Sí, con límite** | Permiso **T** solo para movimientos operativos `entry` y `exit`. Ajustes, anulaciones, eliminaciones, costos, fórmulas, ubicaciones y configuración permanecen en administrador. |
| D-10 | El operador puede gestionar empleados, anticipos, préstamos o nómina. | **Resuelta: No** | Pantallas y endpoints de gestión de empleados, control laboral, anticipos, préstamos, abonos y nómina deben ser de `admin_auditor`. |

## Decisiones no cubiertas y pendientes futuras

Estas preguntas ya no bloquean la definición del núcleo de 58B porque su regla
provisional es denegar a `operator`:

| ID | Pendiente futuro | Regla para 58B |
| --- | --- | --- |
| F-01 | ¿El operador puede registrar ventas a crédito? | **Resuelta para 58B: Sí**, con trazabilidad; anulación administrativa. |
| F-02 | ¿El operador puede registrar cobros? | **Resuelta para 58B: Sí**, con trazabilidad; D-04 mantiene la anulación administrativa. |
| F-03 | ¿El operador puede ver resumen mensual o reporte acumulado de caja? | Mantener fuera del rol hasta clasificar la sensibilidad. |
| F-04 | ¿El operador puede registrar compras? | No conceder hasta definir costos, documentos y responsable. |
| F-05 | ¿El operador puede aplicar producción al inventario? | No conceder; D-08 solo autoriza registrar producción diaria. |
| F-06 | ¿El operador puede confirmar consumo de insumos? | No conceder; vista previa/confirmación/reversión deben separarse. |
| F-07 | ¿El operador puede crear o editar proveedores y datos básicos de clientes? | Alta de cliente permanece aprobada; otras ediciones quedan pendientes. |
| F-08 | ¿El operador puede crear o editar gastos operativos fuera de caja? | No conceder hasta definir categorías, monto, fecha y comprobante. |
| F-09 | ¿Qué operaciones de ruta pertenecen al operador de oficina? | No conceder carga, retorno, cierre ni recepción como permiso genérico. |
| F-10 | ¿Una diferencia de caja bloquea el cierre del operador? | Mantener las reglas actuales hasta definir umbral y escalamiento; D-01 autoriza el cierre, no una corrección. |
| F-11 | ¿El operador necesita un directorio mínimo de empleados para otro flujo? | La gestión completa sigue prohibida por D-10; cualquier lectura mínima deberá diseñarse aparte. |

## Diferencias entre el estado actual y la propuesta

Estas diferencias son el insumo prioritario para 58B y 58C:

| Capacidad | Estado actual de `operator` | Política documentada para 58B |
| --- | --- | --- |
| Cerrar cuadre | Permitido en backend y frontend; falta confirmar trazabilidad del cierre | Permitido **T**; registrar actor y timestamp. |
| Corregir cuadre cerrado | Backend y frontend ya restringidos | Mantener exclusivo de administrador. |
| Anular ventas y cobros | Backend y frontend ya restringidos | Mantener exclusivo de administrador. |
| Cambiar precios | Mutaciones backend y pantalla restringidas; lecturas API tienen diferencias visuales | Mantener administración exclusiva; revisar lecturas necesarias para resolver precios. |
| Descargar Excel/PDF | Backend y frontend ya restringidos | Mantener todas las descargas en administrador. |
| Ver panel gerencial | Backend y frontend ya restringidos | Mantener exclusivo de administrador. |
| Registrar producción diaria | Permitido | Mantener permitido **T**; separar aplicación a inventario y consumo. |
| Aplicar producción a inventario | Permitido | Denegar a `operator` como **F** hasta decisión futura. |
| Crear movimientos `entry`/`exit` | Permitido y conserva `created_by` | Mantener permitido **T**; no admitir cambios de costo. |
| Crear `adjustment_in`/`adjustment_out` | Backend y frontend ya restringidos | Mantener exclusivo de administrador. |
| Anular movimientos de inventario | Backend y frontend ya restringidos | Mantener exclusivo de administrador. |
| Gestionar empleados y asistencia | Permitido actualmente | Cerrar brecha: exclusivo de administrador. |
| Registrar anticipos, préstamos y abonos | Permitido actualmente | Cerrar brecha: exclusivo de administrador. |
| Crear roles de pago y ver nómina | Permitido actualmente | Cerrar brecha: exclusivo de administrador. |
| Crear/editar/activar fórmulas e ítems | Permitido actualmente | Cerrar brecha: exclusivo de administrador. |
| Editar/desactivar clientes | Permitido actualmente | Edición **F**; desactivación administrador. |
| Crear/editar/desactivar productos | Permitido actualmente | Administrador; operador solo consulta. |
| Crear/editar/desactivar rutas y vehículos | Permitido actualmente | Administrador; operador solo consulta. |
| Crear/editar/desactivar proveedores | Permitido actualmente | Alta/edición **F**; desactivación administrador. |
| Registrar compras | Permitido actualmente | **F**; denegar a operador hasta decisión futura. |
| Crear/editar gastos operativos | Permitido actualmente | **F**; denegar a operador hasta decisión futura. |
| Confirmar consumo de insumos | Permitido actualmente | **F**; denegar a operador hasta decisión futura. |
| Carga, retorno, cierre y recibo de ruta | Permitido actualmente | **F**; decidir cada operación por separado. |
| Ver resumen mensual y reporte acumulado | Permitido actualmente | **F** hasta clasificación operativa/financiera. |

No se debe resolver esta brecha ocultando controles antes de proteger el
backend.

## Base de alcance para 58B

58B debe auditar cada ruta exacta, pero puede partir de este mapa:

| Grupo backend | Política objetivo |
| --- | --- |
| `POST /cash-sessions/{id}/close` | Permitir a `operator` con trazabilidad de actor y timestamp. |
| Correcciones bajo `/cash-sessions/{id}/corrections` | Mantener `admin_auditor`; `operator` recibe `403`. |
| `POST /sales/{id}/void` y `POST /credit-payments/{id}/void` | Mantener `admin_auditor`; `operator` recibe `403`. |
| Mutaciones bajo `/pricing` | Mantener `admin_auditor`. |
| Lecturas `/pricing/price-lists*` frente a `/pricing/resolve` | Restringir la administración/listado sensible; conservar al operador únicamente la resolución de precio necesaria para un flujo autorizado. |
| `/reports/management-dashboard` y `/reports/exports/*` | Mantener `admin_auditor`. |
| `POST /production/batches` | Permitir a `operator` con `created_by` y datos del lote. |
| `/production/batches/{id}/apply-inventory` | Denegar a `operator` como pendiente **F**. |
| Mutaciones de fórmulas e ítems bajo `/production/recipes` | Restringir a `admin_auditor`, no solo la anulación. |
| Confirmación de consumo de insumos | Denegar a `operator` como pendiente **F**; la anulación sigue en administrador. |
| `POST /inventory/movements` con `entry` o `exit` | Permitir a `operator` con `created_by`, motivo/referencia y sin aceptar cambios de costo. |
| `POST /inventory/movements` con `adjustment_in` o `adjustment_out` | Mantener `admin_auditor`. |
| Anulación de movimiento y mutaciones de ubicaciones | Restringir a `admin_auditor`. |
| `/employees`, controles laborales y `/payroll` | Restringir gestión, datos sensibles y escrituras a `admin_auditor`; cualquier lectura mínima futura requerirá un diseño separado. |
| Crear venta a crédito o cobro | Permitir a `operator` con trazabilidad; las anulaciones siguen siendo administrativas. |
| Mutaciones de compras, gastos operativos y proveedores | Denegar a `operator` como pendiente **F**, salvo configuraciones que ya son administrativas. |
| Mutaciones de carga, retorno, cierre y recibo de ruta | Denegar a `operator` como pendiente **F**; mantener consultas operativas aprobadas. |
| Mutaciones de productos, rutas y vehículos | Restringir a `admin_auditor` según la matriz. |
| Resumen mensual y reporte acumulado | Denegar a `operator` como pendiente **F**; mantener resumen diario operativo. |

Orden obligatorio:

1. proteger o permitir explícitamente el endpoint en backend;
2. probar petición directa con ambos roles;
3. ocultar o deshabilitar la acción en frontend;
4. volver a probar que manipular la UI no evita el `403`.

## Riesgos

| Riesgo | Impacto | Tratamiento recomendado |
| --- | --- | --- |
| Regla backend demasiado amplia para endpoints no marcados como críticos | `operator` puede ejecutar acciones sensibles por petición directa | Aplicar permisos explícitos en 58B y denegar por defecto las capacidades no aprobadas. |
| Guardas frontend repetidas por página | Una pantalla futura puede omitir o interpretar distinto el rol | Centralizar capacidades en 58C sin convertir el frontend en autoridad. |
| Rol almacenado en navegador | El usuario puede alterar la presentación local | Validar siempre en backend; usar el rol cliente solo para UX. |
| Confundir “cerrar”, “corregir” y “anular” | Un permiso amplio puede permitir cambios irreversibles | Usar permisos separados por verbo y estado. |
| Permiso por módulo demasiado genérico | Autorizar “rutas” o “inventario” abriría acciones con riesgos muy distintos | Definir claves por acción, no un único booleano por módulo. |
| Falta de alcance por registro | Un operador autorizado podría ver o cambiar registros fuera de su turno, ruta o ubicación | Evaluar alcance por fecha, ruta, ubicación o autor en una fase posterior si George lo necesita. |
| Información financiera y laboral sensible | Exposición de márgenes, nómina, deudas o anticipos | Mantener gerencia, exportaciones y nómina en administrador; decidir vistas operativas mínimas. |
| Datos maestros con efecto futuro | Cambiar producto, ruta, proveedor o cliente altera operaciones posteriores | Separar lectura, alta, edición y desactivación; auditar cambios sensibles. |
| Cobros y cierres sin reversión del operador | Un error operativo requerirá a George | Mantener un procedimiento de escalamiento claro y corrección trazable. |
| Cobertura de pruebas parcial | Una dependencia puede retirarse o una ruta nueva quedar abierta | Generar pruebas parametrizadas desde la matriz aprobada. |
| Trazabilidad desigual | No todos los CRUD de datos maestros tienen necesariamente el mismo actor/motivo que las operaciones anulables | Auditar campos y logs en 58B antes de permitir edición al operador. |
| Cambio de política sin aprobación | La implementación podría ampliar el rol sin decisión de George | Denegar a `operator` toda celda **F** hasta registrar una decisión posterior. |

## Estrategia técnica para implementación futura

### Opción A: permisos fijos por rol en código

Una tabla central define capacidades como:

```text
cash_session.view
cash_session.create
cash_session.close
cash_session.correct_closed
sale.cash.create
sale.credit.create
sale.void
inventory.movement.operational.create
inventory.adjust
production.batch.create
production.inventory.apply
employee.manage
report.management.view
report.export
user.manage
```

El backend asocia esas capacidades a `operator` y `admin_auditor`; el frontend
usa la misma nomenclatura o una proyección equivalente para adaptar la
interfaz.

Ventajas:

- implementación más simple y rápida;
- no requiere migraciones;
- menor superficie administrativa;
- suficiente para el MVP interno y dos roles.

Desventajas:

- menos flexible;
- un cambio de política requiere desplegar código;
- no permite perfiles distintos entre dos operadores con el mismo rol.

### Opción B: permisos configurables por usuario o perfil en base de datos

Los permisos se almacenan y administran como perfiles, asignaciones o
excepciones por usuario.

Ventajas:

- permite configurar actividades específicas;
- soporta varios puestos operativos;
- puede limitar capacidades sin crear nuevos despliegues.

Desventajas:

- requiere migraciones y modelo de datos;
- exige pantalla administrativa segura;
- aumenta combinaciones de prueba y riesgo de configuraciones contradictorias;
- necesita auditoría de cambios de permisos y reglas de precedencia;
- es innecesariamente compleja mientras existan solo dos perfiles reales.

### Recomendación

Empezar con la **Opción A**:

1. tomar las diez decisiones oficiales como alcance aprobado;
2. definir claves de permiso fijas por acción;
3. aplicar primero la autorización en backend;
4. ajustar después la interfaz;
5. probar cada combinación `operator`/`admin_auditor`;
6. evolucionar a la Opción B solo si Agua Activa necesita operadores con
   funciones diferentes.

La implementación debería:

- denegar por defecto una capacidad no declarada;
- conservar `401` para falta de autenticación y `403` para falta de permiso;
- comprobar permisos antes de ejecutar servicios o iniciar transacciones;
- mantener las reglas de estado además del permiso;
- registrar usuario y motivo en toda acción crítica;
- evitar depender del texto de un botón o de la ruta frontend;
- exponer a la UI únicamente capacidades derivadas de una sesión autenticada;
- incluir cada endpoint nuevo en una prueba de permisos.

## Bloques futuros

### 58B - Permisos backend para acciones críticas

- convertir la matriz aprobada en capacidades fijas;
- aplicar dependencias o comprobaciones centrales;
- cerrar primero las brechas actuales;
- conservar control total de `admin_auditor`;
- implementar las capacidades **T** con actor y evidencia;
- denegar a `operator` todas las celdas **F**;
- proteger primero backend y solo después ajustar visibilidad frontend.

### 58C - Ajuste frontend por permisos

- ocultar o deshabilitar destinos y acciones según capacidades;
- centralizar el consumo del rol/permisos;
- mostrar un estado de acceso denegado coherente;
- mantener el backend como autoridad.

### 58D - Pruebas por rol

- pruebas positivas y negativas para cada capacidad;
- petición directa a endpoints, no solo prueba visual;
- estados abierto/cerrado/activo/anulado;
- comprobación de `401`, `403` y ausencia de efectos laterales;
- regresión completa para `admin_auditor`.

### 58E - Documentación operativa

- guía del operador;
- procedimiento de escalamiento a George;
- ejemplos de tareas permitidas y prohibidas;
- manejo de errores, correcciones y anulaciones.

### Futuro

Evaluar permisos configurables por usuario o perfil únicamente si existen
puestos operativos distintos que no puedan representarse con los dos roles
actuales.

## Criterios de aceptación para la implementación

La implementación de 58B a 58D podrá considerarse cerrada cuando:

1. las diez decisiones oficiales estén implementadas y toda capacidad **F**
   permanezca denegada a `operator`;
2. cada capacidad tenga una clave única y un dueño funcional;
3. `admin_auditor` conserve acceso total;
4. `operator` pueda ejecutar todas las tareas diarias aprobadas;
5. `operator` reciba `403` en toda acción restringida mediante petición directa;
6. la denegación ocurra antes de cualquier escritura o efecto lateral;
7. las reglas de estado abierto/cerrado y activo/anulado sigan vigentes;
8. correcciones, anulaciones y acciones sensibles conserven usuario y motivo;
9. frontend y backend coincidan, sin depender del frontend para seguridad;
10. las páginas administrativas no carguen datos para `operator`;
11. reportes y descargas estén clasificados individualmente;
12. exista cobertura automatizada por rol para todos los grupos de endpoints;
13. las pruebas demuestren que una nueva ruta no queda permitida por omisión;
14. no se requiera migración para la Opción A;
15. la matriz efectiva y la guía operativa se actualicen después de aprobar las
    pruebas;
16. cierre de caja, producción diaria y movimientos operativos registren actor
    y timestamp;
17. `operator` solo pueda crear `entry`/`exit` y no pueda enviar costos,
    `adjustment_in`, `adjustment_out` ni anular movimientos;
18. gestión de empleados, control laboral, anticipos, préstamos, abonos y
    nómina devuelvan `403` a `operator`;
19. frontend oculte las acciones restringidas únicamente después de comprobar
    su protección backend.

## Criterios de cierre del Bloque 58A

- [x] Se inventariaron las 36 páginas bajo `apps/web/app/dashboard`.
- [x] Se inventariaron las familias de endpoints y sus controles actuales.
- [x] Se distinguieron guardas frontend y autorización backend.
- [x] Se documentaron acciones que hoy devuelven `403`.
- [x] Se propuso una clasificación por módulo y categoría.
- [x] Se marcaron como resueltas las diez decisiones oficiales de George.
- [x] Se documentó el límite de inventario manual a `entry`/`exit`, sin
  ajustes, anulaciones, eliminaciones, costos, fórmulas ni configuración.
- [x] Se separaron permitidos, permitidos con trazabilidad, restringidos y
  pendientes futuros.
- [x] Se compararon las opciones técnica A y B.
- [x] Se recomienda empezar con permisos fijos por rol.
- [x] Se definieron los bloques 58B a 58E y criterios de aceptación.
- [x] Este bloque no implementa ni cambia permisos.
