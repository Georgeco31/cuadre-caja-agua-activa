# 32 - Plan de rediseño progresivo del frontend

## Propósito

Convertir Agua Activa ERP en una interfaz más clara, moderna y profesional sin
alterar su lógica. El rediseño se ejecutará en bloques pequeños, verificables y
reversibles, con prioridad en claridad operativa, lectura rápida y exactitud.

Este documento define la dirección futura. El Bloque 57A no implementa los
cambios descritos.

## Visión visual propuesta

Agua Activa debe sentirse como un sistema interno confiable:

- limpio, sin decoración innecesaria;
- denso cuando el trabajo lo requiera, pero ordenado por jerarquía;
- orientado a tareas diarias y estados pendientes;
- sobrio en escritorio y usable con una mano en móvil;
- consistente entre caja, ventas, rutas, inventario y administración;
- reconocible por una identidad de agua, limpieza, control y confianza.

La pantalla debe responder rápidamente a cinco preguntas:

1. ¿En qué módulo estoy?
2. ¿Qué debo hacer ahora?
3. ¿Cuál es el estado del registro?
4. ¿Qué dato requiere atención?
5. ¿Qué acción es segura y cuál es crítica?

## Principios de diseño

### 1. Exactitud antes que estética

No ocultar importes, estados, fechas, identificadores ni explicaciones
financieras para ganar espacio.

### 2. Una acción principal por contexto

Cada página o sección debe destacar una acción primaria. Acciones secundarias,
administrativas y destructivas deben tener menor peso.

### 3. Jerarquía consistente

Todas las páginas usarán la misma secuencia:

1. contexto o breadcrumb;
2. título y descripción;
3. estado o resumen;
4. barra de acciones;
5. contenido principal;
6. ayuda o notas de negocio.

### 4. Progresión segura

Primero navegación y lectura; después formularios y acciones. No combinar
refactor de autenticación, API o negocio con cambios visuales.

### 5. Responsive explícito

No asumir que apilar todo resuelve móvil. Cada tabla, toolbar y formulario debe
tener una decisión documentada para anchos pequeños.

### 6. Consistencia semántica

Abierto, cerrado, corregido, activo, inactivo, anulado, pendiente, pagado,
vencido y con diferencia deben conservar significado y tratamiento visual en
todo el ERP.

### 7. Accesibilidad práctica

Foco visible, etiquetas claras, mensajes anunciables, contraste suficiente,
orden de teclado lógico y blancos táctiles cómodos.

### 8. Movimiento mínimo

Usar transición solo para foco, hover, expansión o feedback. Evitar animaciones
de entrada, contadores animados y efectos que retrasen la operación.

## Paleta conceptual

No se implementa en este bloque.

| Rol | Dirección conceptual | Uso |
| --- | --- | --- |
| Primario | Azul agua profundo | Acción principal, enlace activo, foco y marca. |
| Primario suave | Azul agua muy claro | Selección, contexto, tarjetas destacadas. |
| Superficie | Blanco | Tarjetas, formularios y tablas. |
| Fondo | Gris azulado muy claro | Fondo general y separación de áreas. |
| Texto principal | Azul pizarra casi negro | Títulos, cifras y contenido crítico. |
| Texto secundario | Gris pizarra medio | Descripciones y metadatos. |
| Éxito | Verde sobrio | Pagado, activo o conciliado. |
| Advertencia | Ámbar | Pendiente, vencimiento o atención. |
| Peligro | Rojo sobrio | Anulado, error o acción destructiva. |
| Información | Azul intermedio | Ayuda y mensajes informativos. |

Reglas:

- `water` seguirá siendo el color de marca; no se sustituirá por una paleta
  multicolor.
- Los colores semánticos se reservarán para estados, no para decorar módulos.
- Cada estado tendrá texto explícito, borde o forma además de color.
- Se validará contraste de texto, controles, foco y estados deshabilitados.
- La paleta actual de Tailwind se ampliará únicamente cuando exista un uso
  documentado.

## Tipografía conceptual

No se instalarán fuentes en 57A ni se requiere una fuente web para iniciar el
rediseño.

Dirección recomendada:

- familia sans del sistema, priorizando `Segoe UI` en Windows;
- títulos con peso 600, sin tamaños excesivos;
- cuerpo de 14 a 16 px según densidad;
- ayudas y metadatos no menores a 12 px;
- importes con números tabulares;
- mayúsculas solo para etiquetas breves, nunca para párrafos;
- interlineado mayor en explicaciones de negocio y menor en tablas.

Una fuente externa solo debe evaluarse después del piloto visual y si mejora
legibilidad sin introducir dependencia de red.

## Estructura de navegación propuesta

### Escritorio

Una carcasa común con:

- marca Agua Activa;
- navegación agrupada por área;
- módulo activo;
- acceso al dashboard;
- usuario y rol en lenguaje legible;
- cierre de sesión visible, pero no dominante;
- contenido con ancho adaptable: cómodo para formularios y mayor para tablas.

Grupos conceptuales:

1. **Inicio:** dashboard.
2. **Operación diaria:** cuadre, ventas, cobros, rutas.
3. **Clientes y catálogo:** clientes, productos, precios.
4. **Inventario y producción:** existencias, producción, fórmulas, insumos.
5. **Administración:** compras, gastos, empleados, nómina, usuarios.
6. **Control y reportes:** historial, resúmenes, gerencia y exportaciones.

La visibilidad de enlaces seguirá dependiendo de los permisos actuales. El
componente visual no decidirá autorización por sí solo.

### Móvil

- encabezado compacto con título y acceso al menú;
- navegación en panel controlado por teclado;
- acción principal visible sin cubrir contenido;
- toolbars apiladas;
- tablas con scroll interno o vista resumida explícita;
- acciones destructivas separadas de las acciones frecuentes.

## Sistema de componentes propuesto

Los componentes vivirían probablemente en `apps/web/components/ui/`. La
ubicación y API definitivas se decidirán en 57B.

### `PageHeader`

Responsabilidad:

- eyebrow o breadcrumb;
- título `h1`;
- descripción;
- enlace de retorno opcional;
- zona de acciones.

No debe consultar usuario, token ni API.

### `StatCard`

Responsabilidad:

- etiqueta;
- valor ya calculado;
- nota;
- tono semántico opcional.

No calcula dinero, porcentajes ni estados. El llamador entrega el texto final.

### `ActionCard`

Responsabilidad:

- título, descripción, destino y jerarquía;
- estado deshabilitado o etiqueta opcional.

No filtra roles internamente. La pantalla conserva la regla actual de
visibilidad.

### `DataTable`

Responsabilidad:

- estructura semántica;
- contenedor responsive;
- encabezados, alineación y estado vacío;
- zona opcional para acciones por fila.

No hace fetch, no ordena, no pagina, no exporta y no transforma datos por
defecto. Si una tabla necesita una conducta especial, se compone desde su
componente de dominio.

### `EmptyState`

Responsabilidad:

- explicar qué falta;
- mostrar la siguiente acción válida cuando exista;
- diferenciar falta de datos de error o falta de permisos.

### `StatusBadge`

Responsabilidad:

- presentar etiqueta ya normalizada y tono semántico;
- mantener forma, tamaño y contraste consistentes.

El dominio decide la traducción y el significado. No se asumirá que `active`
significa lo mismo en todas las entidades.

### `FormSection`

Responsabilidad:

- título, descripción y grupo de campos;
- preferir `fieldset` y `legend` cuando corresponda;
- zona de ayuda o resumen.

No posee estado, validación ni envío.

### `ResponsiveToolbar`

Responsabilidad:

- ordenar filtros, búsqueda, acciones y resultados;
- apilar controles en móvil;
- mantener la acción principal identificable.

No aplica filtros ni administra sus valores.

## Componentes complementarios a evaluar

Solo si los ocho componentes base resultan insuficientes:

- `AppShell` o `DashboardShell`;
- `Button` con variantes limitadas;
- `FieldMessage`;
- `LoadingState`, `ErrorState` y `SuccessMessage` unificados;
- `ConfirmDialog` accesible;
- `SectionCard`.

No se creará una biblioteca completa antes de tener dos pantallas reales que
demuestren el patrón.

## Criterios de aceptación visual generales

Estos criterios aplican a todos los bloques posteriores:

### Jerarquía y consistencia

- una sola etiqueta `h1` visible por página;
- título, descripción y acciones en posiciones consistentes;
- una acción primaria evidente por contexto;
- acciones destructivas siempre etiquetadas y separadas;
- mismo estado visual para el mismo significado;
- espacios, radios, bordes y sombras basados en un conjunto reducido.

### Escritorio

- validar como mínimo 1366 x 768 y 1440 x 900;
- no tener scroll horizontal en el documento;
- mantener visibles importes, estados y acciones principales;
- usar el ancho disponible en tablas sin estirar formularios en exceso.

### Móvil

- validar como mínimo 390 x 844 y 412 x 915;
- no tener scroll horizontal en el documento;
- permitir scroll interno documentado en tablas cuando sea necesario;
- controles principales con blanco táctil cómodo;
- formularios en una columna salvo pares breves y seguros;
- no fijar barras que oculten filas, mensajes o botones.

### Tablas y datos

- importes alineados y sin perder moneda o signo;
- fechas e identificadores legibles;
- encabezados asociados a columnas;
- contexto accesible mediante título o caption;
- estados y acciones no dependen solo de color;
- estado vacío, carga y error se distinguen;
- ninguna columna crítica se oculta sin alternativa.

### Formularios

- cada control conserva label, nombre, tipo, valor, default y validación;
- ayuda y error aparecen junto al campo o sección correspondiente;
- envío deshabilitado mientras la petición está activa;
- foco visible y orden de teclado lógico;
- cancelar nunca ejecuta la acción;
- una modificación visual no cambia el payload.

### Funcionalidad

- mismos endpoints, queries, métodos y payloads;
- mismos permisos para `operator` y `admin_auditor`;
- mismas redirecciones de login, `401` y `403`;
- mismos cálculos y valores mostrados;
- mismas descargas Excel/PDF;
- no cambia la base de datos ni el backend.

### Validación técnica por bloque

- `git diff --check`;
- `npm run typecheck`;
- `npm run build` cuando se modifique frontend;
- prueba manual de rutas afectadas;
- prueba en escritorio y móvil;
- prueba por ambos roles cuando haya contenido condicionado;
- staging vacío salvo autorización explícita distinta.

## Roadmap

### 57B - Base visual y layout general

#### Objetivo

Definir tokens y una carcasa visual común sin centralizar autenticación ni
cambiar navegación funcional.

#### Alcance

- documentar escala de espacios, radios, sombras, tipografía y colores;
- crear los componentes presentacionales mínimos;
- crear la estructura de navegación agrupada;
- aplicar la base primero a `/dashboard` y, si es necesario, a una vista de
  lectura de bajo riesgo;
- conservar las guardas de cada página durante este bloque.

#### Archivos probables

- `apps/web/app/globals.css`
- `apps/web/tailwind.config.ts`
- `apps/web/app/dashboard/layout.tsx`, solo si la carcasa no contiene lógica
- `apps/web/components/ui/PageHeader.tsx`
- `apps/web/components/ui/ActionCard.tsx`
- `apps/web/components/ui/StatusBadge.tsx`
- `apps/web/components/ui/ResponsiveToolbar.tsx`
- un posible `apps/web/components/ui/DashboardShell.tsx`

#### Riesgos

- aplicar el layout a 36 rutas de una vez;
- duplicar encabezados durante la transición;
- mover protección de sesión o roles al crear la carcasa;
- ocultar enlaces permitidos o mostrar enlaces administrativos.

#### Criterios de aceptación

- navegación agrupada y comprensible;
- el rol ve exactamente los mismos destinos que antes;
- ninguna ruta cambia;
- autenticación y cierre de sesión conservan comportamiento;
- no se migran formularios operativos;
- layout sin scroll horizontal en escritorio o móvil;
- componentes nuevos son presentacionales.

#### Cómo probar

1. Capturar línea base del login y dashboard.
2. Entrar como `operator` y como `admin_auditor`.
3. Comparar destinos visibles antes y después.
4. Abrir cada grupo y volver al dashboard.
5. Probar 1366 x 768, 1440 x 900, 390 x 844 y 412 x 915.
6. Ejecutar typecheck y build.

### 57C - Dashboard principal

**Estado:** implementado en el frontend y documentado en
`docs/34-bloque-57c-dashboard-principal.md`. La validación técnica y el health
LAN/Tailscale están aprobados; queda pendiente la matriz visual autenticada por
rol con una credencial productiva vigente.

#### Objetivo

Convertir el índice plano en un panel de trabajo diario con jerarquía.

#### Alcance

- destacar estado del cuadre y tareas frecuentes;
- agrupar las 33 acciones por área;
- separar operación diaria, reportes y administración;
- mejorar sesiones recientes y recordatorio de backup;
- conservar URLs y filtro por rol.

#### Archivos probables

- `apps/web/app/dashboard/page.tsx`
- `apps/web/components/DashboardQuickActions.tsx`
- `apps/web/components/DashboardTodayCard.tsx`
- `apps/web/components/DashboardRecentSessions.tsx`
- `apps/web/components/BackupReminderCard.tsx`
- componentes `ActionCard` y `StatCard`

#### Riesgos

- perder un enlace al reordenar;
- convertir prioridad visual en permiso;
- ocultar una alerta o el estado del cuadre;
- cambiar cargas del dashboard al intentar optimizar la UI.

#### Criterios de aceptación

- los 33 destinos siguen disponibles según el rol;
- cuadre y operación diaria aparecen primero;
- administración no domina la pantalla de operador;
- no cambia `loadDashboard` ni sus llamadas;
- sesiones recientes conservan fecha, estado y totales;
- navegación móvil no exige recorrer una cuadrícula indiferenciada.

#### Cómo probar

1. Comparar lista de `href` antes y después.
2. Probar dashboard con cuadre inexistente, abierto y cerrado.
3. Probar con error de API y carga.
4. Probar ambos roles.
5. Abrir al menos un enlace de cada grupo.
6. Ejecutar typecheck y build.

### 57D - Panel gerencial y reportes

#### Objetivo

Mejorar lectura de indicadores, alertas, gráficos, resúmenes y exportaciones sin
cambiar datos ni archivos descargados.

#### Alcance

- panel gerencial;
- resumen diario y mensual;
- resumen acumulado de caja;
- cuentas por cobrar y estado de cuenta;
- catálogo de exportaciones;
- `StatCard`, estados, toolbars y jerarquía de tablas.

#### Archivos probables

- `apps/web/app/dashboard/management/page.tsx`
- `apps/web/app/dashboard/daily-summary/page.tsx`
- `apps/web/app/dashboard/monthly-summary/page.tsx`
- `apps/web/app/dashboard/reports/page.tsx`
- `apps/web/app/dashboard/exports/page.tsx`
- `apps/web/app/dashboard/receivables/reports/**`
- `DailySummary*`, `MonthlySummary*`, `CashSummary*`,
  `ReceivablesSummaryCards` y `CustomerStatementView`

#### Riesgos

- cambiar formato o interpretación de indicadores;
- ocultar alertas sin datos;
- alterar queries de fecha;
- romper descargas, nombres o contenido de Excel/PDF;
- hacer gráficos decorativos sin contexto accesible.

#### Criterios de aceptación

- todos los valores coinciden con la línea base;
- alertas conservan severidad y texto;
- rangos y filtros generan las mismas consultas;
- exportaciones descargan los mismos formatos;
- panel y exportaciones siguen restringidos;
- gráficos tienen alternativa textual o etiqueta suficiente.

#### Cómo probar

1. Fijar un rango de datos y registrar valores antes del cambio.
2. Comparar tarjetas, alertas, tablas y totales después.
3. Descargar una muestra Excel y PDF sin modificar su lógica.
4. Probar acceso directo con ambos roles.
5. Probar períodos sin datos y con datos.
6. Ejecutar typecheck y build.

### 57E - Formularios operativos

#### Objetivo

Ordenar formularios y acciones sin modificar campos, validación, payloads ni
reglas.

#### Alcance

Debe dividirse en entregas pequeñas:

- **57E.1:** maestros simples: clientes, productos, empleados, vehículos, rutas
  y proveedores;
- **57E.2:** ventas de contado, ventas a crédito y cobros;
- **57E.3:** inventario, producción, fórmulas, consumo, cargas y retornos;
- **57E.4:** cuadre, gastos operativos, compras, control de empleados y nómina.

Cada entrega debe abordar uno o dos flujos completos, no una familia entera en
un solo cambio.

#### Archivos probables

- componentes `*Form.tsx` y sus páginas;
- `apps/web/app/dashboard/cash-session/page.tsx`;
- `apps/web/app/dashboard/inventory/page.tsx`;
- `apps/web/app/dashboard/operating-expenses/page.tsx`;
- `apps/web/app/dashboard/purchases/page.tsx`;
- `apps/web/app/dashboard/payroll/page.tsx`;
- `apps/web/app/dashboard/employees/control/page.tsx`;
- `apps/web/app/dashboard/production/**`;
- `FormSection` y `ResponsiveToolbar`.

#### Riesgos

- es el bloque de mayor riesgo;
- cambiar orden o condición de campos;
- perder defaults, decimales o estados deshabilitados;
- reutilizar un campo que transforma el valor de otra forma;
- mover handlers o lógica a componentes genéricos;
- ejecutar acciones críticas durante la prueba.

#### Criterios de aceptación

- mismos campos, tipos, nombres, opciones y defaults;
- mismo payload observado en pruebas controladas;
- mismos mensajes de backend;
- acciones críticas conservan permiso y confirmación;
- ningún cálculo se traslada al frontend;
- formularios extensos quedan divididos visualmente, no funcionalmente;
- no se mezclan creación, anulación y refactor técnico.

#### Cómo probar

1. Documentar casos válidos, inválidos y límites del flujo elegido.
2. Comparar payload y respuesta antes y después en un entorno de prueba.
3. Probar doble clic, envío activo, cancelar y error.
4. Probar permisos de anulación con ambos roles.
5. Verificar importes y cantidades decimales.
6. Ejecutar las pruebas funcionales existentes, typecheck y build.

### 57F - Tablas e historial

#### Objetivo

Unificar lectura, filtros, estados vacíos y acciones de filas sin ocultar datos.

#### Alcance

- historial de cuadres y detalle;
- listas de clientes, productos, empleados, vehículos y rutas;
- listas de ventas, cobros, inventario, producción y compras;
- `DataTable`, `StatusBadge`, `EmptyState` y toolbars;
- alineación de fechas, identificadores, cantidades e importes.

#### Archivos probables

- `apps/web/app/dashboard/history/**`
- componentes `*List.tsx`, `*Table.tsx` y `*Filters.tsx`
- tablas locales dentro de páginas grandes
- `apps/web/components/ui/DataTable.tsx`
- `apps/web/components/ui/EmptyState.tsx`
- `apps/web/components/ui/StatusBadge.tsx`

#### Riesgos

- una abstracción genérica demasiado compleja;
- alterar filtros, orden o selección;
- esconder columnas críticas en móvil;
- cambiar qué acciones aparecen por estado o rol;
- degradar rendimiento con renderizados innecesarios.

#### Criterios de aceptación

- datos, orden y filtros coinciden con la línea base;
- importes están alineados y completos;
- tablas tienen contexto semántico;
- acciones conservan condiciones actuales;
- móvil no tiene scroll del documento;
- si existe scroll interno, es visible y usable;
- estados vacíos indican el siguiente paso cuando corresponde.

#### Cómo probar

1. Comparar conteo de filas y valores con un conjunto fijo.
2. Probar todos los filtros y su limpieza.
3. Probar tabla vacía, carga y error.
4. Probar filas largas y múltiples acciones.
5. Probar teclado y móvil.
6. Ejecutar typecheck y build.

### 57G - Mejoras móviles

#### Objetivo

Completar la experiencia móvil después de estabilizar componentes y flujos.

#### Alcance

- navegación móvil;
- barras de filtros y acciones;
- formularios largos;
- tablas, tarjetas y modales;
- blancos táctiles, foco y teclado;
- revisión de landscape cuando sea útil.

#### Archivos probables

- carcasa y navegación;
- `ResponsiveToolbar`;
- `DataTable`;
- formularios y listas con problemas detectados en la matriz responsive;
- estilos globales mínimos.

#### Riesgos

- aplicar CSS global que altere escritorio;
- ocultar datos para “simplificar”;
- usar barras fijas que cubran contenido;
- cambiar el orden funcional de campos;
- depender de hover.

#### Criterios de aceptación

- rutas prioritarias aprobadas a 390 x 844 y 412 x 915;
- sin scroll horizontal del documento;
- controles utilizables con toque y teclado;
- tablas conservan acceso a toda la información;
- modales caben, desplazan su contenido y mantienen acciones accesibles;
- escritorio no regresa.

#### Cómo probar

1. Crear una matriz por ruta y ancho.
2. Probar al menos login, dashboard, caja, venta, cobro, ruta, historial,
   gerencia y exportaciones.
3. Probar teclado virtual en formularios.
4. Probar textos y valores largos.
5. Repetir smoke de escritorio.
6. Ejecutar typecheck y build.

### 57H - Revisión final de consistencia

#### Objetivo

Cerrar diferencias visuales, accesibilidad básica y regresiones antes de dar por
terminado el rediseño.

#### Alcance

- inventario de las 38 rutas;
- comparación de componentes y estados;
- eliminación de duplicación visual solo cuando sea segura;
- matriz de escritorio, móvil y roles;
- actualización de documentación.

#### Archivos probables

- componentes `ui`;
- páginas con excepciones documentadas;
- documentación de frontend;
- pruebas visuales o E2E si se incorporan en un bloque autorizado.

#### Riesgos

- convertir el cierre en un rediseño adicional;
- eliminar excepciones necesarias del dominio;
- hacer limpieza de lógica fuera de alcance;
- aceptar una ruta no probada porque comparte componentes.

#### Criterios de aceptación

- todas las rutas están clasificadas como aprobadas o con excepción explícita;
- no quedan variantes accidentales de botones, estados, cards o encabezados;
- ambos roles mantienen permisos;
- cálculos y exportaciones coinciden;
- no hay errores visibles, scroll de documento o foco perdido;
- documentación refleja el resultado real.

#### Cómo probar

1. Ejecutar la matriz completa por rutas, roles y viewports.
2. Comparar datos críticos contra una línea base.
3. Ejecutar pruebas existentes, typecheck y build.
4. Ejecutar `git diff --check`.
5. Revisar el diff para confirmar que no hay backend, migraciones, seeds,
   scripts ni entornos modificados.

## Recomendación para el primer bloque de implementación

Comenzar por **57B: base visual y layout general**, con un alcance todavía más
pequeño:

1. capturar la línea base visual del login, dashboard y una vista de lectura;
2. definir tokens conceptuales en código;
3. crear `PageHeader`, `ActionCard`, `StatusBadge` y `ResponsiveToolbar` como
   componentes presentacionales;
4. construir una carcasa de navegación sin mover autenticación;
5. aplicarla únicamente al dashboard y a una vista de lectura piloto;
6. validar ambos roles y cuatro viewports;
7. detenerse antes de migrar caja, ventas o formularios.

El éxito de 57B no se medirá por cuántos archivos cambien, sino por demostrar
que el sistema visual puede introducirse sin alterar rutas, permisos, datos o
lógica. Solo después de esa prueba debe comenzar 57C.

## Cambios futuros, no incluidos en 57A

- crear componentes `ui`;
- editar `globals.css` o Tailwind;
- añadir layout o navegación;
- agrupar acciones del dashboard;
- migrar tarjetas, tablas o formularios;
- normalizar estilos de estados;
- cambiar responsive;
- añadir pruebas visuales o E2E;
- evaluar iconos o una fuente externa.

En 57A solo quedan definidos el diagnóstico, la dirección visual, los riesgos,
el roadmap y los criterios de aceptación.
