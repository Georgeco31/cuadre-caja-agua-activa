# 64 - Plan de limpieza de ventas de ruta del 2026-08-01

## Decisión actual

**No anular todavía.** George indicó que probablemente existen ventas de ruta
registradas en módulos oficiales el 1 de agosto, pero 63A solo prepara una
identificación de lectura. No se modifican ventas, abonos, cierres, caja,
reportes ni inventario.

## Dry-run

Solo `admin_auditor` puede consultar:

```text
GET /api/v1/simple-routes/cleanup/august-1-route-sales-dry-run
```

El filtro fijo es `sale_date = 2026-08-01` y `route_load_id IS NOT NULL`. El
reporte devuelve ID, número, cliente snapshot, tipo, estado, total, cobrado,
saldo, abonos activos, carga, cierre, cuadre de la fecha, posibilidad técnica,
riesgo y motivo sugerido. `modified_records` siempre es `0`.

## Validación productiva 63A-2 del 2026-08-06

Con Alembic en `0029_simple_routes`, el endpoint productivo identificó 14
candidatas para el 2026-08-01 y devolvió `modified_records = 0`. El acceso
administrativo respondió `200` y `operator` recibió `403`.

Antes y después de ejecutar el dry-run se conservaron 321 ventas oficiales, 15
abonos oficiales y 0 hojas de Rutas Simples. No se anuló ninguna venta, no se
crearon cobros, no se alteraron cierres y no se modificó caja, inventario o
nómina. La revisión manual y cualquier anulación continúan pendientes de una
autorización explícita de George con IDs exactos.

## Criterios para considerar una candidata

Una fila del dry-run no autoriza anulación. Debe comprobarse contra la hoja
física y confirmarse que:

1. corresponde realmente a una venta informal de ruta;
2. no es una venta oficial legítima de contado o crédito;
3. producto, cantidad, precio, cobrado y saldo coinciden con la hoja física;
4. no existen abonos oficiales que deban anularse primero;
5. la carga no tiene cierre financiero activo que bloquee la venta;
6. caja y reportes del día fueron identificados antes de cambiar algo;
7. George autoriza por escrito los IDs exactos.

## Riesgos

- reducir indebidamente ventas oficiales;
- alterar cartera y abonos activos;
- desalinear un cierre de ruta tradicional;
- cambiar reportes históricos del día;
- explicar dos veces el mismo efectivo en caja;
- confundir una venta real con una operación informal.

## Motivo recomendado

```text
Venta de ruta del 2026-08-01 migrada al módulo independiente,
previa autorización de George
```

El motivo debe ampliarse con el documento de autorización y el ID de la hoja
física o digital correspondiente; no debe copiarse sin verificación.

## Procedimiento futuro con autorización

1. Crear y validar backup.
2. Guardar dry-run firmado con los IDs autorizados.
3. Tomar conteos y totales de ventas, abonos, caja, cierres y reportes.
4. Verificar que no haya sesiones operando sobre la fecha.
5. Anular primero abonos oficiales autorizados si la venta crédito los tiene.
6. Resolver o anular el cierre tradicional autorizado antes de la venta.
7. Anular cada venta mediante el endpoint oficial existente y motivo completo.
8. No borrar filas ni ejecutar SQL manual de eliminación.
9. Registrar la operación equivalente en Rutas Simples solo desde la hoja real;
   no inventar cliente, producto, cantidad o precio.
10. Conciliar el efectivo de Rutas Simples con el cuadre sin duplicarlo.

## Verificación posterior

- las ventas autorizadas quedan `voided`, no eliminadas;
- los demás registros del 1 de agosto conservan estado y totales;
- no quedan abonos activos apuntando a ventas anuladas;
- cierres tradicionales y recibos de ruta quedan coherentes;
- caja física no se incrementa ni reduce automáticamente;
- reportes excluyen anuladas conforme a sus reglas actuales;
- inventario, nómina, usuarios y credenciales no cambian;
- health, pytest, frontend test, typecheck y build pasan.

Si cualquier conciliación no coincide, detener la limpieza. No restaurar ni
borrar datos sin un procedimiento nuevo y autorización expresa.
