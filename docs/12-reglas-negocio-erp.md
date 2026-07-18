# 12 - Reglas de Negocio ERP

Este documento define reglas generales para crecer desde el modulo actual de caja hacia Agua Activa ERP sin perder exactitud ni trazabilidad.

## Reglas generales

- No borrar registros importantes sin trazabilidad.
- Los totales monetarios deben calcularse en backend.
- Usar `Decimal` o manejo seguro de dinero.
- No usar floats para dinero.
- Mantener auditoria en operaciones sensibles.
- Cada modulo debe probarse antes de avanzar al siguiente.
- No mezclar ventas, inventario, rutas y caja sin reglas claras.
- Los datos maestros deben existir antes de ventas.
- Los clientes deben existir antes de ventas a credito.
- Los productos deben existir antes de inventario y ventas.
- Las rutas deben existir antes del cierre de ruta.
- Los empleados deben existir antes de roles de pago.
- La caja debe poder compararse contra ventas, cobros y rutas.
- Los gastos antes del conteo no se restan del total final de caja.
- Los gastos despues del conteo si se restan del total final de caja.
- El sistema debe priorizar exactitud y trazabilidad antes que diseno avanzado.

## Reglas de crecimiento

- No implementar modulos grandes de golpe.
- Cada bloque debe tener objetivo, alcance, pruebas y commit separado.
- No crear tablas sin haber definido reglas de negocio.
- No crear pantallas sin tener claro el flujo real.
- No inventar datos del negocio.
- Si falta informacion, marcarla como pendiente.

## Reglas sobre datos maestros

- Los datos maestros deben ser claros, reutilizables y faciles de mantener.
- Clientes, productos, empleados, vehiculos y rutas deben evitar duplicados.
- Un dato maestro inactivo no debe eliminarse si ya tiene movimientos historicos.
- Los cambios sensibles en datos maestros deben quedar registrados cuando el modulo lo requiera.

## Reglas sobre dinero

- Los montos deben guardarse y calcularse con precision decimal.
- Los totales oficiales no deben depender del frontend.
- Caja, ventas, cobros, gastos, compras y pagos deben poder compararse.
- Cualquier diferencia entre dinero esperado y dinero recibido debe poder investigarse.

## Reglas sobre inventario y produccion

- El inventario debe moverse por entradas, salidas, devoluciones o ajustes documentados.
- La produccion debe aumentar inventario disponible cuando corresponda.
- Las ventas deben disminuir inventario cuando el flujo se implemente.
- El inventario por camion debe poder compararse contra carga, ventas y retorno.

## Reglas sobre rutas

- Una ruta debe tener fecha, responsable y camion cuando el flujo lo requiera.
- El cierre de ruta debe comparar productos cargados, vendidos y retornados.
- El dinero de ruta debe poder compararse contra ventas de contado, cobros y gastos de ruta.
- Las diferencias de ruta deben quedar registradas.

## Reglas sobre auditoria

- Las operaciones sensibles deben guardar usuario, fecha y motivo cuando aplique.
- Las correcciones no deben ocultar el dato anterior.
- El sistema debe conservar historial suficiente para revisar errores operativos.
