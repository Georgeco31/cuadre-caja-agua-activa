# 15 - Guía de piloto con datos reales

## Objetivo

Validar que Agua Activa ERP representa de forma confiable la operación diaria
sin perder información ni abandonar prematuramente los controles actuales. El
piloto debe comprobar exactitud, trazabilidad, facilidad de uso, backup,
restauración y capacidad de investigar diferencias.

El piloto no busca cargar todo el historial ni activar todos los módulos el
primer día.

## Duración recomendada

Duración: **1 a 2 semanas**, idealmente entre 7 y 14 días operativos normales.

- Semana 1: datos maestros, caja y un flujo operativo limitado.
- Semana 2: ampliar gradualmente a crédito, cobros y ciclo completo de una o
  más rutas si la primera semana fue estable.

Durante todo el piloto se mantiene el registro manual o externo actual como
fuente de comparación.

## Responsables mínimos

Antes de iniciar, asignar por nombre fuera de este documento:

- Responsable de operación y digitación.
- Responsable de revisión diaria.
- Responsable de backups.
- Responsable de autorizar correcciones, anulaciones o restauraciones.

Una misma persona puede cumplir varios roles en el piloto, pero cada acción
debe quedar clara.

## Condiciones previas

- [ ] Credenciales y secretos reales configurados sin publicarlos.
- [ ] Servicios levantan y health responde.
- [ ] Login funciona.
- [ ] Backend, typecheck y build pasan.
- [ ] Alembic está en `0018_route_receipts`.
- [ ] Existe un backup de línea base.
- [ ] Se probó una restauración con datos de prueba en un entorno aislado.
- [ ] Se entiende qué operaciones no están automatizadas.
- [ ] Existe una bitácora externa de incidentes.
- [ ] Se decidió qué productos, clientes y ruta entran en el primer alcance.

## Qué datos reales ingresar primero

Ingresar solo datos verificados y en este orden:

1. **Productos**: nombre, SKU si existe, presentación, precio base y estado.
2. **Clientes del alcance**: identificación disponible, contacto, tipo y
   condiciones de crédito verificadas.
3. **Rutas y vehículos**: únicamente los que participarán en el piloto.
4. **Empleados mínimos**: solo las fichas necesarias para consulta; este módulo
   no gestiona pagos ni roles.
5. **Ubicaciones de inventario**: bodega, producción y vehículo del piloto.
6. **Inventario inicial**: desde conteo físico realizado y aprobado el mismo
   día; registrar el ajuste o entrada con referencia clara.
7. **Operaciones nuevas**: caja, producción, cargas, ventas, cobros y retornos
   desde la fecha oficial de inicio.

No inventar identificaciones, precios, cantidades, saldos ni nombres para
completar campos opcionales. Si un dato real no está disponible, validarlo
antes de usarlo en una decisión financiera.

## Qué no cargar al inicio

- Historial completo de años anteriores.
- Saldos de crédito no conciliados.
- Inventario estimado sin conteo físico.
- Datos de empleados que no sean necesarios para el alcance.
- Gastos operativos generales dentro del módulo de gastos de caja.
- Compras o proveedores simulados: el módulo todavía no existe.
- Fórmulas, insumos o costos de producción simulados.
- Precios especiales usando manualmente el precio base como sustituto.

## Semana 1

### Alcance recomendado

- Login y dashboard.
- Productos y clientes del subconjunto elegido.
- Rutas, vehículos y ubicaciones necesarias.
- Cuadre diario en paralelo con el cuadre manual.
- Conteos y gastos de caja.
- Producción y aplicación a inventario para pocos productos.
- Inventario inicial y revisión de movimientos.
- Una ruta controlada: carga, ventas seleccionadas, retorno y cierre, solo
  después de validar el stock.
- Resumen diario, rutas vs caja y backup.

### Meta de la semana

- No perder datos.
- Poder explicar cada diferencia.
- Confirmar que los operadores siguen la secuencia correcta.
- Validar que el backup se crea todos los días.
- Encontrar errores de flujo antes de ampliar el alcance.

## Semana 2

Ampliar solo si la semana 1 no dejó diferencias críticas abiertas:

- Más productos, clientes o rutas.
- Ventas a crédito.
- Cobros y abonos.
- Reportes de cartera y estados de cuenta.
- Más cargas y retornos.
- Registro de dinero de ruta en caja.
- Revisión mensual acumulada.

Cada ampliación debe empezar después de un backup.

## Módulos que deben evitarse o limitarse hasta validar

- **Ventas con efecto en inventario**: el efecto automático no existe; mantener
  conciliación manual.
- **Cartera masiva**: empezar con pocos clientes y saldos comprobados.
- **Todas las rutas a la vez**: validar primero una ruta completa.
- **Correcciones y anulaciones**: usarlas solo para errores reales, con motivo
  y autorización.
- **Producción a gran escala**: no ampliar hasta comprobar cantidades netas y
  ubicación destino.
- **Gastos operativos generales**: mantenerlos en el control actual.
- **Nómina, anticipos, préstamos y pagos**: no están implementados.
- **Compras, proveedores, insumos y costos**: no están implementados.
- **Bancos y conciliación contable**: no están implementados.
- **Uso remoto o público**: no exponer el sistema sin una revisión de
  seguridad, HTTPS, roles y estrategia de sesión.

## Flujo diario del piloto

1. Hacer health check y confirmar backup anterior.
2. Abrir o crear el cuadre del día.
3. Registrar producción y aplicarla a inventario.
4. Revisar stock y cargar el vehículo.
5. Registrar ventas y cobros con su carga cuando corresponda.
6. Contar y registrar retorno.
7. Cerrar financieramente la ruta.
8. Registrar el dinero de ruta recibido en el cuadre abierto.
9. Completar conteos y gastos de caja.
10. Comparar rutas contra caja.
11. Revisar resumen diario y control manual.
12. Investigar diferencias.
13. Cerrar el cuadre cuando corresponda.
14. Hacer backup.
15. Registrar observaciones, incluso si no hubo incidentes.

El detalle operativo está en
[`docs/14-checklist-uso-real-agua-activa.md`](14-checklist-uso-real-agua-activa.md).

## Bitácora de errores

Usar una hoja o documento externo con esta estructura:

| Campo | Contenido |
| --- | --- |
| Identificador | Código consecutivo del incidente |
| Fecha y hora | Momento en que ocurrió |
| Operador | Persona que ejecutó la acción |
| Módulo y pantalla | Lugar del sistema |
| Acción | Qué se intentó hacer |
| Identificadores | ID de cuadre, venta, carga u operación, si existe |
| Resultado esperado | Qué debía ocurrir |
| Resultado observado | Qué ocurrió |
| Mensaje | Texto del error sin contraseñas ni tokens |
| Impacto | Informativo, operativo, dinero, inventario o pérdida de acceso |
| Evidencia | Captura o referencia documental segura |
| Estado | Nuevo, investigando, resuelto o aceptado |
| Decisión | Corrección, anulación, restauración o trabajo pendiente |

### Prioridad de incidentes

- **Crítico**: pérdida de datos, total monetario incorrecto persistido,
  inventario incoherente sin explicación o imposibilidad de hacer backup.
- **Alto**: bloquea una operación principal o genera diferencia reproducible.
- **Medio**: existe alternativa manual y no altera datos.
- **Bajo**: texto, orden visual o mejora de usabilidad.

Ante un incidente crítico, detener el flujo afectado, conservar evidencia y
hacer backup del estado actual. No borrar ni restaurar automáticamente.

## Backup antes, durante y después

### Antes del piloto

```bash
./scripts/backup-db.sh
```

- Conservar el archivo de línea base.
- Copiarlo a un segundo medio seguro.
- No subirlo a Git.

### Durante el piloto

- Hacer backup al cierre de cada día.
- Hacer backup antes de una carga inicial, ampliación de alcance o corrección
  masiva.
- Confirmar nombre, fecha y tamaño del archivo.
- Mantener al menos una copia fuera del disco principal.

### Después del piloto

```bash
./scripts/backup-db.sh
```

- Etiquetar externamente el backup final con fecha y resultado del piloto.
- Probar una restauración en un entorno aislado.
- No restaurar encima de la base piloto para “comprobar” sin proteger antes el
  estado actual.

El script genera dumps con instrucciones de limpieza para los objetos
incluidos. Restaurar puede reemplazar datos; debe considerarse una operación
destructiva y controlada.

## Revisión diaria de diferencias

Para cada día, responder:

- ¿El cuadre coincide con el control manual?
- ¿Las diferencias entre rutas y caja tienen explicación documentada?
- ¿Las ventas de contado y cobros coinciden con el efectivo esperado?
- ¿La producción neta coincide con lo aplicado?
- ¿La carga menos retorno y ventas físicas coincide con el vehículo?
- ¿Los saldos de crédito coinciden con los comprobantes?
- ¿Existe alguna operación abierta o pendiente?
- ¿El backup de cierre se creó?

No considerar una diferencia como error automático: caja puede incluir dinero
de oficina u otros conceptos que no pertenecen a una ruta. La explicación debe
quedar registrada.

## Criterios para operación completa

El sistema está listo para ampliar su uso solo si:

- [ ] Completó al menos 7 días operativos sin pérdida de datos.
- [ ] Todos los backups diarios existen y uno fue restaurado en entorno
  aislado.
- [ ] Los totales de caja coinciden o cada diferencia está explicada.
- [ ] El inventario del alcance coincide con conteos físicos.
- [ ] Las rutas piloto completan carga, actividad, retorno y cierre.
- [ ] Los saldos de crédito piloto coinciden con el control externo.
- [ ] No hay incidentes críticos o altos abiertos.
- [ ] Los operadores pueden completar el checklist sin asistencia técnica
  constante.
- [ ] Las limitaciones no automatizadas siguen controladas manualmente.
- [ ] Se aprobó por escrito ampliar productos, clientes o rutas.

## Decisión final

### Avanzar

Ampliar gradualmente si todos los criterios se cumplen. Mantener backups y
conciliaciones manuales para los módulos parciales.

### Extender el piloto

Extender una semana si hay problemas de uso, diferencias explicables o
incidentes medios pendientes.

### Detener

Detener la entrada de nuevas operaciones si existe pérdida de datos,
inventario incoherente, totales persistidos incorrectos o backups no
restaurables. Conservar la base y la evidencia para investigar.

Detener el piloto no significa borrar el volumen ni los registros.
