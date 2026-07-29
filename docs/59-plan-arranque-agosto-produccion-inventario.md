# 59 - Plan de arranque de agosto: producción e inventario

## Objetivo

Organizar cinco jornadas de arranque para validar stock inicial, insumos,
producción, cargas, retornos y diferencias sin abandonar el método manual.

Completar el Día 5 no declara producción definitiva. George decide si el flujo
continúa, se extiende, requiere corrección o se detiene.

## Reglas del arranque

1. No inventar cantidades.
2. No cargar un carro sin stock disponible.
3. No duplicar una aplicación de producción con una entrada manual.
4. No tratar un envase retornable como insumo consumible sin decisión.
5. No usar ajustes para ocultar diferencias.
6. Mantener el método manual en paralelo.
7. Registrar cada incidencia.
8. Dejar fórmulas, costos, aplicaciones, consumos, cargas, retornos y
   anulaciones bajo `admin_auditor`.
9. No mezclar nómina ni roles de pago.

## Responsables

| Función | Responsable |
| --- | --- |
| Autorizar alcance y decisiones | George |
| Conteo físico | Personal designado por George |
| Registro operativo diario | Persona de oficina con `operator` |
| Fórmulas, consumo, aplicación, cargas y retornos | George o persona autorizada con `admin_auditor` |
| Conciliación diaria | George |
| Incidencias | Quien detecta; George revisa |
| Backup y health | Responsable ya definido para el piloto |

## Condiciones para comenzar

- [ ] Health productivo OK.
- [ ] Alembic en `0027_sale_date_corrections`.
- [ ] PostgreSQL 5432 no publicado.
- [ ] Backup reciente comprobado.
- [ ] Usuarios y roles confirmados.
- [ ] Método manual disponible.
- [ ] Productos y precios revisados.
- [ ] Ubicaciones y vehículos revisados.
- [ ] Plantilla del documento 57 disponible.
- [ ] George autorizó el conteo.

## Resumen

| Jornada | Objetivo | Evidencia mínima | Decisión |
| --- | --- | --- | --- |
| Día 0 | Conteo físico y preparación | Plantilla 57 completa y pendientes visibles | Autorizar o no el stock inicial |
| Día 1 | Stock inicial y primera producción | Movimientos de apertura, lote, consumo/aplicación revisados | Autorizar o pausar producción |
| Día 2 | Cargas y retornos | Carga con stock previo, conteo de carro y retorno | Autorizar o pausar rutas |
| Día 3 | Revisión de diferencias | Comparación ERP/físico/manual por ubicación y ruta | Clasificar causas |
| Día 4 | Ajuste del flujo | Procedimiento aclarado sin alterar fórmulas/costos/datos a ciegas | Repetir caso controlado |
| Día 5 | Evaluación y decisión | Resumen de cinco días, incidencias y backups | Continuar, extender, corregir o detener |

## Día 0 - Conteo físico

### Objetivo

Obtener una foto real de producto terminado, insumos y producto ya cargado en
vehículos antes del primer movimiento de agosto.

### Tareas

1. Definir hora de corte.
2. Pausar movimientos que cambien el conteo.
3. Revisar catálogo y ubicaciones.
4. Contar bodega, carro por carro y oficina.
5. Contar insumos por unidad.
6. Separar consumibles de retornables.
7. Completar el documento 57.
8. Realizar una segunda revisión.
9. Llevar faltantes o dudas a Pendientes.
10. George decide si autoriza registrar stock inicial.

### Criterio de aprobación

Todas las cantidades que se registrarán tienen conteo, ubicación, responsable
y revisión. No hay cantidades estimadas.

### Criterios de pausa

- producto principal no contado;
- ubicación de vehículo ambigua;
- unidad de insumo desconocida;
- diferencia entre dos conteos sin resolver;
- envase retornable mezclado con producto terminado.

## Día 1 - Stock inicial y primera producción

### Objetivo

Registrar la apertura por ubicación y completar un primer ciclo controlado de
producción.

### Tareas

1. Revisar health y backup.
2. Registrar `entry` con motivo
   `Stock inicial agosto 2026 - conteo físico`.
3. Comparar el saldo ERP con la plantilla.
4. Registrar la primera producción real.
5. Revisar producto, producido y merma.
6. Seleccionar y revisar la fórmula.
7. Previsualizar el consumo.
8. Confirmarlo solo si todos los insumos tienen stock y la fórmula es correcta.
9. Aplicar el neto producido a bodega.
10. Confirmar que no exista entrada manual duplicada.
11. Comparar saldos y registrar incidencias.

### Evidencia

| Campo | Registro |
| --- | --- |
| Referencias de stock inicial | |
| Referencia de producción | |
| Consumo confirmado | Sí / No / No aplica |
| Aplicación confirmada | Sí / No |
| Diferencias | |
| Decisión de George | |

### Criterio de aprobación

Stock inicial coincide con el conteo y el ciclo producción → consumo →
aplicación queda trazado sin duplicados.

## Día 2 - Cargas y retornos

### Objetivo

Validar que un carro se carga desde bodega real y que el sobrante vuelve a la
ubicación correcta.

### Tareas

1. Revisar stock de bodega.
2. Preparar documento físico de carga.
3. Seleccionar ruta, vehículo y ubicación vinculada.
4. Comparar cada cantidad contra el stock visible.
5. Registrar la carga con `admin_auditor`.
6. Verificar disminución en bodega y aumento en vehículo.
7. Vincular ventas/cobros a la carga cuando corresponda.
8. Contar sobrante físico.
9. Registrar el retorno a bodega.
10. Consultar la liquidación simple por carga y producto.
11. Comparar cargado, retornado, vendido físico y vendido registrado.
12. Comparar la liquidación simple contra la hoja física.
13. No cerrar financieramente hasta revisar ambas fuentes.

### Evidencia

| Campo | Registro |
| --- | --- |
| Referencia de carga | |
| Vehículo y ubicación verificados | Sí / No |
| Stock previo suficiente | Sí / No |
| Referencia de retorno | |
| Estado de liquidación simple | Pendiente / Cuadrada / Con diferencia |
| Diferencia de producto | |
| Diferencia de dinero | |
| Comparación manual completada | Sí / No |
| Decisión de George | |

### Criterio de aprobación

No se forzó stock, los traslados coinciden con el físico, el resumen fue
revisado y toda diferencia quedó registrada.

## Día 3 - Revisión de diferencias

### Objetivo

Encontrar el origen de cualquier diferencia sin cambiar datos a ciegas.

### Tareas

1. Recontar productos con diferencia.
2. Revisar stock inicial.
3. Revisar producción, consumo y aplicación.
4. Revisar entradas/salidas manuales.
5. Revisar carga, ventas y retorno.
6. Revisar la liquidación simple por producto y dinero.
7. Confirmar fechas y ubicaciones.
8. Clasificar cada diferencia:
   - conteo;
   - digitación;
   - movimiento duplicado;
   - producción sin aplicar;
   - consumo pendiente;
   - venta sin efecto en inventario;
   - retorno incompleto;
   - regla de envase no definida;
   - otra.
9. Definir responsable y decisión.

### Registro

| Diferencia | Causa probable | Evidencia | Decisión | Responsable | Estado |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

### Criterio de aprobación

Cada diferencia tiene causa o investigación abierta. Ninguna se ocultó con un
ajuste.

## Día 4 - Ajuste del flujo

### Objetivo

Corregir el procedimiento y repetir un caso real controlado, sin ampliar el
alcance ni cambiar fórmulas o costos sin autorización.

### Acciones permitidas

- aclarar responsables;
- cambiar el orden de los pasos;
- mejorar la hoja manual;
- agregar una revisión antes de confirmar;
- dejar un producto o insumo fuera del piloto;
- pausar una ruta;
- proponer un bloque de código separado.

### Acciones no permitidas

- inventar stock;
- borrar registros;
- ejecutar restore;
- cambiar costos o fórmulas para cuadrar;
- aplicar ajustes sin evidencia;
- modificar ventas históricas;
- implementar nómina;
- declarar resuelta una brecha sin prueba.

### Criterio de aprobación

El caso repetido sigue la secuencia correcta y no reproduce la diferencia, o
la brecha técnica queda claramente documentada para un bloque posterior.

## Día 5 - Evaluación y decisión

### Objetivo

Revisar los cinco días y decidir el siguiente alcance.

### Tareas

1. Revisar health y backups del período.
2. Revisar conteo inicial y saldo actual.
3. Revisar producciones, consumos y aplicaciones.
4. Revisar cargas, retornos y cierres.
5. Revisar diferencias e incidencias.
6. Confirmar que el método manual se mantuvo.
7. Separar módulos aprobados, pausados y no probados.
8. Registrar una decisión.

### Indicadores

| Indicador | Resultado |
| --- | --- |
| Stock inicial conciliado | |
| Días con método manual completo | |
| Producciones sin duplicado | |
| Producciones con consumo y aplicación revisados | |
| Cargas rechazadas por falta de stock | |
| Cargas forzadas con stock ficticio | Debe ser 0 |
| Rutas con comparación física completa | |
| Diferencias sin explicación | Debe ser 0 |
| Incidencias críticas abiertas | Debe ser 0 para continuar |
| Backups esperados comprobados | |

### Decisión

Marcar una:

- [ ] **Continuar:** el alcance probado es estable.
- [ ] **Extender:** falta evidencia, sin riesgo crítico.
- [ ] **Corregir antes de seguir:** existe una brecha concreta.
- [ ] **Detener:** el riesgo de datos, inventario, caja o respaldo no permite
  continuar.

| Campo | Registro |
| --- | --- |
| Fecha | |
| Decisión | |
| Productos incluidos | |
| Insumos incluidos | |
| Rutas incluidas | |
| Módulos aprobados | |
| Módulos pausados | |
| Brechas para siguiente bloque | |
| Responsable | George |
| Próxima revisión | |

## Control diario común

### Apertura

- [ ] Health OK.
- [ ] Backup revisado.
- [ ] Usuario y fecha correctos.
- [ ] Incidencias anteriores revisadas.
- [ ] Método manual disponible.

### Cierre

- [ ] Producción conciliada.
- [ ] Insumos conciliados.
- [ ] Bodega conciliada.
- [ ] Vehículos conciliados.
- [ ] Ventas/cobros conciliados.
- [ ] Liquidaciones simples de rutas revisadas.
- [ ] Caja conciliada.
- [ ] Diferencias registradas.
- [ ] Decisión del día confirmada.

## Criterios de detención inmediata

- stock creado sin soporte físico;
- carga realizada desde una ubicación incorrecta;
- diferencia material sin trazabilidad;
- pérdida de datos o backup no disponible;
- cuentas compartidas;
- cambio de costos, fórmulas o permisos sin autorización;
- intento de ocultar una diferencia mediante borrado, ajuste o duplicado;
- uso del flujo de envase retornable sin regla aprobada.

Al detener un flujo, el método manual continúa desde una hora de corte clara y
se registra la incidencia.
