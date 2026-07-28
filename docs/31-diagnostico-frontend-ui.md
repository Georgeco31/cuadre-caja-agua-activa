# 31 - Diagnóstico del frontend y de la interfaz

## Fecha

27 de julio de 2026.

## Objetivo

Documentar el estado visual y estructural del frontend de Agua Activa ERP antes
de iniciar un rediseño progresivo. Este bloque identifica rutas, componentes,
patrones repetidos, problemas de usabilidad, pantallas prioritarias y zonas de
alto riesgo.

El Bloque 57A no rediseña pantallas ni cambia lógica. Su resultado es una línea
base para ejecutar los siguientes bloques sin alterar cálculos, permisos,
endpoints o flujos del negocio.

## Alcance y método

La revisión cubrió:

- estructura de `apps/web`;
- las 38 rutas definidas mediante `page.tsx`;
- los 67 componentes de `apps/web/components`;
- estilos globales y configuración de Tailwind;
- navegación, formularios, tablas, estados y mensajes;
- separación actual entre UI, autenticación y llamadas API;
- reglas de negocio y permisos ya documentados.

Se realizó una auditoría estática de código y de patrones CSS. También se
intentó revisar la aplicación desplegada en
`http://192.168.100.220:3000`, pero en el momento del diagnóstico la URL rechazó
la conexión y `docker compose ... ps` no mostró contenedores activos. No se
inició ni modificó producción. Por tanto, los hallazgos actuales se basan en el
código y se complementan con la validación responsive a 390 x 844 px registrada
previamente en
[`18-auditoria-tecnica-completa.md`](18-auditoria-tecnica-completa.md).

Esta limitación no invalida el inventario estructural, pero exige capturar una
línea base visual de escritorio y móvil al comenzar el Bloque 57B.

## Estado actual del frontend

### Tecnología y estructura

- Next.js 16.2.9 con App Router.
- React 19.2.7 y TypeScript.
- Tailwind CSS 3.4.19, sin biblioteca externa de componentes o iconos.
- `app/globals.css` contiene únicamente reset mínimo, fondo y color base.
- `tailwind.config.ts` define una identidad `water` limitada a cuatro tonos:
  `50`, `100`, `500` y `700`.
- No existe `app/dashboard/layout.tsx` ni una carcasa común para las pantallas
  autenticadas.
- Las 36 páginas bajo `/dashboard` son componentes cliente y repiten lectura
  del token, tratamiento de `401`, cierre de sesión y parte del encabezado.
- El acceso a datos está centralizado en `lib/api.ts`; autenticación, moneda y
  rol tienen utilidades separadas en `lib/auth.ts`, `lib/money.ts` y
  `lib/useCurrentRole.ts`.

La base es funcional y razonablemente responsive, pero el crecimiento por
módulos dejó una UI compuesta principalmente por clases Tailwind copiadas y
componentes de dominio. Todavía no existe un sistema visual transversal.

### Navegación actual

El dashboard funciona como un índice plano:

- presenta 33 tarjetas de acceso;
- solo el acceso a cuadre está marcado como primario;
- cuatro accesos son exclusivos de `admin_auditor`;
- los módulos no están agrupados por tarea, frecuencia o área;
- 33 pantallas incluyen un enlace textual para volver al dashboard;
- no hay sidebar, menú móvil, breadcrumb ni indicador persistente del módulo
  actual.

La navegación es correcta en términos de rutas y permisos, pero requiere
recordar dónde está cada opción y volver al panel central entre módulos.

### Patrones visuales ya presentes

La UI ya tiene una base aprovechable:

- fondos claros en `slate`;
- color `water` para marca y acción primaria;
- tarjetas blancas con borde, radio y sombra ligera;
- campos con foco visible mediante borde y `ring`;
- formularios apilados en móvil y grids desde `sm`;
- tablas dentro de contenedores con scroll horizontal;
- texto de estado acompañado por etiquetas, no solo por color;
- diálogos críticos con `role="dialog"`, `aria-modal` y título asociado.

Una búsqueda de clases en los archivos TSX detectó, como ocurrencias y no como
componentes únicos:

| Patrón | Ocurrencias aproximadas |
| --- | ---: |
| Fondo `bg-slate-50` | 146 |
| Tarjeta blanca base | 117 |
| `shadow-sm` | 124 |
| Acción primaria `bg-water-700` | 75 |
| Acción secundaria blanca | 72 |
| Tabla o bloque con `overflow-x-auto` | 45 |
| Grid responsive desde `sm` | 65 |
| Texto `text-sm` | 855 |
| Texto `text-xs` | 183 |
| `transition` | 184 |

Esto confirma consistencia parcial, pero también alta repetición manual.

## Rutas detectadas

### Entrada

| Ruta | Función |
| --- | --- |
| `/` | Redirige a `/login`. |
| `/login` | Inicio de sesión. |
| `/dashboard` | Panel operativo y acceso a módulos. |

### Caja, historial y reportes de caja

| Ruta | Función |
| --- | --- |
| `/dashboard/cash-session` | Abrir, consultar, contar y cerrar el cuadre. |
| `/dashboard/history` | Filtrar y consultar cuadres. |
| `/dashboard/history/[cashSessionId]` | Detalle y correcciones autorizadas. |
| `/dashboard/reports` | Resumen acumulado de caja. |
| `/dashboard/daily-summary` | Resumen operativo diario. |
| `/dashboard/monthly-summary` | Resumen operativo mensual. |

### Clientes, ventas y cartera

| Ruta | Función |
| --- | --- |
| `/dashboard/customers` | Clientes. |
| `/dashboard/sales/cash` | Ventas de contado. |
| `/dashboard/sales/credit` | Ventas a crédito. |
| `/dashboard/receivables` | Cobros y abonos. |
| `/dashboard/receivables/reports` | Cartera por cliente. |
| `/dashboard/receivables/reports/[customerId]` | Estado de cuenta. |

### Catálogo, inventario y producción

| Ruta | Función |
| --- | --- |
| `/dashboard/products` | Productos y precios base. |
| `/dashboard/pricing` | Listas de precios; administración restringida. |
| `/dashboard/inventory` | Ubicaciones, existencias y movimientos. |
| `/dashboard/production` | Producción y aplicación a inventario. |
| `/dashboard/production/recipes` | Fórmulas de producción. |
| `/dashboard/production/material-consumption` | Consumo de insumos. |

### Rutas y vehículos

| Ruta | Función |
| --- | --- |
| `/dashboard/vehicles` | Vehículos. |
| `/dashboard/delivery-routes` | Rutas de entrega. |
| `/dashboard/route-loads` | Carga de camión. |
| `/dashboard/route-returns` | Retorno de ruta. |
| `/dashboard/route-activity` | Actividad comercial de ruta. |
| `/dashboard/route-closures` | Cierre financiero de ruta. |
| `/dashboard/route-cash-receipts` | Ingreso de efectivo de ruta al cuadre. |
| `/dashboard/route-cash-comparison` | Comparación entre rutas y caja. |

### Compras, gastos y personal

| Ruta | Función |
| --- | --- |
| `/dashboard/suppliers` | Proveedores. |
| `/dashboard/purchases` | Compras. |
| `/dashboard/operating-expenses` | Gastos operativos. |
| `/dashboard/employees` | Empleados. |
| `/dashboard/employees/control` | Asistencia, anticipos, préstamos y abonos. |
| `/dashboard/payroll` | Roles de pago. |

### Administración y gerencia

| Ruta | Función |
| --- | --- |
| `/dashboard/management` | Panel gerencial restringido. |
| `/dashboard/exports` | Exportaciones restringidas. |
| `/dashboard/users` | Usuarios y permisos. |

No se detectaron rutas independientes para bancos, mantenimiento de vehículos,
cuentas por pagar o facturación. Esas capacidades no deben insinuarse mediante
la navegación mientras no existan.

## Componentes principales detectados

### Transversales actuales

| Componente | Uso actual | Observación |
| --- | --- | --- |
| `LogoutButton` | Cierre de sesión en las 36 páginas de dashboard | Es el elemento realmente común más usado. |
| `ErrorMessage` | Error visible en las 36 páginas | No usa `role="alert"` ni región viva. |
| `LoadingState` | Carga en 35 páginas | Estado claro, pero solo textual. |
| `DateSelector` | Selección de fecha de caja | Específico del flujo de caja. |
| `SummaryCard` | Totales de caja | Reutilizado en cuadre y detalle de historial. |

### Dashboard

- `DashboardTodayCard`
- `DashboardQuickActions`
- `DashboardRecentSessions`
- `BackupReminderCard`

### Caja e historial

- `CashSessionCard`
- `CashSessionDetailCard`
- `CashSessionHistoryFilters`
- `CashSessionHistoryTable`
- `CashSummaryFilters`
- `CashSummaryReportCards`
- `DenominationCountTable`
- `CountItemsList`
- `ExpenseForm`
- `ExpenseList`
- `CorrectionCountForm`
- `CorrectionExpenseForm`
- `CorrectionLogsList`

### Maestros y operación

Existen familias de `Form`, `Filters` y `List` para clientes, productos,
empleados, vehículos y rutas. Ventas, cobros, inventario, producción, carga,
retorno y cierre de rutas también tienen componentes de dominio.

Esta separación ayuda, pero no es uniforme. Las pantallas más nuevas o
complejas concentran formulario, filtros, tabla, modal y helpers dentro de
`page.tsx`.

### Componentes visuales locales repetidos

Se encontraron múltiples implementaciones locales con nombres o funciones
equivalentes:

- `StatusBadge` o `StatusPill` en compras, nómina, gastos, recetas y listas de
  rutas;
- `EmptyState` en gastos y reportes;
- `Field` en usuarios, proveedores, precios, recibos y formularios de rutas;
- `MetricCard` en reportes diarios y mensuales;
- un `DataTable` local únicamente en control de empleados;
- botones de sección y estructuras de modal definidas dentro de páginas.

Los nombres propuestos para el futuro sistema visual todavía no constituyen
una API compartida. Deben crearse con contratos pequeños para no trasladar
lógica de negocio a componentes genéricos.

## Problemas visuales encontrados

### 1. Jerarquía de navegación insuficiente

Las 33 acciones rápidas tienen casi el mismo peso visual. El usuario debe
recorrer una cuadrícula extensa para encontrar tareas diarias, reportes,
catálogos o administración. La única distinción fuerte es el cuadre.

### 2. Falta de una carcasa visual común

Cada página reconstruye fondo, ancho, encabezado, enlace de retorno y cierre de
sesión. Esto produce diferencias pequeñas en espacios, anchos, títulos y
ubicación de acciones. También impide mostrar de forma persistente el área
actual.

### 3. Densidad elevada

El uso dominante de `text-sm` y `text-xs`, combinado con muchas tarjetas,
campos y columnas, maximiza información pero reduce escaneabilidad. En pantallas
operativas extensas, las acciones principales compiten con filtros, resúmenes y
acciones secundarias.

### 4. Patrones equivalentes con variantes visuales

Tarjetas, botones, campos, estados, mensajes vacíos y barras de acciones se
repiten mediante cadenas de clases. Una corrección visual requiere editar
muchos lugares y puede producir variaciones involuntarias.

### 5. Estados no totalmente normalizados

Hay estados traducidos y estilizados en varios módulos, pero otros componentes
muestran valores técnicos directamente. Por ejemplo, `SummaryCard` presenta
`summary.status` sin normalización. Los significados de abierto, cerrado,
corregido, activo, anulado, pendiente y pagado no usan todavía un mapa visual
único.

### 6. Tablas correctas pero difíciles de leer

Se detectaron 52 etiquetas `<table>` y 45 contenedores con scroll horizontal.
El scroll evita romper la página, pero no resuelve priorización de columnas,
alineación de importes, encabezados persistentes ni acciones en móvil. Ninguna
tabla incluye `<caption>`; varias dependen del título de la sección para
contexto.

### 7. Identidad de marca limitada

La paleta `water` es adecuada para Agua Activa, pero solo tiene cuatro tonos y
se usa junto a numerosas combinaciones directas de `slate`, `emerald`, `amber`
y `red`. El login y las cabeceras muestran el nombre, pero la identidad visual
no va más allá del color y el texto.

### 8. Feedback visual poco estandarizado

Errores, éxito, carga, vacío y advertencia se resuelven de forma distinta según
el módulo. No hay regiones `aria-live`, `role="alert"` ni un patrón único para
mensajes posteriores a una acción.

### 9. Foco y movimiento

Hay estilos `focus:` en campos, pero no se detectó uso de `focus-visible:` ni
enlace para saltar al contenido. Se encontraron 184 transiciones; son ligeras,
pero deberían quedar limitadas a color, borde y opacidad y respetar reducción
de movimiento.

## Problemas de usabilidad encontrados

1. **Demasiadas decisiones al entrar.** El panel mezcla operación diaria,
   gerencia, configuración y tareas ocasionales.
2. **Navegación tipo ida y vuelta.** La ruta habitual es módulo → volver al
   dashboard → siguiente módulo.
3. **Poca orientación contextual.** No hay breadcrumb, grupo activo ni
   descripción persistente del área.
4. **Acciones críticas y comunes pueden competir.** Cerrar, anular, corregir o
   ajustar aparecen dentro de pantallas ya densas y con confirmaciones de
   estilos distintos.
5. **Confirmaciones inconsistentes.** Se usan 12 `window.confirm` y ocho
   diálogos propios. El navegador interrumpe el flujo y no comunica siempre el
   mismo nivel de riesgo.
6. **Formularios largos.** En gastos, compras, nómina, recetas y control de
   empleados, la carga cognitiva aumenta porque muchas secciones y estados
   conviven en una sola página.
7. **Tablas móviles dependientes de scroll.** Es una solución segura para no
   ocultar datos, pero requiere jerarquizar columnas o presentar un modo
   compacto sin eliminar información.
8. **Etiquetas técnicas visibles.** Roles como `admin_auditor` y algunos
   estados internos aparecen sin una capa consistente de lenguaje para el
   usuario.
9. **Estados vacíos poco orientadores.** Varios informan que no hay registros,
   pero no siempre indican la siguiente acción válida.
10. **La prioridad del negocio no coincide con el orden del dashboard.** Las
    opciones administrativas aparecen antes que caja, clientes y ventas en el
    arreglo de acciones.

## Riesgos técnicos

### Riesgo alto: UI y lógica mezcladas

Doce páginas superan 600 líneas. Las de mayor tamaño son:

| Página | Líneas aproximadas |
| --- | ---: |
| Gastos operativos | 2.177 |
| Fórmulas de producción | 1.823 |
| Control de empleados | 1.588 |
| Listas de precios | 1.375 |
| Compras | 1.356 |
| Roles de pago | 1.224 |
| Panel gerencial | 1.084 |
| Consumo de insumos | 837 |
| Dinero de ruta en caja | 801 |
| Cuadre de caja | 680 |

Cambiar JSX en estos archivos puede afectar estado, validación, llamadas API o
permisos aunque el objetivo sea únicamente visual.

### Riesgo alto: guardas repetidas

Las 36 páginas de dashboard repiten `getToken()`, `removeToken()` y tratamiento
de `401`. La autorización de interfaz se completa mediante consultas de usuario
o `useCurrentRole` en pantallas concretas. Centralizar autenticación al mismo
tiempo que se rediseña el layout ampliaría demasiado el alcance.

### Riesgo alto: flujos encadenados

Caja, ventas, cobros, inventario, producción y rutas tienen dependencias
operativas y anulaciones reversibles. Reordenar controles, cambiar condiciones
de render o reutilizar handlers puede producir errores funcionales difíciles de
detectar visualmente.

### Riesgo medio: abstracción prematura

Un `DataTable`, `StatusBadge` o `FormSection` demasiado inteligente podría
absorber filtros, cálculos, permisos o transformación de datos de dominios
distintos. Los componentes visuales futuros deben ser presentacionales.

### Riesgo medio: regresión responsive

El código contiene muchas reglas responsive y scroll interno. Sustituir
contenedores en bloque puede volver a introducir scroll horizontal de la página
o esconder columnas e importes necesarios.

### Riesgo medio: ausencia de pruebas E2E

La auditoría técnica anterior ya registró que no hay evidencia E2E
automatizada. El rediseño necesitará pruebas manuales por rol y una matriz de
rutas, además de `typecheck` y `build`.

## Pantallas prioritarias

### Prioridad P0: orientación y operación diaria

1. `/dashboard`: reduce el costo de encontrar cualquier módulo.
2. `/dashboard/cash-session`: núcleo del trabajo diario, pero debe rediseñarse
   después de estabilizar componentes visuales.
3. `/dashboard/sales/cash` y `/dashboard/sales/credit`: operación frecuente.
4. `/dashboard/receivables`: afecta la cobranza diaria.
5. Rutas: carga, retorno, cierre, recibo y comparación con caja.
6. `/dashboard/customers` y `/dashboard/products`: maestros necesarios para
   ventas y operación.

### Prioridad P1: consulta y control

1. `/dashboard/history` y su detalle.
2. `/dashboard/daily-summary` y `/dashboard/monthly-summary`.
3. `/dashboard/management`.
4. `/dashboard/exports`.
5. Reportes de caja y cuentas por cobrar.

### Prioridad P2: administración y operación especializada

1. Inventario, producción, fórmulas y consumo de insumos.
2. Gastos operativos, compras y proveedores.
3. Empleados, control de empleados y nómina.
4. Usuarios, permisos y listas de precios.
5. Vehículos y catálogos de rutas.

La prioridad visual no autoriza cambiar primero los flujos de mayor riesgo. El
orden de implementación debe empezar por base visual, dashboard y vistas de
lectura.

## Pantallas de alto riesgo

| Pantalla o grupo | Motivo | Tratamiento recomendado |
| --- | --- | --- |
| Login | Token, redirección y consulta de usuario | Cambiar solo presentación; no tocar `LoginForm` al crear el layout. |
| Cuadre de caja | Conteos, gastos, cierre y fórmula explicativa | Migrar por secciones y comparar totales antes/después. |
| Detalle de historial | Correcciones restringidas y logs | Posponer hasta estabilizar tablas y estados. |
| Ventas y cobros | Creación, límites, pagos y anulaciones | Mantener handlers, payloads, orden de datos y permisos intactos. |
| Inventario y producción | Movimientos reversibles y dependencias | No combinar rediseño de formulario con refactor técnico. |
| Carga, retorno, cierre y recibo de ruta | Stock y dinero se relacionan mediante pasos explícitos | Probar el flujo completo por rol en cada cambio. |
| Gastos, compras y nómina | Archivos muy grandes y datos financieros | Dividir por subpantalla o sección; no migrar todo en un PR. |
| Usuarios y precios | Administración restringida | Probar operador y administrador, incluida URL directa. |
| Exportaciones | Contratos de descarga Excel/PDF | No cambiar URL, query, nombre, formato ni manejo de blob. |

## Recomendaciones generales

1. Crear primero una base visual presentacional y aplicarla en una superficie de
   bajo riesgo.
2. Mantener `lib/api.ts`, `lib/auth.ts`, tipos, endpoints y handlers fuera de
   los cambios visuales.
3. Agrupar la navegación por tareas: Operación diaria, Ventas y clientes,
   Inventario y producción, Rutas, Administración y Reportes.
4. Reservar una zona visible para la tarea principal del día y otra para
   alertas o pendientes.
5. Usar títulos, subtítulos, barras de acciones y espacios consistentes.
6. Estandarizar estados con texto y color semántico; nunca depender solo del
   color.
7. Alinear importes a la derecha y usar cifras tabulares.
8. Mantener tablas completas en escritorio y ofrecer una estrategia móvil
   explícita sin ocultar datos críticos.
9. Dividir formularios extensos en secciones semánticas, sin cambiar campos,
   defaults ni validaciones.
10. Unificar carga, error, éxito, vacío y advertencia con accesibilidad básica.
11. Evitar animaciones decorativas, dependencias visuales nuevas y una
    iconografía que requiera aprendizaje.
12. Capturar evidencias visuales antes y después en los mismos tamaños y con
    los mismos datos.

## Qué no se debe tocar todavía

- llamadas y contratos de `lib/api.ts`;
- almacenamiento o eliminación del token;
- redirecciones de autenticación;
- filtros por rol y condiciones `admin_auditor`;
- cálculos, formateo de dinero y textos que explican reglas financieras;
- orden, nombres, valores y defaults de los campos;
- validaciones, payloads y estados de envío;
- handlers de crear, editar, cerrar, corregir, anular o exportar;
- estados que bloquean acciones y dependencias entre módulos;
- URLs de rutas y enlaces;
- generación o descarga de Excel/PDF;
- backend, migraciones, seeds, base de datos y scripts de producción;
- `.env.production.local`;
- una centralización de autenticación mezclada con el rediseño visual.

## Conclusión

El frontend es funcional y tiene una base clara de color, tarjetas, formularios
y responsive. El problema principal no es la ausencia total de estilo, sino la
falta de jerarquía y sistema: 33 accesos planos, una carcasa repetida, patrones
visuales locales y páginas muy grandes que mezclan presentación con lógica.

El rediseño debe avanzar en capas pequeñas. La secuencia segura es crear una
base visual, aplicarla al dashboard, continuar con vistas de lectura y solo
después migrar formularios y tablas operativas. El plan detallado está en
[`32-plan-redisenio-frontend.md`](32-plan-redisenio-frontend.md).

