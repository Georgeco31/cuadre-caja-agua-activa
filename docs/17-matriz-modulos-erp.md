# 17 - Matriz de módulos de Agua Activa ERP

## Criterios de estado

| Estado | Significado |
| --- | --- |
| Implementado base | El flujo principal existe, pero faltan automatizaciones o funciones de madurez |
| Implementado avanzado | El flujo incluye controles, reportes y trazabilidad suficiente para piloto |
| Parcial | Solo una parte del módulo existe o el nombre agrupa capacidades ausentes |
| Pendiente | Está planificado y tiene dependencias identificadas |
| No implementado | No existe modelo, endpoint ni pantalla funcional del módulo |

La valoración corresponde al corte del Bloque 53. “Implementado” no significa
que el módulo pueda operar sin conciliación, backup o control manual.

## Matriz

| Módulo | Estado | Qué existe | Qué falta | Prioridad | Riesgo |
| --- | --- | --- | --- | --- | --- |
| 1. Caja y bancos | Parcial | Cuadre diario, denominaciones, conteos, gastos de caja, cierre, historial, correcciones, resumen y comparación con rutas | Bancos, conciliación, saldo inicial, múltiples cajas/turnos, ingreso automático y gastos generales | Alta | Alto: caja no se concilia automáticamente con ventas, cobros o bancos |
| 2. Clientes | Implementado base | Alta, consulta, filtros, edición, activación/inactivación, crédito habilitado y límite | Historial de cambios, contactos avanzados, documentos, anticipos y segmentación comercial completa | Media | Medio: cambios de maestro no tienen auditoría general |
| 3. Productos y precios | Implementado base | Catálogo, SKU, presentación, precio base, costo estimado, retornabilidad, estado, clasificación productiva y listas por cliente/ruta | Promociones, historial general de cambios y costos reales | Alta | Medio: el costo del catálogo sigue siendo estimado y no se actualiza desde producción |
| 4. Ventas | Implementado base | Contado, crédito, múltiples ítems, snapshots, totales backend, filtros, detalle, vínculo opcional a carga y anulación | Facturación, edición controlada, devoluciones, descuentos formales y descarga automática de inventario | Alta | Alto: venta registrada no disminuye stock |
| 5. Créditos, cobros y abonos | Implementado avanzado | Límite, saldo, abonos parciales/totales, anulación reversible, cartera, vencidos y estado de cuenta | Recibos formales, cobros masivos, anticipos, refinanciación y conciliación bancaria | Alta | Alto: requiere comparación externa de comprobantes y efectivo |
| 6. Inventario | Implementado base | Ubicaciones, stock, entradas, salidas, ajustes, costos opcionales, anulación, producción, carga y retorno vinculados | Kardex/valoración avanzada, conteos físicos, transferencias generales y descarga por ventas | Alta | Alto: omitir un movimiento explícito deja módulos desalineados |
| 7. Rutas de entrega | Implementado avanzado | Rutas, cargas, inventario vehicular, retorno, actividad comercial, cierre financiero, dinero recibido y comparación con caja | Planificación, asignación formal de personal, liquidación física completa, mapas y geolocalización | Alta | Alto: cierre y recibo no cambian caja ni inventario automáticamente |
| 8. Compras y proveedores | Implementado base | Proveedores, items, snapshots, totales backend, filtros, detalle y anulación de compras | Recepción en inventario, cuentas por pagar, pagos, devoluciones, retenciones y costeo avanzado | Alta | Medio: las compras quedan registradas, pero el ingreso a stock y el pago requieren control separado |
| 9. Gastos operativos | Implementado base | Gastos generales fuera de caja, categorías, proveedor opcional, estados y métodos informativos, vencimientos, edición activa, anulación, plantillas manuales y resumen agrupado | Subcategorías, centros de costo, pagos parciales reales, cuentas por pagar, adjuntos y conciliación explícita con caja/bancos | Alta | Medio: existe control administrativo, pero el movimiento real de dinero se concilia fuera del módulo |
| 10. Empleados, anticipos y roles | Implementado base | Ficha base, alta/baja, asistencia diaria, anticipos, préstamos, abonos, saldos, roles por período, snapshots, deducciones seleccionadas, preview, detalle, resumen por empleado y anulaciones lógicas | Pago real de nómina, cierre formal de períodos, IESS, décimos, vacaciones avanzadas, horas extras, comisiones, retenciones, aprobación y permisos | Alta | Medio: el cálculo queda congelado, pero el pago y movimiento real de dinero siguen fuera del sistema |
| 11. Camiones y mantenimiento | Parcial | Vehículos, placa, tipo, capacidad, combustible referencial, estado y uso en cargas | Mantenimiento, combustible consumido, kilometraje, asignaciones, documentos, costos y rentabilidad | Media | Medio: no hay alerta de mantenimiento ni costo real por vehículo |
| 12. Producción o envasado | Implementado base | Lotes, cantidades, merma, snapshots, anulación, aplicación reversible a inventario, clasificación de insumos, fórmulas, costos estimados y consumo explícito reversible por lote | Lotes de materia prima, consumo parcial avanzado, mano de obra, costos indirectos y costeo contable real | Alta | Medio: el consumo ya descuenta stock de forma controlada, pero todavía no determina el costo contable real del producto terminado |
| 13. Reportes gerenciales | Implementado base | Caja acumulada, cartera, estado de cuenta, rutas vs caja, resumen diario y mensual, panel gerencial por rango, indicadores, alertas, gráficos base, diez exportaciones Excel detalladas y cinco exportaciones PDF ejecutivas autenticadas | Rentabilidad, comparativos avanzados, programación y BI | Media | Medio: los indicadores y exportaciones son informativos y todavía no sustituyen contabilidad ni conciliación |

## Lectura por prioridad

### Prioridad alta

- Recepcion de compras en inventario y cuentas por pagar.
- Listas de precios.
- Madurez de gastos operativos: centros de costo, pagos reales y conciliación.
- Pago real de nómina y obligaciones laborales avanzadas.
- Costos reales de producción, lotes de insumo y consumo parcial avanzado.
- Automatizaciones y conciliaciones que hoy dependen del operador.

### Prioridad media

- Mantenimiento de vehículos.
- Reportes gerenciales avanzados.
- Auditoría general de cambios de datos maestros.

### Condiciones transversales

Antes de ampliar el número de usuarios o exponer el sistema fuera del equipo
local:

- Implementar roles y permisos.
- Mejorar la estrategia de sesión.
- Automatizar backups con copia externa.
- Añadir pruebas E2E y pruebas de integración PostgreSQL.
- Definir despliegue seguro, HTTPS, monitoreo y recuperación.
- Corregir contraseña/exposición de PostgreSQL.
- Resolver URL API, CORS y zona horaria para la red local.
- Probar restauración en un entorno aislado.
- Revisar manualmente migraciones mientras exista divergencia Alembic.

El detalle técnico, los riesgos y criterios están en:

- [`18-auditoria-tecnica-completa.md`](18-auditoria-tecnica-completa.md)
- [`19-hallazgos-riesgos-produccion.md`](19-hallazgos-riesgos-produccion.md)
- [`20-checklist-preparacion-servidor-local.md`](20-checklist-preparacion-servidor-local.md)
- [`21-plan-correcciones-pre-produccion.md`](21-plan-correcciones-pre-produccion.md)

## Próxima actualización

Actualizar esta matriz al terminar cada bloque del
[`roadmap de funciones obligatorias`](16-roadmap-funciones-obligatorias.md),
registrando evidencia de pruebas, migración aplicada y resultado del piloto.
