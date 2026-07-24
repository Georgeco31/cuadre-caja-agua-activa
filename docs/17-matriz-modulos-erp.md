# 17 - Matriz de módulos de Agua Activa ERP

## Criterios de estado

| Estado | Significado |
| --- | --- |
| Implementado base | El flujo principal existe, pero faltan automatizaciones o funciones de madurez |
| Implementado avanzado | El flujo incluye controles, reportes y trazabilidad suficiente para piloto |
| Parcial | Solo una parte del módulo existe o el nombre agrupa capacidades ausentes |
| Pendiente | Está planificado y tiene dependencias identificadas |
| No implementado | No existe modelo, endpoint ni pantalla funcional del módulo |

La valoración corresponde al corte del Bloque 45. “Implementado” no significa
que el módulo pueda operar sin conciliación, backup o control manual.

## Matriz

| Módulo | Estado | Qué existe | Qué falta | Prioridad | Riesgo |
| --- | --- | --- | --- | --- | --- |
| 1. Caja y bancos | Parcial | Cuadre diario, denominaciones, conteos, gastos de caja, cierre, historial, correcciones, resumen y comparación con rutas | Bancos, conciliación, saldo inicial, múltiples cajas/turnos, ingreso automático y gastos generales | Alta | Alto: caja no se concilia automáticamente con ventas, cobros o bancos |
| 2. Clientes | Implementado base | Alta, consulta, filtros, edición, activación/inactivación, crédito habilitado y límite | Historial de cambios, contactos avanzados, documentos, anticipos y segmentación comercial completa | Media | Medio: cambios de maestro no tienen auditoría general |
| 3. Productos y precios | Parcial | Catálogo, SKU, presentación, precio base, costo estimado, retornabilidad y estado | Listas por cliente/ruta, vigencias, promociones, reglas de precedencia y costos reales | Alta | Alto: el precio especial depende de captura manual |
| 4. Ventas | Implementado base | Contado, crédito, múltiples ítems, snapshots, totales backend, filtros, detalle, vínculo opcional a carga y anulación | Facturación, edición controlada, devoluciones, descuentos formales y descarga automática de inventario | Alta | Alto: venta registrada no disminuye stock |
| 5. Créditos, cobros y abonos | Implementado avanzado | Límite, saldo, abonos parciales/totales, anulación reversible, cartera, vencidos y estado de cuenta | Recibos formales, cobros masivos, anticipos, refinanciación y conciliación bancaria | Alta | Alto: requiere comparación externa de comprobantes y efectivo |
| 6. Inventario | Implementado base | Ubicaciones, stock, entradas, salidas, ajustes, costos opcionales, anulación, producción, carga y retorno vinculados | Kardex/valoración avanzada, conteos físicos, transferencias generales y descarga por ventas | Alta | Alto: omitir un movimiento explícito deja módulos desalineados |
| 7. Rutas de entrega | Implementado avanzado | Rutas, cargas, inventario vehicular, retorno, actividad comercial, cierre financiero, dinero recibido y comparación con caja | Planificación, asignación formal de personal, liquidación física completa, mapas y geolocalización | Alta | Alto: cierre y recibo no cambian caja ni inventario automáticamente |
| 8. Compras y proveedores | Implementado base | Proveedores, items, snapshots, totales backend, filtros, detalle y anulación de compras | Recepción en inventario, cuentas por pagar, pagos, devoluciones, retenciones y costeo avanzado | Alta | Medio: las compras quedan registradas, pero el ingreso a stock y el pago requieren control separado |
| 9. Gastos operativos | Parcial | Gastos vinculados a un cuadre, separados antes/después del conteo | Gastos fuera de caja, categorías, proveedores, recurrencias, vencimientos, pagos y centros de costo | Alta | Alto: el reporte de caja no representa todos los gastos del negocio |
| 10. Empleados, anticipos y roles | Parcial | Ficha base, cargo, tipo, sueldo referencial, frecuencia, alta/baja | Asistencia, anticipos, préstamos, novedades, pagos, descuentos, roles y cierres de período | Alta | Alto: obligaciones laborales se controlan fuera del sistema |
| 11. Camiones y mantenimiento | Parcial | Vehículos, placa, tipo, capacidad, combustible referencial, estado y uso en cargas | Mantenimiento, combustible consumido, kilometraje, asignaciones, documentos, costos y rentabilidad | Media | Medio: no hay alerta de mantenimiento ni costo real por vehículo |
| 12. Producción o envasado | Implementado base | Lotes, cantidades, merma, snapshots, anulación y aplicación reversible a inventario | Insumos, materia prima, fórmulas, consumo, lotes de insumo, mano de obra y costeo | Alta | Alto: se conoce cantidad producida, no costo real completo |
| 13. Reportes gerenciales | Parcial | Caja acumulada, cartera, estado de cuenta, rutas vs caja, resumen diario y mensual | Gráficos, Excel/PDF, indicadores, rentabilidad, comparativos avanzados y programación | Media | Medio: decisiones gerenciales requieren consolidación externa |

## Lectura por prioridad

### Prioridad alta

- Recepcion de compras en inventario y cuentas por pagar.
- Listas de precios.
- Gastos operativos.
- Empleados avanzado.
- Producción con insumos y costos.
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

## Próxima actualización

Actualizar esta matriz al terminar cada bloque del
[`roadmap de funciones obligatorias`](16-roadmap-funciones-obligatorias.md),
registrando evidencia de pruebas, migración aplicada y resultado del piloto.
