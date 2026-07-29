# 56 - Preparación de producción, inventario e insumos para agosto

## Objetivo

Preparar el arranque operativo de agosto de 2026 con stock inicial basado en
conteo físico, producción diaria trazable, consumo controlado de insumos y
cargas de vehículos que salgan únicamente de inventario disponible.

Este documento corresponde al Bloque 60D. Es una auditoría y una guía
operativa: no registra cantidades, no modifica datos reales, no cambia costos
ni fórmulas y no reemplaza la autorización de George.

## Contexto del piloto

Agua Activa ERP está en piloto controlado y conserva el método manual en
paralelo. Los bloques recientes corrigieron la anulación de ventas, el acceso
por LAN/Tailscale/localhost y la corrección administrativa de fecha de ventas.
La producción local está migrada a `0027_sale_date_corrections`.

Durante el piloto se intentó cargar un camión cuando la bodega no tenía stock
disponible en el sistema. El rechazo fue correcto, pero evidenció que antes de
usar cargas se debe preparar el inventario inicial y entender la separación
entre producción, inventario y rutas.

## Regla principal de inventario

> **No se puede cargar un carro si el producto no está disponible primero en
> la ubicación de inventario de origen.**

La carga no crea producto. Traslada una cantidad existente desde una ubicación
de origen, normalmente bodega, hacia una ubicación de tipo vehículo. Si la
cantidad solicitada supera el stock disponible, el backend rechaza toda la
carga y no deja movimientos parciales.

No se debe resolver un rechazo creando una entrada ficticia, usando un ajuste
sin conteo, cambiando la ubicación o inventando una producción.

## Evidencia técnica del corte

Corte realizado el 2026-07-29:

| Control | Resultado |
| --- | --- |
| Git inicial | Limpio; staging vacío |
| Compose productivo | Configuración válida |
| `db` | `healthy` |
| `api` | `healthy` |
| `web` | `healthy` |
| API localhost | OK |
| API LAN | OK |
| API Tailscale | OK |
| Web LAN | OK |
| Web Tailscale | OK |
| Alembic | `0027_sale_date_corrections` |
| PostgreSQL | Puerto `5432` no publicado |
| Pruebas dirigidas | 342 aprobadas |
| Cambios de código o datos | Ninguno |

Las pruebas cubrieron inventario, permisos, producción, aplicación a
inventario, fórmulas, consumo de insumos, cargas, retornos, actividad
comercial, cierres y reportes.

## Estado actual de los módulos

| Módulo | Qué existe y funciona | Estado para agosto | Restricción o reserva |
| --- | --- | --- | --- |
| Productos | Catálogo activo, SKU, presentación, unidad, precio, tipo productivo y marca de envase retornable | Listo para verificación | Altas, cambios, precios, costos y clasificación son administrativos |
| Ubicaciones | Bodega, vehículo, área de producción u otra; vínculo opcional con vehículo | Listo si se revisan antes del conteo | La ubicación del carro debe quedar vinculada al vehículo correcto |
| Stock por ubicación | Saldo por producto y ubicación, nunca negativo | Listo para piloto | Depende de registrar el conteo inicial en la ubicación física correcta |
| Movimientos | `entry`, `exit`, ajustes, motivo, fecha, usuario, snapshots, costo opcional y anulación reversible | `entry`/`exit` listos | Para `operator`, solo entrada/salida sin costo; ajustes y anulaciones son admin |
| Producción | Lote por fecha, producto, cantidad producida, merma, notas y usuario | Listo para registro diario | Registrar el lote no aumenta stock ni consume insumos |
| Aplicación de producción | Entrada explícita y reversible del neto producido a una ubicación | Lista bajo control admin | Es una confirmación separada; no duplicarla con una entrada manual |
| Fórmulas | Fórmula por producto terminado, cantidad base, insumos, merma, vigencia y costos estimados | Lista para revisión administrativa | Debe estar activa y verificada; el sistema permite registrar producción sin fórmula |
| Consumo de insumos | Vista previa, escalamiento por cantidad producida, validación agregada de stock, salidas atómicas y anulación reversible | Listo bajo control admin | No es automático; debe confirmarse de forma explícita |
| Carga de vehículo | Traslado bodega → ubicación de vehículo, con ruta, carro, partidas y movimientos relacionados | Lista bajo control admin | Requiere stock previo; `operator` solo consulta |
| Retorno | Traslado vehículo → ubicación no vehicular, ligado a una carga, trazable y reversible | Listo bajo control admin | Solo un retorno activo por carga; no calcula automáticamente lo vendido |
| Ventas/cobros por carga | Asociación opcional a carga activa y actividad comercial consolidada | Lista para conciliación financiera | Una venta no descuenta stock del vehículo |
| Liquidación simple de ruta | Resumen por carga y producto de cargado, retornado, vendido físico, vendido registrado, ventas, cobros y dinero | Lista como apoyo de conciliación | Es de solo lectura; no crea salidas por venta ni reemplaza el conteo físico |
| Cierre de ruta | Efectivo esperado, entregado y diferencia; bloquea cambios comerciales posteriores | Listo como cierre financiero | No exige retorno previo ni liquida inventario automáticamente |
| Reportes | Stock en pantalla, resumen diario, resumen mensual y Excel de inventario/producción/rutas | Útiles para revisión | No existe reporte oficial de inventario inicial vs final por ubicación |

## Modelo de inventario auditado

### Entradas

Una entrada `entry` aumenta el stock del producto en una ubicación. Registra
fecha, cantidad, usuario, snapshots del producto y un motivo opcional a nivel
técnico. Para agosto el motivo es obligatorio por procedimiento.

La aplicación de producción también crea entradas, pero quedan ligadas al lote
y se deben anular desde Producción, no directamente desde Inventario.

### Salidas

Una salida `exit` reduce el stock de una ubicación. Si no existe saldo o la
cantidad es insuficiente, se rechaza. Las salidas de consumo, carga y retorno
quedan ligadas a su módulo de origen y se anulan desde ese módulo.

### Permisos

| Acción | `operator` | `admin_auditor` |
| --- | --- | --- |
| Consultar ubicaciones, stock y movimientos | Sí | Sí |
| Crear `entry`/`exit` sin costo | Sí | Sí |
| Crear `adjustment_in`/`adjustment_out` | No | Sí |
| Informar costo unitario en movimiento | No | Sí |
| Crear o editar ubicaciones | No | Sí |
| Anular movimientos | No | Sí |
| Registrar lote de producción | Sí | Sí |
| Aplicar producción a inventario | No | Sí |
| Confirmar/anular consumo de insumos | No | Sí |
| Crear/anular carga, retorno o cierre de ruta | No | Sí |

El motivo de una entrada/salida es técnicamente opcional. Para el piloto debe
escribirse siempre un motivo claro. Esta disciplina operativa evita movimientos
sin explicación.

## Fórmulas y consumo de insumos

- Puede haber fórmulas activas por producto y el administrador selecciona cuál
  usar para cada partida producida.
- Una fórmula activa debe tener por lo menos un insumo activo.
- El cálculo escala cada insumo según la cantidad producida y agrega el
  porcentaje de merma configurado.
- La vista previa muestra cantidad requerida, stock disponible y costo.
- La confirmación crea todas las salidas en una sola transacción.
- Si falta un insumo, no se descuenta ninguno.
- El consumo activo puede anularse con motivo y devuelve las cantidades.
- Una producción puede registrarse sin fórmula y puede quedar sin consumo.
- La aplicación del producto terminado y el consumo de insumos son acciones
  independientes.

### Regla operativa recomendada

No aplicar producto terminado a inventario si el consumo correspondiente quedó
pendiente o rechazado, salvo decisión expresa y documentada de George. El
sistema lo permite técnicamente, por lo que el control depende del
procedimiento.

### Costos

La modificación de costos y fórmulas está restringida a
`admin_auditor`. El frontend oculta costos al operador. Sin embargo, las
respuestas de lectura de productos y fórmulas todavía incluyen campos de costo
en la API autenticada; se documenta como brecha de endurecimiento y no se
cambia en este bloque.

## Cargas, retornos y cierre de ruta

### Carga

1. Seleccionar ruta activa y vehículo activo.
2. Seleccionar bodega u otra ubicación de origen.
3. Seleccionar la ubicación de tipo vehículo correspondiente al carro.
4. Revisar en pantalla el stock disponible por producto.
5. Ingresar cantidades tomadas del documento físico de carga.
6. Confirmar.

La pantalla informa el stock, pero la autoridad final es el backend. Una carga
con una partida insuficiente se rechaza completa.

### Retorno

1. Seleccionar la carga activa.
2. Contar el sobrante físico en el vehículo.
3. Elegir la bodega o ubicación no vehicular de destino.
4. Registrar únicamente lo que regresó físicamente.
5. Confirmar y revisar el stock de ambas ubicaciones.

El retorno valida que no se supere lo cargado y que el vehículo tenga stock
suficiente. No se debe usar el retorno para registrar envases vacíos
retornables sin una regla aprobada: el flujo actual está pensado para productos
de la carga.

### Ventas, liquidación simple y cierre

Las ventas y cobros pueden asociarse a una carga. El cierre financiero congela
ventas de contado, ventas a crédito, cobros, efectivo esperado, efectivo
entregado y diferencia.

El resumen de liquidación simple compara por producto:

`cargado − retornado = vendido físico`

y presenta la diferencia contra las cantidades de ventas asociadas. También
muestra ventas registradas, cobros, efectivo esperado, dinero entregado y
diferencia de dinero. Si falta retorno o dinero entregado, queda pendiente.

El flujo actual **no**:

- descuenta las ventas del inventario del carro;
- exige que exista un retorno;
- crea automáticamente movimientos por lo vendido;
- persiste una incidencia de diferencia física independiente;
- controla el ciclo del bidón retornable.

Por eso, en agosto se debe conciliar físicamente cada ruta con el método manual
y usar el resumen como apoyo, no como liquidación automática de inventario.

## Flujo recomendado para agosto

### A. Antes del 1 de agosto

1. Ejecutar health y confirmar backup.
2. Imprimir o copiar la plantilla del documento 57.
3. Confirmar productos activos, unidades, presentaciones y precios sin
   modificarlos durante el conteo.
4. Confirmar ubicaciones activas de bodega, oficina, producción y cada carro.
5. Confirmar que cada ubicación de vehículo corresponde al carro correcto.
6. Contar por separado producto terminado en bodega, carros y oficina.
7. Contar insumos por unidad real de control.
8. Identificar, sin asumir, qué envases son consumibles y cuáles retornables.
9. Revisar fórmulas activas y su unidad base.
10. Registrar el stock inicial solo después de la revisión y autorización de
    George.
11. Comparar los saldos cargados en el ERP contra la hoja física.
12. Conservar el método manual listo.

### B. Durante cada día

1. Revisar health y el último backup.
2. Confirmar que el stock inicial o el cierre anterior están conciliados.
3. La operadora registra el lote de producción con producido y merma reales.
4. George revisa el lote y la fórmula seleccionada.
5. George previsualiza y confirma el consumo de insumos si corresponde.
6. George aplica el neto producido a la ubicación de bodega.
7. Revisar que no exista una entrada manual duplicada para esa producción.
8. Revisar stock de bodega antes de preparar cargas.
9. George registra las cargas a los vehículos.
10. Registrar ventas y cobros, vinculados a la carga cuando corresponda.
11. Contar y registrar el retorno físico.
12. Registrar gastos y cerrar caja según el flujo vigente.
13. Consultar la liquidación simple y revisar las diferencias por producto.
14. Realizar el cierre financiero de ruta cuando la información esté completa.
15. Comparar ERP, físico y método manual.
16. Registrar toda diferencia como incidencia; no ocultarla con ajustes.

### C. Al cierre

- comparar inventario esperado con conteo físico por ubicación;
- comparar carga, ventas y retorno en la liquidación simple y en el método manual;
- comparar dinero esperado con dinero contado;
- revisar lotes sin consumo o sin aplicación a inventario;
- revisar cargas sin retorno o sin cierre;
- revisar movimientos sin motivo claro;
- registrar incidencias y responsable;
- dejar una decisión explícita para el día siguiente.

## Cómo registrar el stock inicial

La opción recomendada es un movimiento `entry` por producto y ubicación, con
el motivo exacto:

`Stock inicial agosto 2026 - conteo físico`

Ejemplo sin cantidad real:

| Campo | Valor |
| --- | --- |
| Producto | Bidón 20 L |
| Ubicación | La ubicación donde fue contado físicamente |
| Tipo | `entry` |
| Cantidad | Según conteo físico real |
| Costo | No ingresar ni modificar en este procedimiento |
| Motivo | `Stock inicial agosto 2026 - conteo físico` |

Reglas:

- no inventar cantidades;
- no registrar antes de terminar y firmar el conteo;
- usar un movimiento separado por ubicación;
- si el producto ya está físicamente en un carro, registrarlo en la ubicación
  de ese carro; no simular después una carga desde bodega;
- no usar ajustes para el primer conteo salvo una decisión administrativa
  posterior y documentada;
- no crear una entrada manual si la misma cantidad ya entró por aplicación de
  producción;
- guardar la referencia del movimiento en la plantilla;
- George revisa el saldo final contra el conteo.

## Tratamiento de insumos

| Grupo | Tratamiento inicial recomendado |
| --- | --- |
| Tapas, sellos y etiquetas | Insumos consumibles; contar, definir unidad y vincular a fórmula si la cantidad por producto está confirmada |
| Botellas/envases desechables | `packaging` o insumo consumible, solo después de confirmar que no regresan |
| Fundas | Insumo consumible si la unidad y cantidad por presentación están confirmadas |
| Químicos o insumos de planta | Controlar solo si el negocio define unidad, fórmula y responsable; si no, dejar pendiente |
| Bidón 20 L retornable | No tratar como tapa consumida; mantener marcado como retornable y dejar el ciclo avanzado para otro bloque |
| Otros insumos existentes | Revisar nombre, tipo productivo, unidad y fórmula antes de usarlos |

Un bidón retornable representa un activo/ciclo físico que puede salir lleno,
volver vacío, lavarse y reutilizarse. Esa vida no equivale al consumo de una
tapa. Hasta definir la regla, el piloto puede controlar el producto vendido y
el conteo físico manual de envases, pero no debe inventar consumo automático.

## Checklist de stock inicial

- [ ] Conteo físico terminado por ubicación.
- [ ] Producto terminado en bodega contado.
- [ ] Producto ya cargado en carros contado.
- [ ] Producto en oficina u otra ubicación contado.
- [ ] Unidades y presentaciones verificadas.
- [ ] Responsable y segunda revisión registrados.
- [ ] Motivo estándar confirmado.
- [ ] Entradas registradas solo con cantidades firmadas.
- [ ] Referencias de movimientos anotadas.
- [ ] Saldo ERP comparado contra la hoja física.
- [ ] Diferencias registradas sin ajustes improvisados.

## Checklist de insumos

- [ ] Cada insumo tiene nombre y unidad comprensibles.
- [ ] Tapas, sellos, etiquetas y fundas fueron contados.
- [ ] Botellas/envases fueron clasificados como consumibles o pendientes.
- [ ] Químicos incluidos tienen regla y unidad aprobadas.
- [ ] Bidón retornable está separado del consumo simple.
- [ ] Stock inicial está por ubicación.
- [ ] No se cargaron cantidades estimadas.
- [ ] Los pendientes tienen responsable y fecha de decisión.

## Checklist de recetas

- [ ] Cada producto a controlar tiene fórmula revisada o una decisión expresa
  de dejar su consumo manual.
- [ ] Producto terminado correcto.
- [ ] Cantidad base y unidad correctas.
- [ ] Insumos activos correctos.
- [ ] Cantidades requeridas confirmadas.
- [ ] Porcentaje de merma confirmado.
- [ ] Vigencia revisada.
- [ ] Costos no modificados sin autorización.
- [ ] Envases retornables no fueron agregados como consumibles por suposición.
- [ ] Vista previa revisada antes del primer consumo real.

## Checklist de producción diaria

- [ ] Fecha y soporte de planta verificados.
- [ ] Producto y presentación correctos.
- [ ] Cantidad producida real.
- [ ] Merma real.
- [ ] Lote registrado una sola vez.
- [ ] Consumo previsualizado y confirmado por admin, si aplica.
- [ ] Neto aplicado a bodega por admin.
- [ ] No existe entrada manual duplicada.
- [ ] Stock de insumos y producto terminado revisado.
- [ ] Diferencias registradas.

## Checklist de cargas de carros

- [ ] Ruta y vehículo activos.
- [ ] Ubicación de vehículo correcta.
- [ ] Documento físico de carga disponible.
- [ ] Stock de origen suficiente por producto.
- [ ] Cantidades digitadas comparadas con el documento.
- [ ] Carga registrada por `admin_auditor`.
- [ ] Stock de bodega disminuyó.
- [ ] Stock del vehículo aumentó.
- [ ] No se creó una entrada para forzar stock.
- [ ] Referencia de carga anotada.

## Checklist de retornos

- [ ] Carga activa correcta.
- [ ] Sobrante contado físicamente.
- [ ] Destino no vehicular correcto.
- [ ] Cantidad no supera lo cargado ni el stock actual del vehículo.
- [ ] Retorno registrado por `admin_auditor`.
- [ ] Stock del vehículo disminuyó.
- [ ] Stock de destino aumentó.
- [ ] Envases vacíos retornables se controlaron por separado.
- [ ] Diferencia contra ventas/carga revisada en la liquidación simple.
- [ ] Resultado comparado con el método manual.

## Checklist de cierre diario

- [ ] Health y backup revisados.
- [ ] Producciones del día completas.
- [ ] Lotes pendientes de consumo identificados.
- [ ] Lotes pendientes de aplicación identificados.
- [ ] Cargas y retornos revisados.
- [ ] Ventas y cobros conciliados.
- [ ] Liquidación simple revisada por producto.
- [ ] Cierre financiero de ruta revisado, si aplica.
- [ ] Caja cerrada según el flujo vigente.
- [ ] Inventario esperado comparado con físico.
- [ ] Método manual comparado.
- [ ] Incidencias registradas.
- [ ] George decidió continuar, pausar o corregir.

## Mínimos para arrancar agosto

- [ ] Productos activos correctos.
- [ ] Stock inicial de producto terminado.
- [ ] Stock inicial de insumos que sí entran al piloto.
- [ ] Recetas verificadas para los productos incluidos.
- [ ] Rutas, vehículos y ubicaciones verificadas.
- [ ] Precios verificados sin cambios no autorizados.
- [ ] Usuarios y roles confirmados.
- [ ] Backup reciente y tarea diaria OK.
- [ ] Método manual paralelo disponible.
- [ ] Responsable de revisión diaria definido.

Si falta stock inicial del producto que debe cargarse, no se inicia el flujo de
carga. Si falta la fórmula o el stock de un insumo, se pausa el consumo
automático de ese producto y se registra el pendiente.

## Riesgos y brechas detectadas

| Brecha | Efecto | Control temporal para agosto | Prioridad posterior |
| --- | --- | --- | --- |
| Ventas no descuentan stock del vehículo | El saldo del carro no representa automáticamente lo vendido | Conciliación manual cargado − vendido − retornado y conteo físico | Alta |
| Cierre financiero no exige retorno | Puede cerrarse dinero antes de completar el producto | Completar retorno y revisar la liquidación simple antes del cierre | Alta |
| Producción puede quedar sin consumo o sin aplicación | Insumos y terminado pueden desalinearse | Checklist diario de tres pasos y revisión de George | Alta |
| No existe reporte inicial vs final por ubicación | La diferencia diaria requiere cálculo manual | Guardar plantilla de apertura/cierre | Alta |
| Resumen simple no mueve inventario ni persiste incidencias | La diferencia es visible, pero no se liquida automáticamente | Revisar resumen y conservar hoja manual por carga | Alta |
| Envase retornable solo tiene una marca básica | No hay ciclo lleno/vacío/prestado/devuelto | Conteo manual separado; no consumir como tapa | Alta |
| Motivo de `entry`/`exit` es opcional técnicamente | Puede perderse explicación operativa | Motivo obligatorio por procedimiento | Media |
| Costos aparecen en respuestas API de lectura autenticada | El backend no aplica la misma ocultación que el frontend | No usar API directa con operador; endurecer en bloque separado | Media |
| Vigencia de fórmula no se valida al confirmar consumo | Una fórmula activa fuera de fecha puede seleccionarse | Revisión humana de vigencia antes de confirmar | Media |
| Una ubicación de vehículo puede no estar vinculada | Riesgo de seleccionar un carro ambiguo | Vincular y revisar cada ubicación antes de agosto | Media |
| No hay recepción automática de compras a inventario | Comprar un insumo no aumenta stock | Entrada controlada con soporte, sin duplicar | Media |

## Qué no debe usarse aún como control oficial

- liquidación física automática de ruta; el resumen simple es solo informativo;
- control avanzado de envases retornables;
- inventario descontado automáticamente por ventas;
- producción totalmente automática desde fórmula hasta stock;
- ajuste de diferencias sin autorización y evidencia;
- costos o fórmulas no revisados;
- reportes actuales como sustituto del conteo físico;
- nómina o roles de pago dentro de este flujo.

## Próximos bloques sugeridos

Los nombres son propuestas y no autorizan implementación:

1. **Liquidación automática completa de ruta:** convertir ventas en salidas
   reversibles, persistir incidencias y definir condición obligatoria de retorno.
2. **Inventario por venta de ruta:** salida del vehículo transaccional y
   reversible al registrar/anular la venta.
3. **Envases retornables:** lleno, vacío, entregado, devuelto, pérdida,
   cliente/ruta y saldo.
4. **Conciliación de inventario:** apertura, entradas, salidas, cierre esperado,
   conteo físico y diferencia por ubicación.
5. **Endurecimiento de producción:** vigencia de fórmulas, motivo obligatorio,
   alerta de lote incompleto y política de costos en API.
6. **Reporte de consumo:** insumo inicial, entradas, consumo por fórmula, saldo
   esperado y saldo físico.

## Recomendación final

Agosto puede iniciar con control básico si el Día 0 termina con conteos reales,
ubicaciones verificadas, recetas revisadas y stock inicial conciliado. La
secuencia segura es:

`conteo → stock inicial → producción → consumo → aplicación a bodega → carga → ventas/cobros → retorno → cierre y conciliación`.

Ante cualquier diferencia, se conserva el método manual, se registra la
incidencia y George decide. Nunca se fabrica stock en el sistema para permitir
una carga.
