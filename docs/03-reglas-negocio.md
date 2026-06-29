# 03 - Reglas de Negocio

Estas reglas definen el comportamiento esperado del MVP. En el Bloque 0 solo se documentan; no se implementan todavia.

## Reglas principales

1. Solo debe existir un cuadre principal por fecha.
2. Las cantidades de monedas y billetes deben ser mayores o iguales a cero.
3. Los gastos deben tener monto mayor a cero.
4. Los totales no deben escribirse manualmente; el sistema debe calcularlos.
5. Total monedas = suma de subtotales de monedas.
6. Total billetes = suma de subtotales de billetes.
7. Total contado = total monedas + total billetes.
8. Total gastos = suma de gastos.
9. Total final = total contado - total gastos.
10. Si un cuadre esta cerrado, cualquier cambio debe quedar registrado como correccion.
11. No borrar registros importantes sin trazabilidad.
12. Evitar duplicados por fecha.
13. Priorizar exactitud y orden antes que diseño avanzado.

## Reglas sobre cuadres diarios

- Un cuadre representa el cierre principal de una fecha.
- No deben existir dos cuadres principales para la misma fecha.
- Un cuadre puede tener notas generales.
- Un cuadre debe poder diferenciarse entre abierto y cerrado en una etapa futura.
- El cierre debe registrar fecha y hora cuando se implemente.

## Reglas sobre monedas y billetes

- Las monedas y billetes deben registrarse por denominacion.
- La cantidad de cada denominacion debe ser mayor o igual a cero.
- El subtotal de cada denominacion debe ser calculado por el sistema.
- El usuario no debe escribir manualmente los subtotales.
- Las denominaciones deben poder marcarse como activas o inactivas en una etapa futura.

## Reglas sobre gastos

- Cada gasto debe pertenecer a un cuadre.
- Cada gasto debe tener descripcion.
- Cada gasto debe tener monto mayor a cero.
- Cada gasto debe tener fecha.
- Los gastos se suman para calcular el total de gastos.
- El total de gastos se resta del total contado para obtener el total final.

## Reglas sobre totales

- El sistema debe calcular todos los totales.
- El usuario no debe modificar manualmente total monedas, total billetes, total contado, total gastos ni total final.
- Los calculos deben partir de cantidades, denominaciones y gastos registrados.

Formulas:

```text
total_monedas = suma(subtotales de monedas)
total_billetes = suma(subtotales de billetes)
total_contado = total_monedas + total_billetes
total_gastos = suma(gastos)
total_final = total_contado - total_gastos
```

## Reglas sobre cierre y correcciones

- Un cuadre cerrado no debe cambiarse de forma silenciosa.
- Si un cuadre cerrado requiere cambios, debe quedar registrado el motivo.
- La correccion debe guardar el total anterior y el total nuevo.
- La correccion debe asociarse al usuario que la realiza en una etapa futura.
- Los registros importantes no deben borrarse sin trazabilidad.

## Reglas de alcance

No agregar al MVP:

- Facturacion.
- Inventario.
- Clientes.
- Rutas de reparto.
- Ventas.
- WhatsApp.
- Reportes avanzados.
- Multiples cajas o turnos.

## Prioridad operativa

La prioridad del MVP es que el cuadre diario sea exacto, ordenado y trazable. El diseño visual avanzado y las funciones complementarias deben quedar para bloques futuros.
