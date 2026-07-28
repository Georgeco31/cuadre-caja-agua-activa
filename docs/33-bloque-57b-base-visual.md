# 33 - Bloque 57B: base visual y layout general

## Fecha

28 de julio de 2026.

## Objetivo

Crear la primera base visual moderna de Agua Activa ERP en un alcance seguro:
el dashboard y la vista piloto de exportaciones. El bloque introduce una
carcasa responsive y componentes presentacionales sin cambiar backend,
endpoints, payloads, cálculos, autenticación, permisos ni generación de
archivos.

## Estado de cierre

**Aprobado.** George completó la validación productiva real el 28 de julio de
2026. El Bloque 57B queda listo para cierre y habilita el inicio del Bloque 57C.

## Referencia visual aplicada

La referencia aprobada se adaptó al sistema real, sin copiarla literalmente:

- sidebar azul agua en escritorio;
- topbar con acceso a módulos, fecha, avisos y cuenta activa;
- encabezados con jerarquía clara y espacio blanco;
- tarjetas KPI y de navegación con bordes suaves;
- recordatorio operativo en ámbar;
- verde, ámbar y rojo reservados para estados;
- navegación móvil inferior con cinco accesos: Inicio, Caja, Rutas, Reportes y
  Más;
- iniciales `AA` como placeholder mientras se importa el logo definitivo;
- tipografía del sistema, sin fuentes externas;
- iconos mediante texto y símbolos simples, sin dependencias.

La paleta existente `water` se amplió únicamente con tonos intermedios y
oscuros necesarios para el sidebar, estados de foco y sombras.

## Línea base revisada

Antes de modificar se verificó:

- `git status --short`: limpio;
- producción local: los contenedores estaban detenidos;
- se inició la composición productiva sin reconstruir y se capturó `/login` a
  1366 x 768;
- se revisó estáticamente el dashboard, exportaciones, componentes existentes,
  las 33 rutas de navegación y los cuatro filtros `adminOnly`;
- durante la primera captura no se dispuso de una credencial productiva válida,
  por lo que no se forzó ni se cambió la autenticación. Esta limitación inicial
  quedó resuelta posteriormente con la validación real ejecutada por George.

Las capturas no se guardaron dentro del repositorio.

## Archivos modificados

- `apps/web/app/globals.css`
- `apps/web/tailwind.config.ts`
- `apps/web/app/dashboard/page.tsx`
- `apps/web/app/dashboard/exports/page.tsx`
- `apps/web/components/BackupReminderCard.tsx`
- `apps/web/components/DashboardQuickActions.tsx`
- `apps/web/components/DashboardRecentSessions.tsx`
- `apps/web/components/DashboardTodayCard.tsx`
- `apps/web/components/ui/ActionCard.tsx`
- `apps/web/components/ui/DashboardShell.tsx`
- `apps/web/components/ui/PageHeader.tsx`
- `apps/web/components/ui/ResponsiveToolbar.tsx`
- `apps/web/components/ui/StatCard.tsx`
- `apps/web/components/ui/StatusBadge.tsx`
- `docs/33-bloque-57b-base-visual.md`

No se modificaron dependencias, `package.json`, `package-lock.json`, fuentes,
iconos externos ni archivos de configuración productiva.

## Componentes creados

### `PageHeader`

Recibe eyebrow, título, descripción, metadatos y acciones opcionales. No hace
fetch, no lee autenticación y no decide permisos.

### `StatCard`

Presenta label, value, hint, tone e icono opcionales. El valor llega preparado;
el componente no calcula importes.

### `ActionCard`

Presenta title, description, href, variant, badge, disabled e icono. No consulta
roles ni transforma datos de negocio.

### `StatusBadge`

Presenta un label ya traducido y uno de cinco tonos semánticos. No interpreta
estados.

### `ResponsiveToolbar`

Distribuye contenido y acciones en escritorio o móvil. No implementa filtros.

### `DashboardShell`

Carcasa visual con sidebar de escritorio, topbar y navegación inferior móvil.
Recibe usuario, rol, fecha y enlaces como propiedades. No lee token, no elimina
token, no llama APIs y no filtra permisos.

## Pantallas cambiadas

### `/dashboard`

- saludo y contexto del usuario;
- estado del cuadre destacado;
- cuatro KPI oficiales recibidos del backend;
- acciones frecuentes;
- navegación completa agrupada;
- recordatorio de backup;
- sesiones recientes;
- tarjetas móviles en lugar de una tabla horizontal;
- sidebar de escritorio y navegación inferior móvil.

La carga de usuario, cuadre, resumen y sesiones permanece en la página
original. No se movió a la carcasa visual.

### `/dashboard/exports`

- `PageHeader` y `DashboardShell`;
- barra de contexto de solo lectura y restablecimiento de período;
- tarjetas separadas para Excel y PDF;
- controles táctiles y layout responsive;
- mismo selector de reportes, filtros, validaciones y botones.

Las constantes de reportes, endpoints, parámetros, nombres de archivo,
`downloadFile`, manejo de blob y tratamiento de errores permanecen sin cambios.
La única información adicional conservada en estado es el nombre de la cuenta
para presentarlo en la carcasa.

## Pantallas no tocadas

No se aplicó el layout nuevo de forma global y no se editaron:

- `/login`;
- `/dashboard/cash-session`;
- ventas de contado o crédito;
- cobros y cartera operativa;
- rutas operativas;
- producción;
- inventario;
- compras;
- nómina;
- usuarios;
- precios;
- gastos operativos;
- las demás vistas de lectura o formularios.

Tampoco se modificaron backend, migraciones, seeds, Docker, scripts PowerShell,
variables de entorno ni base de datos.

## Decisiones de diseño

1. La carcasa se aplica explícitamente a dos páginas para evitar encabezados
   duplicados en las demás rutas.
2. La navegación persistente contiene solo destinos comunes a ambos roles. Los
   destinos restringidos siguen siendo entregados y filtrados por
   `DashboardQuickActions`, como antes.
3. Los 33 destinos aparecen en siete secciones y no se esconden en móvil.
4. Las cuatro acciones frecuentes se duplican como atajos, pero el inventario
   canónico de módulos conserva 33 enlaces únicos.
5. La actividad reciente usa tarjetas en móvil y tabla desde `md`, conservando
   fecha, estado, total y detalle.
6. La búsqueda de la topbar se adaptó como enlace funcional “Buscar un módulo”
   hacia el inventario del dashboard; no se añadió un buscador falso ni lógica
   nueva.
7. El acceso “Avisos” lleva al recordatorio operativo, sin inventar
   notificaciones.
8. No se ocultó overflow global para disfrazar desbordamientos. La QA midió el
   ancho real del documento.

## Conservación de lógica

- El dashboard sigue leyendo token y usuario en la página.
- Los `401` siguen eliminando token y redirigiendo a `/login`.
- La autorización de exportaciones sigue exigiendo `admin_auditor`.
- Los cuatro destinos restringidos conservan `adminOnly: true`.
- Ningún componente nuevo importa `lib/api` o `lib/auth`.
- No se cambiaron consultas, payloads ni orden de llamadas.
- No se añadieron cálculos financieros.
- Los formatos monetarios existentes solo cambiaron de contenedor visual.
- No se cambiaron rutas ni URLs.

## Comparación de destinos antes y después

| Grupo nuevo | Destinos únicos | Restringidos |
| --- | ---: | --- |
| Inicio / Caja | 2 | 0 |
| Operación diaria | 5 | 0 |
| Ventas y clientes | 6 | 1: listas de precios |
| Rutas | 8 | 0 |
| Inventario y producción | 5 | 0 |
| Administración | 3 | 1: usuarios y permisos |
| Reportes y control | 4 | 2: panel gerencial y exportaciones |
| **Total después** | **33** | **4** |

Comparación automática:

- antes: 33 destinos, cuatro restringidos;
- después: 33 destinos únicos, cuatro restringidos;
- `admin_auditor`: 33 visibles;
- `operator`: 29 visibles.

## Prueba por rol `admin_auditor`

Como QA preliminar se ejecutó una prueba visual con API efímera y datos
ficticios, retirada al terminar:

- 33 destinos únicos visibles;
- siete grupos visibles;
- usuarios, listas de precios, exportaciones y panel gerencial visibles;
- `/dashboard/exports` mostró dos formularios, diez opciones Excel y cinco
  opciones PDF;
- el flujo de descarga de prueba terminó sin error visual, aunque el navegador
  automatizado no expuso el evento de descarga generado mediante blob.

La reserva de esta prueba preliminar quedó resuelta mediante la validación
productiva real de cierre.

## Prueba por rol `operator`

Con la misma API efímera:

- 29 destinos únicos visibles;
- siete grupos visibles;
- usuarios, listas de precios, exportaciones y panel gerencial ausentes;
- acceso directo a `/dashboard/exports` mostró el mensaje de prohibición y
  cero formularios;
- la navegación común siguió disponible.

Se abrieron rutas representativas de los siete grupos:

- `/dashboard/cash-session`;
- `/dashboard/daily-summary`;
- `/dashboard/customers`;
- `/dashboard/delivery-routes`;
- `/dashboard/inventory`;
- `/dashboard/employees`;
- `/dashboard/reports`.

La API y ruta efímeras usadas para QA se eliminaron antes de las validaciones
finales y nunca formaron parte del diff entregado.

## Validación productiva real de cierre

George completó la prueba final sobre la producción local real:

- login real: aprobado;
- `/dashboard` con `admin_auditor`: aprobado;
- `/dashboard/exports` con `admin_auditor`: aprobado;
- descarga Excel con datos reales: aprobada;
- descarga PDF con datos reales: aprobada;
- acceso por LAN: aprobado;
- acceso por Tailscale: aprobado.

No se expusieron ni documentaron contraseñas. No fue necesario modificar
`.env.production.local`, autenticación, permisos, backend, endpoints ni lógica
de descargas.

Con esta prueba quedan confirmados en producción los flujos que durante la QA
automatizada se habían validado inicialmente con datos ficticios.

## Prueba de escritorio

- 1366 x 768: línea base de `/login` productivo revisada.
- 1366 x 768: dashboard nuevo revisado.
- 1440 x 900: dashboard y exportaciones revisados.
- Sidebar, topbar, tarjetas KPI, recordatorio, formularios y acciones
  conservaron lectura y jerarquía.
- No hubo scroll horizontal del documento.

## Prueba móvil

- 390 x 844: dashboard revisado con 33 enlaces de administrador y navegación
  inferior de cinco accesos.
- 412 x 915: exportaciones y dashboard de operador revisados.
- Los controles mantienen al menos 44 px de alto donde son interactivos.
- Los módulos permanecen accesibles en secciones apiladas.
- La actividad reciente cambia a tarjetas.
- No hubo scroll horizontal del documento.

Mediciones principales:

| Vista | Viewport | `innerWidth` | `scrollWidth` | Resultado |
| --- | ---: | ---: | ---: | --- |
| Dashboard admin | 390 x 844 | 390 | 375 | Sin overflow |
| Exportaciones admin | 412 x 915 | 412 | 397 | Sin overflow |
| Dashboard operator | 412 x 915 | 412 | 397 | Sin overflow |

La diferencia de 15 px corresponde a la barra vertical del navegador.

## Validaciones técnicas

- `npm run typecheck`: aprobado.
- `npm run build`: aprobado; 38 rutas generadas.
- build dentro de `prod-local-rebuild.ps1`: aprobado.
- inventario automático: 33 destinos únicos.
- conteo automático: cuatro `adminOnly`.
- `git diff --check`: aprobado antes de documentación y se repite al cierre.
- `docker compose ... config --quiet`: aprobado.
- `docker compose ... ps`: `db`, `api` y `web` activos y saludables.
- salud productiva final: aprobada sin fallos ni advertencias; API y web
  respondieron por localhost, LAN y Tailscale; Alembic quedó en
  `0026_user_roles` y PostgreSQL continuó sin publicar 5432.
- login productivo real con `admin_auditor`: aprobado por George.
- dashboard y exportaciones productivas reales: aprobados por George.
- descargas reales Excel y PDF: aprobadas por George.
- validación final LAN y Tailscale: aprobada por George.
- staging: debe permanecer vacío; no se ejecutó `git add`.

## Problemas y pendientes

No quedan problemas funcionales abiertos para el cierre del Bloque 57B.

Pendientes de bloques futuros:

1. El logo definitivo continúa pendiente; se usa `AA`.
2. Búsqueda avanzada, centro de notificaciones y navegación contextual por
   pantalla quedan fuera de 57B.

## Siguiente bloque recomendado: 57C

Continuar con los componentes de formularios y datos de menor riesgo definidos
en `docs/32-plan-redisenio-frontend.md`, manteniendo el despliegue progresivo.
La base visual 57B ya cuenta con aprobación productiva real y queda cerrada
como punto de partida para esa migración progresiva.
