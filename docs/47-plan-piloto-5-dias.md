# 47 - Plan del piloto paralelo de cinco días

## Propósito

Probar Agua Activa ERP durante cinco jornadas operativas, manteniendo en
paralelo el método actual. El plan incluye un Día 0 de preparación que no
cuenta como jornada del piloto.

Completar el Día 5 no declara producción definitiva. La decisión final puede
ser continuar, extender, corregir antes de seguir o detener.

## Condición previa

No comenzar el Día 1 hasta que George haya aprobado todas las condiciones de
[`43-preparacion-piloto-interno.md`](43-preparacion-piloto-interno.md), incluidos:

- primer backup diario realmente desatendido;
- contraseñas definitivas;
- usuarios reales e individuales;
- reserva DHCP;
- disponibilidad del servidor y Docker;
- acceso real de la secretaria por LAN;
- acceso real de George por Tailscale;
- prohibición de cuentas compartidas.

## Reglas para los cinco días

1. Registrar en el ERP y en el método actual todas las operaciones incluidas.
2. Conciliar ambos registros cada día.
3. Usar `operator` para el trabajo de oficina y `admin_auditor` para control.
4. No ampliar el alcance durante una jornada.
5. No corregir históricos, anular ni ajustar sin motivo y autorización.
6. Registrar toda diferencia o falla en la plantilla de incidencias.
7. Ante una pausa, continuar manualmente desde una hora de corte definida.
8. No borrar datos ni ejecutar restore, migraciones, seeds o
   `docker compose down -v`.

## Resumen del plan

| Día | Objetivo | Tareas principales | Responsable | Evidencia | Criterio de aprobación | Riesgos principales |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | Dejar personas, acceso y continuidad listos | Usuarios, contraseñas, LAN/Tailscale, servidor, Docker, backup y práctica | George; secretaria participa | Checklist 43 completo, accesos y backup comprobados | Todas las condiciones obligatorias cerradas y autorización de George | Inicio prematuro, cuenta compartida, IP cambiante, backup no comprobado |
| 1 | Validar el flujo básico diario | Login, dashboard, caja y gastos | Secretaria opera; George revisa | Cuadre, gastos, conciliación e incidencias | Flujo completo y totales conciliados sin incidente crítico | Cierre anticipado, gasto en etapa incorrecta, diferencia de caja |
| 2 | Validar el flujo comercial | Clientes, ventas, cobros y crédito si fue aprobado | Secretaria opera; George concilia | Referencias de clientes, ventas/cobros y comparación manual | Operaciones del día completas, sin duplicados y con saldos coherentes | Cliente incorrecto, duplicado, crédito no preparado |
| 3 | Validar producción e inventario operativo | Producción diaria y movimientos `entry`/`exit` | Secretaria registra; George revisa | Producción, movimientos y soportes paralelos | Cantidades conciliadas; sin costos, ajustes ni consumos | Ubicación o cantidad incorrecta, confundir producción con movimiento de stock |
| 4 | Validar control administrativo y permisos | Reportes, exportaciones y revisión de permisos; operación base continúa | George; secretaria confirma su vista | Excel/PDF controlados, reporte diario, incidencias de permisos | Solo admin accede a información sensible; reportes coherentes | Exposición de datos, préstamo de cuenta, interpretar reporte como asiento automático |
| 5 | Cerrar y decidir | Operación normal, conciliación global y evaluación | Ambos; George decide | Checklist final, resumen de incidencias y decisión firmada | Cinco días conciliados o diferencias explicadas; decisión registrada | Aprobar con incidentes abiertos, declarar producción definitiva antes de tiempo |

## Día 0 - Preparación

### Objetivo

Comprobar que personas, equipos, accesos, respaldo y contingencia están listos
sin registrar operación real del piloto.

### Tareas

- cerrar todas las casillas obligatorias del documento 43;
- rotar las contraseñas definitivas por un canal seguro;
- confirmar cuentas individuales activas y roles correctos;
- configurar y probar la reserva DHCP;
- confirmar horario de encendido de KERNELOS-PC;
- comprobar el inicio correcto de Docker Desktop;
- probar el acceso de la secretaria con `operator` desde su equipo;
- probar el acceso de George con `admin_auditor` por Tailscale;
- confirmar la primera ejecución desatendida real del backup;
- preparar el método actual y la plantilla de incidencias;
- decidir si ventas a crédito entran en el Día 2;
- practicar el flujo básico sin crear, cerrar, corregir ni borrar datos reales;
- registrar la autorización de George para el Día 1.

### Responsables

- George: aprobación, usuarios, accesos, backup y decisión de inicio.
- Secretaria: confirmar acceso, cuenta y comprensión de la guía.
- Técnico de red, si aplica: reserva DHCP.

### Evidencia

- checklist 43 completo;
- fecha y resultado del backup desatendido;
- pruebas de acceso sin contraseñas;
- dirección estable del servidor;
- nombre y rol de cada cuenta;
- decisión sobre ventas a crédito;
- autorización de inicio.

### Criterio de aprobación

Todos los pendientes obligatorios están cerrados. Una sola casilla obligatoria
vacía mueve el Día 1 y no se considera un fallo del piloto.

### Riesgos

- usar una prueba manual como si fuera ejecución desatendida;
- probar desde un dispositivo distinto al de la operación;
- compartir la cuenta admin para ahorrar tiempo;
- empezar sin método manual disponible.

## Día 1 - Login, dashboard, caja y gastos

### Objetivo

Completar el flujo básico de una jornada y validar el cuadre diario.

### Tareas

- iniciar sesión con cuentas individuales;
- revisar fecha, rol y dashboard;
- abrir o consultar el cuadre del día;
- registrar conteos y gastos reales;
- mantener el registro en el método actual;
- comparar totales antes del cierre;
- cerrar el cuadre solo si corresponde y no hay diferencias;
- registrar incidencias.

### Responsables

- Secretaria: registro operativo paralelo.
- George: disponibilidad, permisos, conciliación y autorización ante dudas.

### Evidencia

- referencia del cuadre;
- cantidad de gastos registrados;
- comparación de totales sin publicar datos sensibles;
- checklist de fin de jornada;
- incidencias del Día 1.

### Criterio de aprobación

El flujo se completa con la cuenta de operador, el cuadre coincide con el
método actual o toda diferencia está explicada, y no hay incidentes críticos.

### Riesgos

- abrir o cerrar el cuadre equivocado;
- clasificar mal un gasto;
- intentar corregir después del cierre;
- omitir el registro paralelo.

## Día 2 - Clientes, ventas y cobros

### Objetivo

Validar la operación comercial diaria y la coherencia de los saldos usados.

### Tareas

- consultar o crear clientes necesarios;
- registrar ventas de contado;
- registrar cobros y abonos aplicables;
- usar ventas a crédito solo si fueron aprobadas en el Día 0;
- comparar cada operación con su soporte manual;
- revisar duplicados, cliente, productos, cantidades y valores;
- conciliar el resumen del día;
- registrar incidencias.

### Responsables

- Secretaria: clientes, ventas y cobros.
- George: revisión de diferencias, cartera y alcance del crédito.

### Evidencia

- cantidad de clientes creados o consultados;
- referencias de ventas y cobros;
- conciliación con el método actual;
- confirmación de inclusión o exclusión del crédito;
- incidencias del Día 2.

### Criterio de aprobación

No existen operaciones duplicadas; clientes, valores y saldos son coherentes;
las diferencias están explicadas y no hay incidentes críticos.

### Riesgos

- seleccionar cliente o venta incorrectos;
- registrar dos veces una operación;
- probar crédito sin proceso aprobado;
- asumir que una venta mueve inventario automáticamente.

## Día 3 - Producción e inventario

### Objetivo

Validar producción diaria y movimientos operativos de inventario sin entrar en
costos, fórmulas, ajustes ni consumo de insumos.

### Tareas

- registrar la producción real informada;
- registrar únicamente entradas y salidas operativas necesarias;
- confirmar producto, ubicación y cantidad;
- mantener el soporte paralelo;
- comparar cantidades al cierre;
- registrar incidencias.

### Responsables

- Secretaria: registro de producción e inventario permitido.
- George: revisión de cantidades y restricciones.

### Evidencia

- referencias de producción;
- referencias de movimientos `entry`/`exit`;
- comparación de cantidades;
- incidencias del Día 3.

### Criterio de aprobación

Las cantidades coinciden con el método actual o están explicadas; no se usaron
ajustes, costos, fórmulas, anulaciones ni consumo de insumos.

### Riesgos

- producto o ubicación incorrectos;
- duplicar producción y entrada de stock;
- asumir que registrar producción aumenta stock automáticamente;
- intentar un ajuste para ocultar una diferencia.

## Día 4 - Reportes, exportaciones y permisos

### Objetivo

Confirmar que George puede controlar la operación y que la secretaria conserva
únicamente el acceso operativo.

### Tareas

- mantener el flujo básico de la jornada;
- revisar reportes aplicables por rango correcto;
- generar una muestra controlada de Excel y PDF;
- comparar totales con los registros diarios;
- confirmar que exportar no modifica datos;
- revisar los destinos visibles de ambos roles;
- comprobar bloqueos esperados sin intentar acciones destructivas;
- actualizar incidencias.

### Responsables

- George: reportes, exportaciones y revisión de permisos.
- Secretaria: confirmar su panel operativo y continuar sus tareas normales.

### Evidencia

- nombre y período de reportes revisados;
- archivos guardados en ubicación controlada;
- confirmación de accesos por rol;
- conciliación de totales;
- incidencias del Día 4.

### Criterio de aprobación

George accede a reportes y exportaciones; la secretaria no accede a funciones
administrativas; los totales revisados son coherentes y no cambian datos.

### Riesgos

- entregar un archivo sensible sin revisión;
- usar o prestar la cuenta administrativa;
- confundir un reporte con una conciliación automática;
- cambiar permisos para resolver una duda.

## Día 5 - Cierre, evaluación y decisión

### Objetivo

Completar la última jornada, revisar los cinco días y registrar una decisión
controlada.

### Tareas

- realizar el flujo operativo acordado;
- conciliar ERP y método actual;
- revisar todas las incidencias y diferencias;
- confirmar backups del período;
- evaluar facilidad de uso para la secretaria;
- revisar estabilidad, permisos y calidad de datos;
- clasificar pendientes obligatorios antes de una siguiente fase;
- registrar la decisión final.

### Responsables

- Secretaria: cierre operativo y retroalimentación.
- George: revisión global y decisión.

### Evidencia

- conciliación de cada jornada;
- resumen de incidencias por gravedad y estado;
- verificación de backups;
- lista de módulos aprobados, pausados o no probados;
- decisión final y responsable.

### Criterio de aprobación

Los cinco días están conciliados o tienen diferencias explicadas; no hay
incidentes críticos abiertos; los incidentes altos tienen decisión y
responsable; el resultado final queda registrado.

### Riesgos

- cerrar incidencias sin evidencia;
- considerar el silencio como aprobación;
- aprobar módulos que no fueron probados;
- declarar producción definitiva solo por completar el calendario.

## Indicadores de evaluación

| Indicador | Meta del piloto |
| --- | --- |
| Jornadas conciliadas | 5 de 5 |
| Incidentes críticos abiertos al cierre | 0 |
| Operaciones con cuenta compartida | 0 |
| Backups diarios esperados comprobados | 100 % |
| Diferencias monetarias sin explicación | 0 |
| Accesos indebidos por rol | 0 |
| Incidencias con responsable y estado | 100 % |
| Jornadas con método actual completo | 5 de 5 |

Las metas sirven para decidir; no deben maquillarse corrigiendo datos sin
trazabilidad.

## Decisión final

Marcar una sola opción:

- [ ] **Continuar:** el alcance probado es estable y puede pasar a una siguiente
  fase controlada. No significa producción definitiva.
- [ ] **Extender piloto:** faltan días o casos para obtener evidencia, sin un
  riesgo que obligue a detener.
- [ ] **Corregir antes de seguir:** existen fallos concretos que requieren un
  bloque de corrección y nueva validación.
- [ ] **Detener:** el riesgo operativo, de seguridad, respaldo o integridad no
  permite continuar.

Registrar:

| Campo | Decisión |
| --- | --- |
| Fecha | |
| Opción elegida | |
| Alcance aprobado | |
| Módulos no aprobados | |
| Incidencias abiertas | |
| Correcciones requeridas | |
| Próxima revisión | |
| Responsable de la decisión | George |
| Observaciones | |

## Cierre

El piloto termina con una evaluación, no con un cambio automático de estado.
Cualquier paso hacia producción definitiva requiere una autorización posterior
y un alcance propio.
