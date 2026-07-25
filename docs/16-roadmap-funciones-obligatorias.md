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

- Anticipos y préstamos.
- Asistencia y novedades.
- Pagos y roles.
- Descuentos y saldos por empleado.
- Períodos cerrados y trazabilidad de correcciones.

### D. Producción avanzada

- Insumos y materia prima.
- Fórmulas o recetas versionadas.
- Consumo de insumos.
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
| 49 | Producción avanzada | Compras, inventario y productos |
| 50 | Reportes avanzados | Datos estables de los bloques anteriores |

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

### Objetivo

Controlar obligaciones con empleados sin convertir la ficha base en una
nómina improvisada.

### Alcance mínimo

- Asistencia, ausencias y novedades.
- Anticipos y préstamos con saldo.
- Ingresos y descuentos.
- Períodos de pago.
- Roles de pago calculados en backend.
- Pago, anulación y cierre de período.
- Historial por empleado.

### Reglas que deben definirse antes

- Frecuencias, redondeos y períodos.
- Fórmulas legales y conceptos aplicables.
- Autorización de anticipos.
- Descuentos máximos y saldos.
- Privacidad y permisos de información laboral.

### Criterio de cierre

Un período piloto debe poder calcularse, revisarse, pagarse y auditarse sin
modificar períodos cerrados directamente.

## Bloque 49 - Producción avanzada

### Objetivo

Conectar compras, insumos, inventario y producción para conocer consumo y
costo real.

### Alcance mínimo

- Catálogo de insumos y unidades.
- Fórmulas versionadas por producto.
- Lotes de insumo cuando aplique.
- Reserva o consumo explícito.
- Costo promedio o método elegido.
- Mano de obra y costos indirectos definidos.
- Costo del lote y costo unitario.
- Variación de merma contra estándar.

### Regla crítica

Una fórmula no debe reescribir el historial. Cada lote debe conservar la
versión, cantidades y costos usados.

### Criterio de cierre

Un lote piloto debe disminuir insumos, aumentar producto terminado mediante
la aplicación vigente y producir un costo reproducible.

## Bloque 50 - Reportes avanzados, gráficos y exportación

### Objetivo

Convertir datos operativos estabilizados en información gerencial.

### Alcance mínimo

- Indicadores con definición y fórmula visibles.
- Comparaciones por período.
- Gráficos responsivos.
- Exportación Excel con datos tabulares.
- Exportación PDF para reportes cerrados.
- Rentabilidad por dimensiones disponibles.
- Control de zona horaria y fechas de corte.
- Pruebas de totales entre pantalla y exportación.

### Regla crítica

Las exportaciones y gráficos deben consumir resultados oficiales del backend;
no deben recalcular cifras financieras de forma distinta en el navegador.

### Criterio de cierre

El mismo filtro debe devolver los mismos totales en API, pantalla, Excel y PDF.

## Dependencias entre bloques

```text
Bloque 45: compras/proveedores
  +--> Bloque 47: gastos con proveedores
  +--> Bloque 49: costo y consumo de insumos

Bloque 46: listas de precios
  +--> mejora ventas y rentabilidad

Bloque 48: empleados avanzado
  +--> aporta mano de obra al Bloque 49

Bloques 45-49 estables
  +--> Bloque 50: reportes confiables
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
