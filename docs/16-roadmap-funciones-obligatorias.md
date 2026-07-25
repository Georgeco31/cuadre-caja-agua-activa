# 16 - Roadmap de funciones obligatorias

## Propósito

Este roadmap ordena las funciones que faltan para pasar de una base operativa
a un ERP más completo. Cada bloque debe tener reglas, migraciones, pruebas,
documentación y piloto propios. No debe iniciarse más de un bloque crítico sin
cerrar la validación del anterior.

## Funciones obligatorias futuras

### A. Listas de precios

- Listas por cliente, tipo de cliente y ruta.
- Precios especiales con vigencia.
- Prioridad clara entre precio base, lista y precio especial.
- Historial o snapshot del precio aplicado a cada venta.
- Validación backend para evitar precios ambiguos.

### B. Gastos operativos generales

- Gastos fuera del cuadre diario.
- Categorías y centros de costo.
- Proveedores y beneficiarios.
- Estados pendiente, pagado y anulado.
- Pagos recurrentes y vencimientos.
- Relación opcional con caja, banco, ruta o vehículo sin duplicar dinero.

### C. Empleados avanzado

- Anticipos y préstamos. **Implementado base en el Bloque 48.**
- Asistencia y novedades básicas. **Implementado base en el Bloque 48.**
- Abonos y saldos de préstamos por empleado. **Implementado base en el
  Bloque 48.**
- Roles calculados por período. **Implementado base en el Bloque 49.**
- Descuentos de anticipos, préstamos y otros conceptos por empleado.
  **Implementado base en el Bloque 49.**
- Pago real de nómina y conciliación con caja o bancos. **Pendiente futuro.**
- Períodos cerrados y trazabilidad de correcciones.

### D. Producción avanzada

- Insumos y materia prima. **Implementado base en el Bloque 50.**
- Fórmulas o recetas con snapshots. **Implementado base en el Bloque 50.**
- Costos estimados por fórmula y unidad. **Implementado base en el Bloque 50.**
- Consumo controlado y explícito de insumos. **Implementado base en el Bloque
  51.**
- Consumo automático al crear producción. **No planificado por seguridad
  operativa; el flujo base exige confirmación explícita.**
- Costos directos e indirectos.
- Costo por lote y por unidad.
- Mermas con causa y análisis.

### E. Reportes avanzados

- Gráficos e indicadores.
- Exportación Excel y PDF.
- Rentabilidad por producto, cliente, ruta y vehículo.
- Tendencias de ventas, cobros, cartera, producción, merma e inventario.
- Filtros consistentes y exportaciones reproducibles desde backend.

## Orden recomendado

| Bloque | Tema | Dependencia principal |
| --- | --- | --- |
| 45 | Compras y proveedores | Productos e inventario |
| 46 | Listas de precios por cliente/ruta | Clientes, rutas, productos y ventas |
| 47 | Gastos operativos generales | Proveedores y reglas de caja/bancos |
| 48 | Empleados avanzado | Fichas de empleados |
| 49 | Roles de pago base | Empleados avanzado |
| 50 | Producción avanzada | Compras, inventario y productos |
| 51 | Consumo controlado de insumos | Producción, fórmulas e inventario |
| 52 | Reportes avanzados | Datos estables de los bloques anteriores |

## Bloque 45 - Compras y proveedores

### Objetivo

Registrar el abastecimiento real y su impacto controlado en inventario y
cuentas por pagar.

### Alcance mínimo

- Proveedores activos e inactivos.
- Órdenes o comprobantes de compra.
- Detalle de productos o insumos.
- Recepción parcial o total.
- Entrada de inventario explícita y trazable.
- Estado pendiente, recibido, anulado y pagado según diseño.
- Costos y snapshots.
- Cuentas por pagar básicas.

### Reglas que deben definirse antes

- Momento exacto en que una compra aumenta inventario.
- Tratamiento de devoluciones.
- Diferencia entre proveedor, beneficiario de gasto y cliente.
- Impuestos y documentos que se registrarán.
- Relación con caja o bancos sin doble contabilización.

### Criterio de cierre

Una compra piloto debe poder registrarse, recibirse, reflejar stock, anularse
de forma trazable y conciliarse con el documento externo.

## Bloque 46 - Listas de precios por cliente/ruta

### Objetivo

Evitar que el operador tenga que recordar o digitar precios habituales.

### Alcance mínimo

- Lista base y listas adicionales.
- Asignación a cliente, tipo de cliente o ruta.
- Vigencia desde/hasta.
- Precio especial por cliente y producto.
- Orden de precedencia documentado.
- Snapshot del precio y origen aplicado en cada venta.
- Permiso o motivo para sobreescritura manual.

### Regla de precedencia propuesta para diseñar

```text
precio especial vigente del cliente
  > lista asignada al cliente
  > lista de la ruta
  > precio base del producto
```

La precedencia es una propuesta de análisis, no una regla implementada. Debe
validarse con Agua Activa antes de crear tablas.

### Criterio de cierre

La misma venta debe obtener un precio determinístico en backend y conservar
qué regla lo produjo.

## Bloque 47 - Gastos operativos generales

**Estado: implementado base en el Bloque 47.**

### Objetivo

Registrar costos que no pertenecen exclusivamente al conteo de una caja.

### Alcance mínimo

- Categorías y subcategorías.
- Proveedor o beneficiario opcional.
- Fecha de documento, vencimiento y pago.
- Gastos recurrentes.
- Relación con ruta, vehículo, producción o área.
- Adjuntos o referencias documentales según seguridad.
- Estados y anulación con motivo.
- Reporte por período y categoría.

### Regla crítica

Definir cuándo un pago del gasto también se registra en caja o banco. El
registro contable y el movimiento de dinero no deben duplicarse.

### Criterio de cierre

El reporte del período debe distinguir gastos devengados, pagados y anulados,
sin alterar el cuadre físico de manera implícita.

### Alcance base completado

- Categorías activables, proveedor opcional, documento, vencimiento y fecha de
  pago informativa.
- Gastos con estados `unpaid`, `paid` y `partial`, edición mientras están
  activos y anulación lógica con motivo.
- Plantillas semanales, mensuales, trimestrales y anuales con generación
  exclusivamente manual.
- Resumen oficial por período, categoría, proveedor y estado de pago, con
  anulados separados.
- Aislamiento explícito respecto de caja, bancos, gastos del cuadre, compras,
  pagos a proveedores, inventario, ventas, cobros, producción y rutas.

Quedan para una fase de madurez las subcategorías, centros de costo, relación
con áreas/rutas/vehículos, adjuntos, pagos parciales reales, cuentas por pagar
y conciliación explícita con caja o bancos.

## Bloque 48 - Empleados avanzado

**Estado: implementado base.**

### Objetivo

Controlar obligaciones con empleados sin convertir la ficha base en una
nómina improvisada.

### Base implementada

- Asistencia diaria editable con estados de presencia, ausencia, atraso,
  permiso, vacaciones y enfermedad.
- Anticipos administrativos con anulación lógica y motivo.
- Préstamos con principal, total abonado y saldo pendiente.
- Abonos parciales o totales, con reversión del saldo al anular.
- Resumen e historial reciente por empleado.
- Validaciones de empleado activo, importes positivos, asistencia única por
  fecha y bloqueo de estados incompatibles.
- Aislamiento de caja, bancos y gastos operativos.

### Completado en el Bloque 49

- Frecuencias, redondeos y períodos.
- Roles de pago calculados en backend.
- Descuentos de anticipos y préstamos dentro del rol.
- Anulación lógica y liberación de deducciones.

### Pendiente futuro

- Pago real de nómina y cierre formal de período.
- Fórmulas legales y conceptos aplicables.
- IESS, décimos, vacaciones, horas extras y comisiones.
- Privacidad y permisos de información laboral.

### Criterio de cierre futuro

Un período piloto debe poder calcularse, revisarse, pagarse y auditarse sin
modificar períodos cerrados directamente.

## Bloque 49 - Roles de pago base

**Estado: implementado base.**

### Objetivo

Calcular y congelar roles por período sin convertir el cálculo en un pago ni
crear movimientos financieros implícitos.

### Base implementada

- Período, fecha de rol, número único, estado activo o anulado y notas.
- Uno o varios empleados activos por rol, sin duplicados.
- Snapshots de identidad, cargo, frecuencia y sueldo base.
- Resumen congelado de asistencia, ausencias, atrasos, permisos, vacaciones,
  enfermedad y horas del período.
- Bonos, otros ingresos y otros descuentos manuales.
- Deducción completa de anticipos activos seleccionados.
- Deducción parcial de préstamos activos sin superar el saldo visible.
- Totales de ingresos, descuentos y neto calculados con `Decimal` en backend.
- Preview sin persistencia, listado, filtros, detalle, resumen por empleado y
  anulación con motivo.
- Bloqueo de anticipos y préstamos ya usados en otro rol activo; la anulación
  libera las referencias.
- Aislamiento explícito de caja, bancos, gastos, saldos de préstamos, estados
  de anticipos y pagos reales de nómina.

### Regla base documentada

El sueldo base no se prorratea en este MVP. La asistencia se conserva como
referencia del período. Para simplificar el control, un préstamo no puede
aparecer en más de un rol activo, aunque el descuento sea parcial.

### Pendiente futuro

- Pago real, comprobantes, aprobación y cierre formal de períodos.
- IESS, décimos, vacaciones avanzadas, horas extras, comisiones y retenciones.
- Exportaciones, firma y privacidad por roles de usuario.

## Bloque 50 - Producción avanzada

**Estado: implementado base.**

### Objetivo

Crear la base de insumos, materia prima, formulas y costos estimados sin
automatizar consumo ni movimientos de inventario.

### Base implementada

- Clasificacion de productos como terminado, materia prima, insumo, empaque,
  servicio u otro.
- Formulas por producto terminado con cantidad de salida, vigencia, estados y
  anulacion logica.
- Items activables con cantidad requerida, costo unitario, costo total,
  porcentaje de merma, notas y snapshots del producto.
- Costos estimados total y por unidad calculados con `Decimal` en backend.
- Estimacion escalada para otra cantidad de salida.
- Filtros por texto, estado, producto, clasificacion y vigencia.
- Aislamiento de inventario, movimientos, produccion existente, caja, compras,
  ventas y costos del producto terminado.

### Pendiente futuro

- Versionado formal de formulas por producto y snapshot de la formula aplicada
  a un lote real.
- Lotes de insumo cuando aplique.
- Reserva de insumos y consumo parcial avanzado.
- Costo promedio o método elegido.
- Mano de obra y costos indirectos definidos.
- Costo del lote y costo unitario.
- Variación de merma contra estándar.

### Regla crítica futura

Una fórmula no debe reescribir el historial. Cada lote debe conservar la
versión, cantidades y costos usados.

### Criterio de cierre

Un lote piloto debe disminuir insumos, aumentar producto terminado mediante
la aplicación vigente y producir un costo reproducible.

## Bloque 51 - Consumo controlado de insumos

**Estado: implementado base.**

### Objetivo

Consumir materia prima e insumos desde inventario usando una formula
seleccionada para cada producto de una produccion, sin crear movimientos
automaticos al registrar el lote.

### Base implementada

- Vista previa sin persistencia ni cambios de stock.
- Formula activa y compatible obligatoria por cada item producido.
- Cantidad calculada con `quantity_produced`, salida base de la formula y
  porcentaje de merma del insumo.
- Validacion de stock agregado por insumo y ubicacion activa.
- Salidas de inventario transaccionales, costos y snapshots trazables.
- Un solo consumo activo por produccion, con historial de anulados.
- Anulacion con motivo que conserva registros, anula movimientos y revierte
  stock.
- Bloqueo de anulacion de la produccion mientras exista consumo activo.
- Aislamiento de caja, compras, ventas, formulas, productos y costo del
  producto terminado.

### Pendiente futuro

- Consumo parcial avanzado.
- Lotes y vencimientos de materia prima.
- Reserva de insumos.
- Costeo contable real, mano de obra y costos indirectos.
- Actualizacion controlada del costo real del producto terminado.

## Bloque 52 - Reportes avanzados, gráficos y exportación

### Objetivo

Convertir datos operativos estabilizados en información gerencial.

### Bloque 52A - Indicadores gerenciales y gráficos base (implementado)

- Endpoint gerencial autenticado y de solo lectura por rango.
- Indicadores base de caja, ventas, cartera, gastos, compras, producción,
  inventario, rutas y nómina.
- Alertas informativas de cuadres abiertos, cartera vencida, stock bajo,
  pendientes y diferencias negativas de ruta.
- Gráficos responsivos simples sin dependencias externas.
- Rango por defecto en el mes calendario actual.
- Sin migraciones, seeds ni modificaciones de datos.

### Bloque 52B - Exportación Excel (implementado base)

- Diez endpoints autenticados para panel gerencial, resumen mensual, ventas,
  cartera, gastos operativos, compras, inventario, producción, rutas y nómina.
- Archivos `.xlsx` generados en memoria con hojas tabulares, encabezados,
  filtros, anchos básicos y formatos numéricos.
- Reutilización de servicios y totales oficiales existentes, incluyendo el
  panel gerencial y el resumen mensual.
- Pantalla central `/dashboard/exports`, acceso desde el dashboard y botones
  directos en panel gerencial y resumen mensual.
- Pruebas de autenticación, apertura con `openpyxl`, rangos vacíos, períodos
  inválidos y ausencia de escrituras.
- Sin migraciones, tablas, seeds ni datos automáticos.

### Bloque 52C - Exportación PDF (implementado base)

- Cinco endpoints PDF autenticados y de solo lectura para panel gerencial,
  resumen mensual, resumen diario operativo, cartera y nómina base.
- Documentos ejecutivos A4 horizontal generados en memoria con ReportLab,
  tablas ajustadas y numeración de páginas.
- Reutilización de los servicios oficiales del panel gerencial y los resúmenes
  mensual y diario.
- Pantalla central `/dashboard/exports` con secciones separadas para Excel
  detallado y PDF ejecutivo, además de botones PDF en panel gerencial y resumen
  mensual.
- Pruebas de autenticación, períodos inválidos, archivos PDF válidos y ausencia
  de escrituras.
- Sin migraciones, tablas, seeds ni datos automáticos.

Pendiente para madurez gerencial futura:

- Rentabilidad por dimensiones disponibles.
- Comparativos avanzados y fechas de corte.
- Definiciones y fórmulas visibles para indicadores de mayor madurez.

### Regla crítica

Las exportaciones y gráficos deben consumir resultados oficiales del backend;
no deben recalcular cifras financieras de forma distinta en el navegador.

### Criterio de cierre

El mismo filtro debe devolver los mismos totales en API, pantalla, Excel y PDF.

## Dependencias entre bloques

```text
Bloque 45: compras/proveedores
  +--> Bloque 47: gastos con proveedores
  +--> Bloque 50: costo y consumo de insumos

Bloque 46: listas de precios
  +--> mejora ventas y rentabilidad

Bloque 48: empleados avanzado
  +--> Bloque 49: roles de pago base
  +--> aporta mano de obra al Bloque 50

Bloques 45-51 estables
  +--> Bloque 52: reportes confiables
```

## Reglas de ejecución del roadmap

- Validar procesos reales antes de diseñar tablas.
- No inventar datos ni reglas del negocio.
- Crear migraciones solo dentro del bloque que las requiera.
- Mantener snapshots en documentos históricos.
- Calcular dinero y totales oficiales en backend.
- Usar anulaciones y cierres, no borrado físico.
- Añadir pruebas PostgreSQL para reglas dependientes de concurrencia.
- Preparar plan de backup y rollback antes de cada migración.
- Pilotear cada módulo con alcance limitado.
- Actualizar la matriz de módulos al cerrar cada bloque.

## Fuera de estos bloques, pero necesario antes de despliegue público

- Roles y permisos.
- Sesión con cookies seguras y protección CSRF cuando corresponda.
- HTTPS, dominio y estrategia de despliegue.
- Backups automáticos cifrados y copia externa.
- Monitoreo, alertas y logs.
- Pruebas E2E y de integración PostgreSQL.
- Procedimiento de recuperación ante desastre.
