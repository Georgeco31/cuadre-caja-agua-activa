# 40 - Bloque 58C: permisos del operador en frontend

## Objetivo

Alinear la interfaz con la política efectiva del backend implementada en 58B:
`operator` debe ver y usar únicamente las tareas aprobadas, mientras
`admin_auditor` conserva el control total.

La interfaz no sustituye la autorización. Ocultar un enlace o un botón evita
ofrecer una operación que terminaría en `403`, pero el backend de 58B continúa
siendo la frontera de seguridad.

Fecha de validación: **2026-07-28**.

## Relación con 58B

58B dejó protegidas las familias sensibles y aprobó 42 pruebas específicas por
rol, además de la suite backend completa con 972 pruebas. Este bloque no cambió
backend, rutas API, endpoints, payloads, cálculos, autenticación, roles,
migraciones, seeds, Docker, scripts ni variables productivas.

58C se limitó a presentación frontend y documentación:

- reutiliza el rol ya almacenado por el flujo de autenticación;
- centraliza la lista de rutas administrativas del dashboard;
- bloquea el montaje de una pantalla restringida cuando el rol es `operator`;
- adapta las acciones dentro de pantallas mixtas;
- conserva todas las operaciones que la política permite.

## Política frontend centralizada

`apps/web/lib/frontendPermissions.ts` concentra dos decisiones simples:

- si el rol puede usar acciones administrativas;
- si el rol puede abrir una ruta del dashboard.

`apps/web/app/dashboard/layout.tsx` espera a resolver el rol y, para
`operator`, reemplaza una ruta restringida por un mensaje claro antes de montar
su contenido. Esto evita también solicitudes de datos originadas por el
componente administrativo.

Las rutas completas reservadas a `admin_auditor` son:

- `/dashboard/employees` y sus rutas hijas, incluido control laboral;
- `/dashboard/payroll`;
- `/dashboard/pricing`;
- `/dashboard/production/recipes`;
- `/dashboard/production/material-consumption`;
- `/dashboard/reports`;
- `/dashboard/monthly-summary`;
- `/dashboard/management`;
- `/dashboard/exports`;
- `/dashboard/users`.

La respuesta visual usa lenguaje operativo:

> Esta sección está disponible solo para administrador/auditor.

También orienta a solicitar autorización a George y ofrece volver al panel
operativo. No muestra términos internos como `Forbidden`, `role mismatch` o
`admin_auditor required`.

## Dashboard y navegación

El dashboard, la navegación lateral y la navegación móvil usan la misma
decisión de acceso.

| Rol | Destinos visibles | Comportamiento |
| --- | ---: | --- |
| `admin_auditor` | 33 | Conserva todos los módulos y la navegación a reportes. |
| `operator` | 22 | Conserva módulos operativos y no recibe enlaces administrativos. |

El conteo de operador baja de 29 a 22 porque 58C incorpora siete restricciones
visuales que antes no se reflejaban en las tarjetas: empleados, control laboral,
nómina, fórmulas de producción, consumo de insumos, resumen acumulado y reporte
mensual. Sumadas a precios, usuarios, gerencia y exportaciones, son once
destinos reservados de los 33 totales.

Las descripciones de tarjetas mixtas también reflejan el acceso real: para el
operador, compras, gastos operativos, rutas, vehículos, proveedores, cargas,
retornos y cierres se presentan como consultas cuando su mutación está
reservada.

## Pantallas ajustadas

### Acciones ocultadas para `operator`

- **Caja histórica:** correcciones de cuadres cerrados, correcciones de
  conteos/gastos y logs administrativos sensibles permanecen fuera de la vista.
- **Ventas y cartera:** no se muestran anulaciones de ventas de contado,
  ventas a crédito ni cobros.
- **Productos:** alta, edición, clasificación, activación, desactivación y
  costos estimados.
- **Rutas y vehículos:** alta, edición, cambio de estado y formularios de
  cargas, retornos, cierres o recibos de efectivo; las anulaciones siguen
  ocultas.
- **Proveedores y compras:** alta o edición de proveedores, registro de compras
  y anulación de compras.
- **Gastos operativos:** creación/edición de gastos, categorías, plantillas
  recurrentes y anulaciones.
- **Producción:** aplicación a inventario, anulaciones, fórmulas, costos y
  consumo de insumos.
- **Inventario:** ubicaciones, ajustes, costos unitarios/totales y anulación de
  movimientos.
- **Administración:** precios, usuarios, empleados, control laboral, anticipos,
  préstamos, nómina, gerencia, reportes acumulados y exportaciones.

En las listas de productos, clientes, vehículos, rutas y ubicaciones se elimina
también la columna de acciones cuando no existe ninguna acción permitida.

### Acciones conservadas para `operator`

- ver el dashboard operativo;
- abrir o crear el cuadre diario;
- registrar conteo y gastos de caja;
- cerrar el cuadre diario;
- consultar historial básico;
- crear clientes y consultarlos;
- registrar ventas de contado y a crédito;
- registrar cobros y consultar cartera;
- consultar productos;
- registrar producción diaria;
- consultar stock y registrar movimientos `entry`/`exit` sin costo;
- consultar los demás módulos operativos aprobados.

En inventario, el selector del operador solo ofrece `Entrada` y `Salida`; el
payload continúa usando el contrato existente y envía costo nulo. La validación
de cliente rechaza además cualquier tipo diferente si se intentara introducir
por un estado inconsistente.

### Comportamiento de `admin_auditor`

El administrador/auditor conserva:

- 33 destinos en el dashboard;
- navegación a reportes en escritorio y móvil;
- panel gerencial, exportaciones, usuarios y listas de precios;
- empleados, control laboral y nómina;
- fórmulas, consumo de insumos y aplicación de producción;
- altas, ediciones, ajustes, costos, anulaciones y demás acciones
  administrativas existentes;
- descargas Excel y PDF.

## Validación manual por rol

La prueba se ejecutó contra una API temporal, aislada y desechable, con SQLite y
usuarios ficticios conocidos. No se usó ni modificó la base productiva y no se
crearon registros de negocio.

### `operator`

- Login correcto y distintivo **Acceso operador**.
- Dashboard con **22 destinos disponibles**.
- Ausencia de enlaces a gerencia, exportaciones, usuarios, precios, personal,
  nómina, fórmulas, consumo de insumos y reportes restringidos.
- URL directa `/dashboard/management` bloqueada con el mensaje esperado y sin
  montar el panel gerencial.
- Producción conserva **Registrar producción**; no muestra aplicar a inventario,
  consumo de materiales ni anulación.
- Inventario ofrece únicamente entrada/salida; no muestra ajuste, costo,
  creación de ubicación ni anulación.
- Ventas de contado conserva **Registrar venta** sin anulación.
- Cobros conserva **Registrar abono** sin anulación.

### `admin_auditor`

- Login correcto y distintivo **Acceso administrador**.
- Dashboard con **33 destinos disponibles** y todos los enlaces esperados.
- Acceso correcto a panel gerencial, centro de exportaciones, usuarios y
  precios, sin pantalla de restricción.
- Acciones administrativas visibles en las cuatro pantallas revisadas.
- Se accionó una descarga gerencial Excel y una PDF; ambas solicitudes
  terminaron con `200 OK`.

## Validación responsive

Se recorrió el dashboard con ambos roles en:

| Viewport | Operador | Administrador/auditor |
| --- | --- | --- |
| `1366x768` | Sin desbordamiento horizontal; 22 destinos; sin Reportes restringido. | Sin desbordamiento horizontal; 33 destinos; Reportes visible. |
| `1440x900` | Sin desbordamiento horizontal; 22 destinos; sin Reportes restringido. | Sin desbordamiento horizontal; 33 destinos; Reportes visible. |
| `390x844` | Bottom nav visible, sin acceso restringido ni desbordamiento horizontal. | Bottom nav visible con Reportes, sin desbordamiento horizontal. |
| `412x915` | Bottom nav visible, sin acceso restringido ni desbordamiento horizontal. | Bottom nav visible con Reportes, sin desbordamiento horizontal. |

## Pruebas técnicas

- `npm run typecheck`: aprobado.
- `npm run build`: aprobado con Next.js 16.2.9; 38 páginas generadas.
- `docker compose -f docker-compose.prod.yml --env-file .env.production.local config --quiet`: aprobado.
- `docker compose -f docker-compose.prod.yml --env-file .env.production.local ps`: `db`, `api` y `web` saludables; PostgreSQL sin puerto publicado.
- Recorrido manual de `operator` y `admin_auditor`: aprobado.
- Descargas administrativas Excel/PDF: solicitudes `200 OK`.
- `git diff --check`: aprobado.
- `git diff --cached --stat`: vacío.

No se ejecutó `pytest` porque el backend no fue modificado. La evidencia
automatizada vigente de 58B permanece en 972 pruebas backend y 42 pruebas
específicas de permisos.

## Seguridad y alcance del cambio

- `.env.production.local` no aparece en los cambios.
- `backups/` no aparece en los cambios.
- No se documentaron ni imprimieron secretos.
- No hubo despliegue ni reconstrucción productiva.
- Los servicios productivos se mantuvieron saludables.
- No se hizo `git add`, commit ni push.

## Pendientes

- Mantener P1-01 abierto hasta que todas las rutas autenticadas compartan un
  único mecanismo de sesión y existan pruebas frontend automatizadas de
  `401/403`; 58C centralizó la política de las rutas administrativas del
  dashboard, no toda la autenticación histórica de cada página.
- Evitar que módulos futuros agreguen tarjetas o rutas administrativas sin
  declararlas en la política frontend y protegerlas primero en backend.
- Validar con George el texto operativo final durante el piloto.

## Siguiente bloque 58D

58D debe convertir la matriz aprobada en cobertura automatizada por rol:

1. pruebas positivas para cada operación permitida al `operator`;
2. pruebas negativas directas para cada familia restringida;
3. comprobación de que la denegación ocurre antes de escribir;
4. casos parametrizados que detecten rutas nuevas sin clasificación;
5. pruebas frontend/E2E mínimas para navegación, URL directa y acciones
   críticas de ambos roles.
