# Bloque 57D - Panel gerencial, reportes y exportaciones

## Objetivo

Mejorar la lectura, jerarquía visual y experiencia responsive de las pantallas
gerenciales y de reportes sin cambiar datos, cálculos, endpoints, queries,
payloads, autenticación, permisos ni archivos descargados.

El bloque conserva el carácter de solo lectura de las cinco rutas:

- `/dashboard/management`;
- `/dashboard/daily-summary`;
- `/dashboard/monthly-summary`;
- `/dashboard/reports`;
- `/dashboard/exports`.

## Pantallas modificadas

### Panel gerencial

Se aplicó la carcasa visual aprobada del dashboard, un encabezado con contexto
de acceso restringido, una barra de período y exportación responsive, KPIs
consistentes, alertas semánticas, gráficos en la paleta de Agua Activa y
paneles de detalle con cifras tabulares.

### Resumen operativo diario

El filtro de fecha quedó separado del contenido, la fecha consultada tiene un
contexto visible, los resúmenes se agrupan por caja, producción, rutas y
actividad comercial, y las tablas usan paneles con scroll interno cuando el
ancho no permite mostrar todas sus columnas. Los importes y cantidades de las
tablas se alinean a la derecha.

### Reporte mensual operativo

La selección del mes y las acciones de exportación quedaron en una toolbar
responsive. Los mismos KPIs se organizan por área y el detalle diario conserva
las tarjetas móviles existentes y la tabla completa desde `md`.

### Resumen acumulado de caja

Los filtros se agrupan por período y estado. El resultado se separa en:

1. cuadres registrados;
2. monedas, billetes y total contado;
3. gastos y total final.

También se muestra `total_expenses`, campo real que ya entregaba el endpoint,
para hacer explícita la separación entre los dos tipos de gasto y el acumulado.
No se creó ni recalculó este valor en el frontend.

### Centro de exportaciones

Se hicieron únicamente ajustes menores de consistencia: navegación activa del
grupo de reportes, protección de ancho mínimo y espaciado. La selección de
reporte, filtros, generación de query, manejo de `blob`, URLs y nombres de
archivo permanecen sin cambios.

## Archivos modificados

- `apps/web/app/dashboard/management/page.tsx`
- `apps/web/app/dashboard/daily-summary/page.tsx`
- `apps/web/app/dashboard/monthly-summary/page.tsx`
- `apps/web/app/dashboard/reports/page.tsx`
- `apps/web/app/dashboard/exports/page.tsx`
- `apps/web/components/DailySummaryAlerts.tsx`
- `apps/web/components/DailySummaryCards.tsx`
- `apps/web/components/DailySummaryDetails.tsx`
- `apps/web/components/MonthlySummaryAlerts.tsx`
- `apps/web/components/MonthlySummaryCards.tsx`
- `apps/web/components/MonthlySummaryDetails.tsx`
- `apps/web/components/CashSummaryFilters.tsx`
- `apps/web/components/CashSummaryReportCards.tsx`
- `apps/web/components/ui/MetricGrid.tsx`
- `apps/web/components/ui/ReportSection.tsx`
- `docs/32-plan-redisenio-frontend.md`
- `docs/35-bloque-57d-reportes-gerenciales.md`

## Componentes creados y reutilizados

### Creados

#### `MetricGrid`

Cuadrícula presentacional para KPIs con variantes de tres, cuatro y cinco
columnas. Solo recibe contenido preparado y no hace fetch, no accede al token,
no decide permisos y no calcula valores.

#### `ReportSection`

Encabezado semántico reutilizable para una sección de reporte. Recibe título,
contexto, descripción y contenido. No contiene lógica de negocio.

### Reutilizados

- `DashboardShell`;
- `PageHeader`;
- `ResponsiveToolbar`;
- `StatCard`;
- `StatusBadge`;
- `ErrorMessage`;
- `LoadingState`;
- `LogoutButton`.

## Endpoints preservados

No se modificó `apps/web/lib/api.ts`. Las consultas continúan usando:

| Pantalla | Endpoint |
| --- | --- |
| Panel gerencial | `GET /auth/me` |
| Panel gerencial | `GET /reports/management-dashboard` con `date_from` y `date_to` opcionales |
| Resumen diario | `GET /reports/daily-operational-summary` con `date` |
| Resumen mensual | `GET /reports/monthly-operational-summary` con `year` y `month` |
| Resumen de caja | `GET /reports/cash-summary` con `date_from`, `date_to` y `status` opcionales |
| Exportaciones | `GET /auth/me` |

Las descargas directas de las pantallas conservan:

- `/reports/exports/management-dashboard.xlsx`;
- `/reports/exports/management-dashboard.pdf`;
- `/reports/exports/monthly-summary.xlsx`;
- `/reports/exports/monthly-summary.pdf`.

El centro de exportaciones conserva su catálogo existente:

- Excel: panel gerencial, resumen mensual, ventas, cartera, gastos operativos,
  compras, inventario, producción, rutas y nómina;
- PDF: panel gerencial, resumen mensual, resumen diario operativo, cartera y
  nómina.

No cambió ningún `endpoint`, `filename`, parámetro, extensión ni construcción de
la query.

## Métricas reales usadas

### Panel gerencial

Se conservan los campos reales del `ManagementDashboard`:

- caja: sesiones, contado, gastos posteriores al conteo y total final;
- ventas: contado, crédito, total, promedio y conteos;
- cartera: cobros, saldo pendiente, vencido y clientes con saldo;
- gastos y compras: totales pagados, pendientes, anulados, categorías y
  proveedores;
- producción e inventario: lotes, cantidades, merma, aplicaciones, costo de
  insumos, stock y stock bajo;
- rutas: cargas, retornos, cierres, esperado, entregado, diferencia y registro
  en caja;
- nómina: roles, bruto, deducciones, neto y anulados;
- series diarias y rankings entregados en `charts`;
- alertas entregadas en `alerts`.

### Resumen diario

Se conservan todos los campos de caja, producción, cargas, retornos, cierres,
dinero de ruta en caja, ventas, cobros, productos y alertas del
`DailyOperationalSummary`, incluido
`total_business_cash_inflow_reference`.

### Resumen mensual

Se conservan caja, producción, ventas, cartera, operación de rutas, cierres,
registros de ruta en caja, productos, filas diarias, alertas y
`total_business_cash_inflow_reference` del `MonthlyOperationalSummary`.

### Resumen acumulado de caja

Se muestran únicamente campos del `CashSummaryReport`:

- total de cuadres, abiertos y cerrados;
- monedas, billetes y total contado;
- gastos antes y después del conteo;
- gastos acumulados;
- total final.

## Métricas descartadas

No se añadieron indicadores sin fuente real, entre ellos:

- utilidad o margen;
- crecimiento porcentual;
- flujo de caja disponible;
- proyecciones de ventas o cobros;
- cumplimiento de metas;
- rentabilidad por producto, ruta o cliente;
- fecha o estado del último backup;
- comparaciones contra un período anterior no entregadas por los endpoints.

## Confirmación de cálculos y datos

- No se modificaron funciones de carga ni handlers.
- No se modificó `apps/web/lib/api.ts`.
- No se añadió ninguna fórmula financiera.
- No se cambiaron filtros enviados, fechas, años, meses ni estados.
- No se modificaron tipos, payloads ni respuestas.
- No se cambiaron alertas, severidades, rangos ni umbrales.
- El umbral informativo de stock bajo continúa siendo `≤ 5`.
- Los formateadores de dinero y cantidades conservan `es-EC` y USD.

## Permisos

La lógica existente permanece en las páginas:

- `/dashboard/management` valida `GET /auth/me` y solo carga el reporte para
  `admin_auditor`;
- `/dashboard/exports` valida `GET /auth/me` y solo habilita el catálogo para
  `admin_auditor`;
- un `401` continúa eliminando el token y redirigiendo a `/login`;
- el dashboard continúa ocultando panel gerencial y exportaciones al rol
  `operator`;
- los componentes nuevos no reciben rol ni deciden autorización.

## Validación técnica

Resultados de la implementación:

- `npm run typecheck`: aprobado;
- `npm run build`: aprobado, 38 rutas generadas;
- build productivo dentro de Docker: aprobado, 38 rutas generadas;
- `docker compose ... config --quiet`: aprobado;
- `docker compose ... ps`: `db`, `api` y `web` saludables;
- `scripts/prod-local-health.ps1`: aprobado sin fallos ni advertencias;
- web y API LAN/Tailscale: aprobadas;
- Alembic: `0026_user_roles`;
- PostgreSQL: `5432` no publicado;
- no se instalaron dependencias;
- no se modificaron backend, migraciones, seeds, Docker ni scripts.

## Validación por rol

George completó la validación autenticada real con `admin_auditor`:

- login productivo: aprobado;
- `/dashboard/management`: aprobado;
- `/dashboard/daily-summary`: aprobado;
- `/dashboard/monthly-summary`: aprobado;
- `/dashboard/reports`: aprobado;
- `/dashboard/exports`: aprobado.

La reserva anterior por falta de una sesión autenticada quedó resuelta. No se
restablecieron contraseñas, no se modificaron credenciales, no se crearon tokens
y no se alteraron usuarios, datos ni permisos.

## Validación Excel/PDF

George confirmó sobre producción:

- descarga Excel real: aprobada;
- descarga PDF real: aprobada.

Se conservaron URLs, parámetros, manejo de `blob`, extensiones y nombres de
archivo.

## Validación responsive

Decisiones aplicadas:

- `DashboardShell` mantiene `overflow-x-clip`;
- todos los contenedores principales y grids usan `min-width: 0`;
- filtros y botones se apilan en móvil y conservan blancos táctiles de 44 px;
- KPIs cambian de una a dos columnas desde 360 px;
- importes usan ajuste de línea y números tabulares;
- tablas anchas usan scroll interno, no scroll horizontal del documento;
- el detalle mensual conserva tarjetas móviles;
- el padding inferior de `DashboardShell` evita que la navegación inferior tape
  contenido o acciones.

George aprobó la validación responsive autenticada en escritorio y móvil, sin
errores funcionales detectados. La navegación inferior, los filtros, las
acciones de exportación y la lectura de importes se mantuvieron utilizables.

La validación LAN y Tailscale también fue aprobada.

## Seguridad y alcance

- `.env.production.local` permanece ignorado y sin modificaciones;
- `backups/` permanece ignorado y sin modificaciones;
- no se muestran secretos en la interfaz ni en este documento;
- no se modificó `apps/api`;
- no se modificaron migraciones ni seeds;
- no se modificaron Dockerfiles, Compose ni scripts;
- no se tocaron pantallas operativas;
- no se hizo `git add`, commit ni push.

## Problemas pendientes

No quedan problemas pendientes para el cierre del Bloque 57D según la
validación autenticada final realizada por George.

## Siguiente bloque recomendado

Continuar con 57E.1, maestros simples, en entregas pequeñas. Deben conservarse
campos, defaults, validaciones, payloads y permisos, y evitar todavía los flujos
operativos financieros de mayor riesgo.

## Cierre

La reserva por validación autenticada quedó resuelta. El Bloque 57D queda
aprobado y listo para cierre.
