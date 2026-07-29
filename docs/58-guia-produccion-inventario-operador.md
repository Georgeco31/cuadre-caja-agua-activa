# 58 - Guía de producción e inventario para la operadora

## Propósito

Registrar únicamente información real y mantener producción e inventario
ordenados durante el piloto de agosto.

Usa siempre tu cuenta `operator`. George usa `admin_auditor` para fórmulas,
consumo de insumos, aplicación de producción, cargas, retornos, ajustes y
anulaciones.

## Regla que no se puede saltar

> Si el sistema no tiene stock disponible en bodega, el carro no se carga.

No crees una entrada, salida, producción o cantidad falsa para desbloquear una
carga. Revisa el conteo y avisa a George.

## Qué puedes registrar

- producción diaria informada por planta;
- entradas `entry` autorizadas y respaldadas;
- salidas `exit` autorizadas y respaldadas;
- observaciones y motivos claros;
- ventas, cobros, gastos y caja dentro del flujo vigente.

## Qué no debes registrar

- cantidades calculadas de memoria o estimadas;
- stock inicial sin hoja de conteo aprobada;
- ajustes positivos o negativos;
- costos;
- fórmulas o cambios de fórmula;
- consumo de insumos;
- aplicación de producción a inventario;
- cargas, retornos o cierres de ruta;
- anulaciones o correcciones;
- envases retornables como si fueran tapas consumidas;
- nómina o roles de pago dentro de este proceso.

## Antes de comenzar el día

1. Confirma que estás en tu cuenta personal.
2. Confirma la fecha.
3. Revisa que el sistema responda.
4. Confirma que tienes el soporte físico o manual.
5. Revisa con George si existe una incidencia pendiente.
6. Mantén abierto el método manual en paralelo.

Si el sistema no responde, no repitas muchas veces el mismo registro. Continúa
por el método manual desde una hora de corte y avisa a George.

## Cómo registrar producción

1. Abre **Producción**.
2. Revisa que la fecha sea la del soporte de planta.
3. Agrega el producto y presentación correctos.
4. Escribe la cantidad producida real.
5. Escribe la merma real; si el soporte no la informa, consulta antes de asumir.
6. Agrega una observación útil si corresponde.
7. Revisa todos los datos.
8. Guarda una sola vez.
9. Anota la referencia del lote en el método manual.
10. Avisa a George que el lote quedó listo para revisión.

Registrar producción **no** aumenta inventario ni consume insumos. George debe:

1. revisar la fórmula;
2. previsualizar y confirmar el consumo;
3. aplicar el producto terminado a bodega.

No hagas una entrada manual del mismo producto si George lo aplicará desde
Producción, porque duplicaría el stock.

## Cómo registrar una entrada

Usa `entry` únicamente cuando existe un soporte real y autorización.

Ejemplos de soporte:

- conteo físico inicial firmado;
- recepción física aprobada;
- corrección operativa indicada expresamente por George, sin convertirla en un
  ajuste oculto.

Pasos:

1. Abre **Inventario**.
2. Selecciona **Entrada**.
3. Confirma fecha, producto y ubicación.
4. Copia la cantidad real del soporte.
5. Escribe un motivo claro.
6. No informes costo.
7. Revisa y guarda una sola vez.
8. Comprueba que el saldo aumentó.
9. Anota la referencia del movimiento.

Para el conteo inicial, el motivo es:

`Stock inicial agosto 2026 - conteo físico`

## Cómo registrar una salida

Usa `exit` únicamente cuando un soporte indique que producto salió de esa
ubicación y el movimiento no pertenece a una carga, retorno o consumo
administrativo.

1. Abre **Inventario**.
2. Selecciona **Salida**.
3. Confirma producto y ubicación de origen.
4. Revisa el stock disponible.
5. Copia la cantidad real del soporte.
6. Escribe el motivo.
7. Revisa y guarda una sola vez.
8. Comprueba que el saldo disminuyó.
9. Anota la referencia.

Si aparece “No hay stock suficiente”, no cambies la cantidad para hacerla
pasar salvo que el soporte estuviera mal digitado. Conserva el mensaje y avisa
a George.

## Si no hay stock

1. No intentes cargar el carro.
2. No crees una entrada ficticia.
3. No uses otro producto o ubicación para reemplazarlo.
4. Revisa si la producción fue registrada.
5. Pregunta a George si la producción ya fue aplicada a bodega.
6. Compara el saldo ERP con el conteo físico.
7. Registra una incidencia si no coinciden.
8. Continúa por el método manual solo bajo la decisión de George.

## Si el sistema no permite cargar el carro

La carga la registra George con rol `admin_auditor`.

Comprueben juntos:

- producto correcto;
- ubicación de origen correcta;
- stock disponible;
- ubicación del vehículo correcta;
- vehículo y ruta activos;
- cantidad digitada;
- si la producción del día ya fue aplicada;
- si existe un movimiento pendiente o duplicado.

No se resuelve con un ajuste improvisado. Si el físico tiene producto y el ERP
no, primero se investiga la diferencia.

## Si sobran productos en el carro

1. Contar físicamente el sobrante.
2. No registrarlo como una entrada manual en bodega.
3. Entregar el conteo a George.
4. George registra el **Retorno de ruta** desde el vehículo hacia bodega.
5. Verificar que baja el stock del vehículo y sube el de bodega.
6. Comparar cargado, vendido y retornado en la hoja manual.

## Si faltan productos

1. No ocultar el faltante con una salida o ajuste.
2. Recontar producto y revisar soportes.
3. Revisar carga, ventas y retorno.
4. Informar inmediatamente a George.
5. Registrar la diferencia como incidencia.
6. George decide si se pausa la ruta o se abre un bloque de corrección.

El sistema todavía no calcula automáticamente la diferencia física de ruta.

## Bidón 20 L retornable

Un bidón retornable no se consume como una tapa. Puede salir lleno y volver
vacío para reutilizarse.

Durante este arranque:

- no lo agregues como insumo consumible por suposición;
- no mezcles bidones llenos con envases vacíos;
- anota el conteo de envases en el método manual definido por George;
- registra cualquier duda como pendiente.

## Cuándo avisar a George

Avisar antes de continuar cuando:

- no hay stock;
- el físico y el ERP no coinciden;
- falta una fórmula o un insumo;
- la producción aparece duplicada;
- se eligió producto, ubicación, fecha o cantidad incorrectos;
- el sistema rechaza una carga o retorno;
- sobra o falta producto;
- un envase retornable no tiene regla;
- se necesita anular, corregir o ajustar;
- el sistema o la red no responden.

## Cierre del día

- [ ] Producciones registradas una sola vez.
- [ ] Entradas/salidas con soporte y motivo.
- [ ] Lotes revisados por George.
- [ ] Consumos y aplicaciones pendientes identificados.
- [ ] Cargas y retornos revisados por George.
- [ ] ERP comparado con el método manual.
- [ ] Stock físico comparado cuando corresponda.
- [ ] Diferencias registradas.
- [ ] Caja y gastos cerrados según el flujo vigente.
- [ ] Decisión para el día siguiente confirmada.

La regla de cierre es sencilla: una diferencia se documenta; no se borra ni se
maquilla.
