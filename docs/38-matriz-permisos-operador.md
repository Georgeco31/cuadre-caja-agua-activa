# 38 - Matriz de permisos granulares del operador

## Estado y alcance

- Bloque: **58A**.
- Estado: **propuesta documental pendiente de aprobación de George**.
- Fecha de corte: **2026-07-28**.
- Alcance: inventario de pantallas, endpoints y permisos existentes; propuesta
  de permisos granulares para `operator`; riesgos y estrategia futura.
- Fuera de alcance: cambios de backend, frontend, rutas, endpoints,
  autenticación, migraciones, seeds, base de datos, variables de entorno o
  lógica de negocio.

Este documento no concede ni revoca permisos. La matriz efectiva que refleja
el Bloque 54 continúa en
[`22-matriz-permisos-roles.md`](22-matriz-permisos-roles.md) hasta que George
apruebe las decisiones pendientes y los bloques 58B a 58D implementen y prueben
la nueva política.

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

La matriz de este documento usa cuatro clasificaciones:

| Código | Clasificación |
| --- | --- |
| **O** | Permitido para `operator`. |
| **A** | Restringido a `admin_auditor`. |
| **G** | Pendiente de decisión de George. Mientras no se decida e implemente, debe mantenerse el comportamiento actual; para el despliegue de la matriz nueva se recomienda denegar por defecto al operador. |
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

`admin_auditor` conserva todas las capacidades marcadas **O**, **A** o **G**.
Las celdas **G** solo mantienen pendiente el acceso de `operator`.

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
- el cierre de cuadre continúa permitido a `operator`;
- el operador también conserva hoy acceso backend a varios flujos que la
  política nueva debe decidir: nómina, fórmulas, datos maestros, compras,
  producción, consumo de insumos, movimientos normales de inventario y
  operaciones de ruta;
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
  ni en frontend ni en backend. Entre ellas están cerrar caja, crear nómina,
  editar fórmulas, administrar varios datos maestros y ejecutar operaciones
  financieras u operativas aún pendientes de George.

## Matriz propuesta por módulo y categoría

Esta tabla representa la política objetivo para `operator`, no el
comportamiento efectivo actual.

| Módulo o capacidad | Ver | Crear | Editar abierto | Cerrar | Corregir cerrado | Anular | Descargar | Administrar configuración |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dashboard operativo | **O** | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Caja / cash sessions | **O** | **O** | **O** | **G** | **A** | N/A | **A** | **A** |
| Conteo de denominaciones | **O** | N/A | **O** mientras caja esté abierta | N/A | **A** | N/A | **A** | N/A |
| Gastos de caja | **O** | **O** mientras caja esté abierta | N/A en el modelo actual | N/A | **A** mediante gasto correctivo | N/A en el modelo actual | **A** | N/A |
| Historial básico de cuadres | **O** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Correcciones y logs de cuadre | **A** | **A** | N/A | N/A | **A** | N/A | **A** | **A** |
| Clientes | **O** | **O** | **G** para datos básicos sin saldos | N/A | N/A | **A** para desactivar | **A** | **A** para reglas crediticias |
| Productos | **O** | **A** | **A** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Precio resuelto durante venta | **O** | N/A | N/A | N/A | N/A | N/A | N/A | **A** |
| Listas e ítems de precios | **A** | **A** | **A** | N/A | N/A | **A** para activar/desactivar | **A** | **A** |
| Ventas de contado | **O** | **O** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Ventas a crédito | **O** | **G** | N/A en el modelo actual | N/A | N/A | **A** | **A** | **A** para límites y excepciones |
| Cobros / pagos de crédito | **O** | **G** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Cartera operativa | **O** | N/A | N/A | N/A | N/A | N/A | **A** | **A** para políticas de crédito |
| Rutas de entrega | **O** | **A** | **A** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Vehículos | **O** | **A** | **A** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Carga de camión | **O** | **G** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Retorno de ruta | **O** | **G** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Actividad comercial de ruta | **O** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Cierre financiero de ruta | **O** | N/A | N/A | **G** | N/A | **A** | **A** | N/A |
| Recepción de efectivo de ruta | **O** | **G** en caja abierta | N/A | N/A | N/A | **A** | **A** | N/A |
| Comparación ruta vs caja | **O** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Inventario y stock básico | **O** | **G** para movimiento normal | N/A | N/A | N/A | **A** | **A** | **A** para ubicaciones y ajustes directos |
| Producción diaria | **O** | **G** | N/A en el modelo actual | **G** para aplicar a inventario | N/A | **A** | **A** | N/A |
| Fórmulas de producción | **O** | **A** | **A** | N/A | N/A | **A** | **A** | **A** |
| Consumo de insumos | **O** | **G** | N/A en el modelo actual | N/A | N/A | **A** | **A** | **A** |
| Proveedores | **O** | **G** | **G** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Compras | **O** | **G** | N/A en el modelo actual | N/A | N/A | **A** | **A** | N/A |
| Gastos operativos | **O** | **G** | **G** mientras estén activos | N/A | N/A | **A** | **A** | N/A |
| Categorías y plantillas de gastos | **O** para usar opciones activas | **A** | **A** | N/A | N/A | **A** para activar/desactivar | **A** | **A** |
| Empleados | **G** | **G** | **G** | N/A | N/A | **A** para desactivar | **A** | **A** |
| Asistencia y control diario | **O** | **G** | **G** | N/A | N/A | N/A en el modelo actual | **A** | **A** |
| Anticipos, préstamos y abonos | **G** | **G** | N/A en el modelo actual | N/A | N/A | **A** | **A** | **A** |
| Nómina / roles de pago | **A** | **A** | N/A en el modelo actual | N/A en el modelo actual | N/A | **A** | **A** | **A** |
| Resumen diario operativo | **O** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Resumen mensual | **G** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Reporte acumulado de caja | **G** | N/A | N/A | N/A | N/A | N/A | **A** | N/A |
| Panel gerencial | **A** | N/A | N/A | N/A | N/A | N/A | **A** | **A** |
| Exportaciones Excel/PDF | **A** | N/A | N/A | N/A | N/A | N/A | **A** | **A** |
| Usuarios, contraseñas y roles | **A** | **A** | **A** | N/A | N/A | **A** para activar/desactivar | **A** | **A** |

## Permisos propuestos como permitidos para `operator`

No requieren una decisión adicional si George acepta la matriz como conjunto:

- iniciar sesión con cuenta personal y ver el dashboard operativo;
- ver, abrir y trabajar el cuadre del día;
- registrar o reemplazar cantidades del conteo mientras el cuadre esté abierto;
- registrar gastos de caja mientras el cuadre esté abierto;
- ver historial y resumen básico de cuadres, sin logs ni herramientas de
  corrección;
- crear clientes;
- ver productos y resolver el precio aplicable durante una venta;
- crear y consultar ventas de contado;
- ver cartera y estados de cuenta operativos;
- consultar actividad de ruta, cierres, recibos y comparación ruta vs caja;
- ver stock e inventario básico;
- ver producciones, fórmulas y consumos sin modificarlos cuando la acción esté
  reservada;
- ver proveedores, compras y gastos operativos necesarios para el trabajo
  asignado;
- ver y registrar la operación diaria únicamente en las capacidades que George
  apruebe en la sección pendiente;
- ver el resumen diario operativo.

Todos los permisos deben continuar sujetos a reglas de estado, validaciones de
negocio y registro del usuario autenticado.

## Permisos propuestos como exclusivos de `admin_auditor`

- administrar usuarios, contraseñas, activación y roles;
- acceder al panel gerencial;
- descargar Excel/PDF hasta que exista una clasificación separada de
  exportaciones operativas no sensibles;
- crear, editar, activar o desactivar listas e ítems de precios;
- corregir cuadres cerrados y consultar sus logs de corrección;
- anular ventas, cobros, compras, gastos, movimientos, producciones, consumos,
  operaciones de ruta, anticipos, préstamos, abonos o roles de pago;
- hacer ajustes directos de inventario;
- administrar ubicaciones de inventario;
- crear o modificar fórmulas y sus insumos;
- administrar categorías y plantillas de gastos;
- crear, editar o desactivar productos, rutas y vehículos;
- desactivar clientes, proveedores, empleados u otros datos maestros;
- gestionar nómina y roles de pago;
- cambiar políticas de crédito, límites o excepciones;
- ejecutar una acción pendiente cuando George no la haya aprobado
  expresamente para `operator`.

## Decisiones pendientes de George

George debe responder estas preguntas antes de implementar 58B. La columna
“recomendación inicial” aplica el principio de mínimo privilegio sin impedir la
operación diaria.

| ID | Pregunta | Recomendación inicial |
| --- | --- | --- |
| G-01 | ¿El operador puede cerrar el cuadre diario? | **Sí**, si el cierre no puede reabrirse y toda corrección posterior sigue siendo de administrador. Confirmar si una diferencia de caja exige aprobación de George. |
| G-02 | ¿El operador puede corregir un cuadre cerrado o ver sus logs? | **No**. Mantener en administrador. |
| G-03 | ¿El operador puede anular ventas? | **No**. Mantener en administrador con motivo y usuario. |
| G-04 | ¿El operador puede registrar ventas a crédito? | **Sí**, solo con cliente activo, límite vigente y sin capacidad de sobrepasar o cambiar el límite. |
| G-05 | ¿El operador puede registrar cobros? | **Sí**, sin anularlos ni cambiar su aplicación después del registro. |
| G-06 | ¿El operador puede cambiar precios o listas de precios? | **No**. Solo debe resolver y usar el precio vigente. |
| G-07 | ¿El operador puede descargar algún Excel/PDF? | **No por ahora**. Si se necesita, definir una lista separada de exportaciones operativas, rango máximo y datos excluidos. |
| G-08 | ¿El operador puede ver el resumen mensual o el reporte acumulado de caja? | Definir si son operativos o financieros. **Restringir inicialmente** hasta clasificar sus indicadores. |
| G-09 | ¿El operador puede registrar compras? | **Pendiente**. Si se permite, no debe anular, cambiar costos cerrados ni recibir inventario implícitamente. |
| G-10 | ¿El operador puede modificar inventario? | Permitir solo movimientos normales expresamente definidos; **nunca** ajustes directos ni anulaciones. George debe listar los tipos autorizados. |
| G-11 | ¿El operador puede registrar producción y aplicarla a inventario? | **Pendiente**. Puede habilitarse si forma parte de su puesto, con actor, lote y ubicación obligatorios. |
| G-12 | ¿El operador puede consumir insumos? | **Pendiente**. Separar vista previa de confirmación; la reversión debe seguir en administrador. |
| G-13 | ¿El operador puede manejar anticipos, préstamos y abonos de empleados? | **No inicialmente**, por sensibilidad financiera y laboral. |
| G-14 | ¿El operador puede registrar o modificar asistencia? | **Pendiente según puesto**; definir ventana de edición y quién corrige días anteriores. |
| G-15 | ¿El operador puede crear o editar empleados, proveedores y datos básicos de clientes? | Clientes: permitir alta y decidir campos editables. Empleados/proveedores: **restringir inicialmente** hasta definir campos y responsable. |
| G-16 | ¿El operador puede crear o editar gastos operativos fuera de caja? | **Pendiente**. Definir categorías, monto máximo, fecha editable y si requiere comprobante. |
| G-17 | ¿Qué operaciones de ruta pertenecen al operador de oficina? | Marcar por separado carga, retorno, cierre y recepción de efectivo. No aprobarlas como un único permiso genérico. |
| G-18 | ¿El operador puede crear movimientos normales de inventario? | Definir tipos, ubicaciones y motivos admitidos. Transferencia, entrada y salida pueden requerir políticas distintas. |
| G-19 | ¿El operador puede editar datos básicos de un cliente? | Definir una lista de campos segura. Cupo, saldo, política de crédito y desactivación deben quedar fuera. |
| G-20 | ¿Una diferencia de caja o ruta bloquea el cierre del operador? | Definir umbral, mensaje y escalamiento; no implementar una aprobación implícita. |

## Diferencias entre el estado actual y la propuesta

Estas diferencias son el insumo prioritario para 58B y 58C:

| Capacidad | Estado actual de `operator` | Propuesta |
| --- | --- | --- |
| Cerrar cuadre | Permitido en backend y frontend | Pendiente G-01. |
| Editar/desactivar clientes | Permitido | Edición básica pendiente; desactivación administrador. |
| Crear/editar/desactivar productos | Permitido | Administrador; operador solo consulta. |
| Crear/editar/desactivar rutas y vehículos | Permitido | Administrador; operador solo consulta. |
| Crear/editar/desactivar proveedores | Permitido | Alta/edición pendiente; desactivación administrador. |
| Crear/editar/desactivar empleados | Permitido | Pendiente; desactivación administrador. |
| Crear/editar/activar fórmulas e ítems | Permitido | Administrador. |
| Crear roles de pago y ver nómina | Permitido | Administrador. |
| Registrar anticipos, préstamos y abonos | Permitido | Pendiente; recomendación inicial restrictiva. |
| Registrar compras | Permitido | Pendiente. |
| Crear/editar gastos operativos | Permitido | Pendiente. |
| Registrar/aplicar producción | Permitido | Pendiente. |
| Confirmar consumo de insumos | Permitido | Pendiente. |
| Crear movimientos normales de inventario | Permitido | Pendiente por tipo; ajuste directo sigue restringido. |
| Carga, retorno, cierre y recibo de ruta | Permitido | Decidir cada operación por separado. |
| Ver resumen mensual y reporte acumulado | Permitido | Pendiente de clasificación operativa/financiera. |

No se debe resolver esta brecha ocultando controles antes de proteger el
backend.

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
| Cambio de política sin aprobación | La implementación podría decidir por George | Bloquear 58B para toda celda **G** hasta registrar la respuesta. |

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
inventory.movement.create
inventory.adjust
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

1. aprobar esta matriz;
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
- no cambiar celdas **G** sin decisión registrada.

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

1. George haya respondido todas las decisiones que afecten el alcance;
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
    pruebas.

## Criterios de cierre del Bloque 58A

- [x] Se inventariaron las 36 páginas bajo `apps/web/app/dashboard`.
- [x] Se inventariaron las familias de endpoints y sus controles actuales.
- [x] Se distinguieron guardas frontend y autorización backend.
- [x] Se documentaron acciones que hoy devuelven `403`.
- [x] Se propuso una clasificación por módulo y categoría.
- [x] Se identificaron decisiones pendientes de George.
- [x] Se compararon las opciones técnica A y B.
- [x] Se recomienda empezar con permisos fijos por rol.
- [x] Se definieron los bloques 58B a 58E y criterios de aceptación.
- [x] Este bloque no implementa ni cambia permisos.
