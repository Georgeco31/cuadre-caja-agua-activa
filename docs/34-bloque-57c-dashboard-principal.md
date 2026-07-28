# Bloque 57C - Dashboard principal avanzado

## Objetivo

Convertir `/dashboard` en un panel operativo diario con mejor jerarquía,
lectura rápida y navegación móvil, sin cambiar datos, cálculos, endpoints,
autenticación ni permisos.

El resultado prioriza seis preguntas:

1. estado del cuadre de hoy;
2. total contado y total final cuando existe resumen;
3. tareas frecuentes;
4. avisos reales disponibles;
5. cuadres recientes;
6. acceso al resto de módulos.

## Archivos modificados

- `apps/web/app/dashboard/page.tsx`
- `apps/web/components/BackupReminderCard.tsx`
- `apps/web/components/DashboardQuickActions.tsx`
- `apps/web/components/DashboardRecentSessions.tsx`
- `apps/web/components/DashboardTodayCard.tsx`
- `apps/web/components/ui/ActionCard.tsx`
- `apps/web/components/ui/DashboardShell.tsx`
- `apps/web/components/ui/StatCard.tsx`
- `docs/32-plan-redisenio-frontend.md`

## Componentes creados

### `DashboardKpiGrid`

Presenta una fila responsive de indicadores ya preparados por la página. No
hace fetch, no accede al token y no calcula reglas de negocio.

### `DashboardAlertPanel`

Presenta avisos ya derivados por la página y contiene el recordatorio de
backup existente. No consulta fuentes de datos ni decide permisos.

### `DashboardModuleGroup`

Presenta cada grupo de módulos mediante `ActionCard` en densidad compacta.
Recibe acciones ya filtradas y no contiene lógica de roles.

## Datos reales usados

Se conservaron las llamadas ya existentes en `loadDashboard`:

- `getCurrentUser`;
- `getCashSessionByDate` para la fecha local actual;
- `getCashSessionSummary` para el cuadre de hoy;
- `listCashSessions`;
- `getCashSessionSummary` para los cinco cuadres recientes.

Los únicos KPIs son campos del `CashSessionSummary` ya recibido:

- `total_counted`;
- `total_pre_count_expenses`;
- `total_post_count_expenses`;
- `final_total`.

El bloque protagonista usa el estado y fecha de `CashSession`, además de
`total_counted` y `final_total` cuando existe resumen. La actividad reciente
continúa mostrando fecha, estado y total final de las sesiones actuales.

Las alertas disponibles son:

- cuadre pendiente cuando `getCashSessionByDate` devuelve `404`;
- recordatorio operativo de backup ya existente;
- error real de carga mediante el manejo de error previo.

## Métricas descartadas

No se añadieron:

- ventas del día;
- efectivo disponible en caja;
- diferencia de caja;
- stock bajo;
- rutas pendientes;
- cobros vencidos;
- último backup realizado.

`/dashboard` no consume endpoints que entreguen esos datos de manera
confiable. El recordatorio de backup no afirma una fecha ni un estado del
último respaldo.

## Destinos antes y después

La comparación automática de los `href` dio el siguiente resultado:

| Medida | Antes | Después |
| --- | ---: | ---: |
| Destinos únicos | 33 | 33 |
| Destinos restringidos | 4 | 4 |
| Grupos visuales | 7 | 6 |

`Inicio / Caja` se integró en `Operación diaria`; no se eliminó ni cambió
ningún destino. Los seis grupos finales son:

1. Operación diaria;
2. Ventas y clientes;
3. Rutas;
4. Inventario y producción;
5. Reportes y control;
6. Administración.

Se destacan como accesos frecuentes caja, ventas de contado y crédito,
clientes, carga de camión, producción, reportes y, solo para administrador,
exportaciones.

## Permisos

El filtro existente se conserva en `DashboardQuickActions`:

- `admin_auditor`: 33 destinos;
- `operator`: 29 destinos;
- cuatro destinos `adminOnly`: listas de precios, usuarios y permisos, panel
  gerencial y exportaciones.

Los componentes presentacionales nuevos no reciben rol ni aplican permisos.
No cambió ningún `href` ni la autorización del backend.

## Responsive

Cambios aplicados:

- contenido con `min-width: 0` en grids y tarjetas;
- KPIs en una columna y dos columnas desde 360 px;
- bloque principal antes de las alertas en móvil;
- botones principales de ancho completo en móvil;
- acciones frecuentes en una o dos columnas según el ancho;
- módulos completos en tarjetas compactas con blancos táctiles;
- actividad reciente en cards móviles y tabla desde `md`;
- importes con ajuste de línea y números tabulares;
- padding inferior calculado con `safe-area-inset-bottom`;
- `DashboardShell` mantiene `overflow-x-clip`.

George completó la revisión visual autenticada con resultado aprobado:

- 1440 x 900;
- 1366 x 768;
- 390 x 844;
- 412 x 915;
- sin scroll horizontal del documento;
- navegación inferior sin cubrir el contenido.

## Validación LAN y Tailscale

Se reconstruyó producción local con
`scripts/prod-local-rebuild.ps1`, sin borrar volúmenes.

`scripts/prod-local-health.ps1` aprobó sin advertencias:

- web LAN: `http://192.168.100.220:3000/login`;
- web Tailscale: `http://100.121.163.126:3000/login`;
- API LAN y Tailscale;
- contenedores `db`, `api` y `web` saludables;
- Alembic `0026_user_roles`;
- PostgreSQL sin publicar `5432`;
- `.env.production.local` ignorado.

La validación productiva autenticada final fue completada por George:

- login real con `admin_auditor`: aprobado;
- `/dashboard` con `admin_auditor`: aprobado;
- 33 destinos visibles para `admin_auditor`: aprobado;
- cuatro enlaces restringidos visibles para `admin_auditor`: aprobado;
- login real con `operator`: aprobado;
- 29 destinos visibles para `operator`: aprobado;
- enlaces restringidos ocultos para `operator`: aprobado.

## Validación de exportaciones

George confirmó sobre `/dashboard/exports`:

- carga productiva: aprobada;
- descarga real: aprobada.

No se modificó la lógica de descargas Excel/PDF durante 57C.

## Validación técnica

Resultados:

- `git diff --check`: aprobado;
- `npm run typecheck`: aprobado;
- `npm run build`: aprobado, 38 rutas generadas;
- build productivo dentro de Docker: aprobado;
- `docker compose ... config --quiet`: aprobado;
- `docker compose ... ps`: tres servicios saludables;
- health productivo LAN/Tailscale: aprobado;
- comparación de destinos: 33 antes y 33 después;
- comparación de restricciones: cuatro antes y cuatro después;
- matriz autenticada `admin_auditor`/`operator`: aprobada;
- matriz responsive en cuatro viewports: aprobada;
- `/dashboard/exports` y descarga real: aprobadas.

## Evidencia de alcance

El diff contiene exclusivamente frontend y documentación:

- no se modificó `apps/api`;
- no se modificaron migraciones;
- no se modificaron seeds;
- no se modificaron Dockerfiles ni Compose;
- no se modificaron scripts;
- no se modificó `.env.production.local`;
- no se instalaron dependencias;
- no se cambiaron endpoints, payloads, cálculos ni descargas;
- no se hizo `git add`, commit ni push.

## Problemas pendientes

No quedan problemas pendientes para el cierre del Bloque 57C según la
validación final realizada por George.

## Siguiente bloque recomendado

Continuar con 57D, panel gerencial y reportes. 57D debe conservar los mismos
indicadores, filtros y descargas, y evitar mezclar todavía formularios
operativos o permisos granulares.

## Cierre

Bloque 57C aprobado y listo para cierre.
