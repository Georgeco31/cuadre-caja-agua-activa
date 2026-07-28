# 45 - Guía del piloto para George / administrador-auditor

## Objetivo

Esta guía define el control diario de George durante el piloto interno de cinco
días. El ERP funcionará en paralelo con el método actual y no será todavía el
único registro operativo ni se declarará producción definitiva.

George usa su cuenta personal `admin_auditor`. La secretaria mantiene su cuenta
personal `operator`; las cuentas no se prestan ni se comparten.

## Responsabilidades de George

- autorizar por escrito el inicio después de aprobar el Día 0;
- confirmar el alcance de cada jornada;
- revisar disponibilidad, backups y acceso;
- acompañar bloqueos e incidencias del operador;
- conciliar cierres y datos con el método actual;
- revisar reportes y exportaciones;
- evitar cambios administrativos innecesarios;
- decidir si se continúa, extiende, corrige o detiene el piloto.

## Revisión antes de cada jornada

- [ ] La PC servidor está encendida y permanecerá disponible.
- [ ] Docker Desktop y los servicios están saludables.
- [ ] La fecha y hora son correctas.
- [ ] El puesto de la secretaria abre el ERP por el acceso aprobado.
- [ ] George puede acceder por Tailscale.
- [ ] La secretaria entra con `operator`.
- [ ] George entra con `admin_auditor`.
- [ ] El backup esperado existe y la tarea terminó con resultado `0`.
- [ ] Hay espacio disponible y no se borraron backups.
- [ ] El método actual y la plantilla de incidencias están disponibles.
- [ ] No existe un incidente crítico abierto del día anterior.
- [ ] El alcance del día fue recordado a la secretaria.

Para comprobar el servidor se deben usar únicamente los procedimientos seguros
ya documentados:

- [`27-scripts-powershell-servidor-local.md`](27-scripts-powershell-servidor-local.md);
- [`30-backup-diario-programado-windows.md`](30-backup-diario-programado-windows.md).

## Revisión durante la jornada

1. Mantener disponible un canal para incidencias.
2. Confirmar que la secretaria continúa usando `operator`.
3. Revisar primero si un bloqueo corresponde a la política de permisos.
4. Evitar operar tareas diarias con `admin_auditor`.
5. No corregir o anular de inmediato: preservar la evidencia y registrar el
   motivo.
6. Confirmar que el método actual continúa recibiendo los mismos movimientos.
7. Definir un punto de corte si el ERP deja de estar disponible.

## Revisión del cierre de caja

- comparar fecha, estado y totales con el método actual;
- revisar conteos y gastos antes y después del conteo;
- confirmar que ventas y cobros incluidos tienen soporte;
- no cerrar mientras exista una diferencia sin explicar;
- si el operador ya cerró y aparece una diferencia, registrar la incidencia
  antes de considerar una corrección administrativa;
- documentar quién autorizó la corrección, el motivo y el resultado;
- no modificar datos históricos solo para hacer coincidir totales.

## Revisión de backups

Cada mañana:

1. Consultar el estado de `AguaActivaERP-BackupDiario`.
2. Confirmar que la última ejecución corresponde a la fecha esperada.
3. Confirmar resultado `0`.
4. Verificar el juego más reciente `.dump`, `.sha256` y `.json`.
5. Confirmar que la validación registrada fue satisfactoria.
6. Registrar la revisión sin copiar secretos ni archivos de negocio.

El primer disparo realmente desatendido debe aprobarse **antes** del Día 1.
Durante el piloto, una ejecución manual no debe ocultar ni reemplazar la
investigación de un fallo desatendido.

No se ejecuta un restore para comprobar un backup durante la operación. La
restauración solo se realiza con procedimiento y autorización específicos, en
un ambiente aislado.

## Revisión de reportes y exportaciones

George puede revisar en modo de solo lectura:

- panel gerencial;
- reportes diarios o mensuales aplicables;
- historial de caja;
- ventas y cartera;
- producción e inventario;
- exportaciones Excel/PDF.

Comprobar que:

- el período sea correcto;
- los totales sean coherentes con los registros del día;
- la descarga no cambie ningún dato;
- el archivo no se entregue a terceros sin revisar su contenido;
- el operador no use la cuenta administrativa para descargarlo.

## Revisión de permisos

- `operator` debe ver y operar únicamente sus módulos aprobados.
- Un mensaje “No tienes permiso” en una acción administrativa es esperado.
- Una acción sensible aceptada por backend para `operator` es un incidente
  crítico.
- Un módulo operativo permitido que bloquea de forma inesperada es una
  incidencia que debe investigarse sin prestar la cuenta admin.
- No se cambian roles o permisos durante el piloto para resolver rápidamente un
  bloqueo.

La referencia vigente es
[`42-guia-operativa-permisos-usuarios.md`](42-guia-operativa-permisos-usuarios.md).

## Si el operador reporta un bloqueo

1. Solicitar hora, módulo, acción y referencia del registro.
2. No solicitar ni usar la contraseña del operador.
3. Comparar la acción con la guía de permisos.
4. Si el bloqueo era esperado, explicar quién debe realizar la tarea.
5. Si era una acción permitida, registrar incidencia y decidir si el módulo se
   pausa.
6. Si George debe realizar una acción administrativa, usar su propia cuenta y
   dejar motivo y evidencia.
7. No ampliar permisos durante la jornada.

## Si el sistema no carga

1. Definir si falla solo un dispositivo, LAN, Tailscale o todo el ERP.
2. Anotar la hora de la última operación confirmada.
3. Indicar a la secretaria que continúe únicamente con el método actual.
4. Consultar estado y health con los scripts seguros existentes.
5. Revisar energía, conectividad y estado de Docker sin borrar ni reconstruir.
6. Abrir una incidencia y conservar capturas o mensajes útiles sin secretos.
7. Definir el punto de corte antes de cualquier reanudación.

No ejecutar migraciones, seeds, rebuild, restore ni `docker compose down -v`
como respuesta improvisada.

## Si existe una diferencia de datos

1. No cambiar ninguno de los dos registros de inmediato.
2. Identificar la primera operación diferente.
3. Comparar fecha, usuario, cliente, producto, cantidad, valor y soporte.
4. Determinar si se trata de omisión, duplicado, dato incorrecto o regla
   comprendida de manera distinta.
5. Registrar la incidencia y su gravedad.
6. Definir por escrito cuál corrección corresponde y quién la autoriza.
7. Si el sistema no permite una corrección segura, mantener la diferencia
   documentada y pausar el módulo.
8. Volver a conciliar después de cualquier acción autorizada.

No debe forzarse una coincidencia alterando datos históricos sin motivo.

## Si falla el backup

1. Clasificar la incidencia como alta; será crítica si no puede obtenerse un
   respaldo verificado.
2. Conservar los backups existentes; no borrar ni reemplazar.
3. Revisar resultado de tarea, sesión de Windows, Docker Desktop, espacio y
   salud siguiendo el documento 30.
4. Ejecutar un backup manual solo si George está autorizado y sigue el
   procedimiento documentado.
5. Verificar el resultado completo, no solo la existencia del archivo.
6. No ejecutar restore.
7. Si no hay respaldo verificado antes de continuar, detener nuevas entradas
   en el ERP y operar manualmente.

## Revisión de incidencias

Al menos al mediodía y al cierre:

- revisar incidencias abiertas;
- confirmar gravedad y responsable;
- relacionar casos repetidos;
- decidir si el módulo continúa o se pausa;
- registrar la acción tomada;
- cerrar una incidencia solo con evidencia;
- mantener abiertas las diferencias aún no conciliadas.

La plantilla oficial del piloto es
[`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md).

## Cuándo detener el piloto

Detener nuevas operaciones en el ERP si:

- hay sospecha de pérdida o corrupción de datos;
- un usuario obtiene acceso fuera de su rol;
- una credencial se comparte o compromete;
- caja, ventas o cobros presentan una diferencia material sin explicación;
- el backup falla y no se obtiene uno verificado;
- el servidor o la base fallan repetidamente;
- la indisponibilidad impide trabajar con seguridad;
- existe un incidente crítico o varios altos relacionados;
- no puede determinarse el punto de corte entre ERP y método actual.

## Cómo volver al método manual

1. George declara la pausa o detención y comunica una hora de corte.
2. Desde esa hora no se crean nuevos registros en el ERP.
3. La secretaria continúa únicamente con el método actual.
4. Se identifican por separado las operaciones ya confirmadas en el ERP y las
   posteriores al corte.
5. Se preservan datos, logs, capturas y soportes.
6. No se borra, restaura, reconstruye ni reingresa información durante la
   investigación.
7. George documenta la causa y decide si se reanuda, se extiende o se corrige
   antes de seguir.
8. La reanudación requiere un plan para evitar omisiones y duplicados.

## Recomendación sobre datos históricos

No modificar datos históricos sin registrar:

- motivo;
- registro afectado;
- valor anterior y valor correcto, cuando sea posible;
- usuario que autoriza;
- usuario que ejecuta;
- fecha y hora;
- evidencia de la conciliación posterior.

Tener permiso administrativo no reemplaza la trazabilidad.

## Checklist de cierre diario

- [ ] Caja y gastos conciliados.
- [ ] Ventas, cobros, producción e inventario usados fueron comparados.
- [ ] Reportes del día revisados por George.
- [ ] Exportaciones necesarias revisadas y protegidas.
- [ ] Incidencias actualizadas con responsable y estado.
- [ ] No hay incidentes críticos abiertos.
- [ ] Operador cerró sesión.
- [ ] Acciones administrativas excepcionales tienen motivo.
- [ ] Operaciones pendientes posteriores a una falla están identificadas.
- [ ] Decisión del día registrada: continuar, pausar un módulo o detener.
