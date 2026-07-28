# 48 - Cierre de pendientes pre-piloto

## Objetivo

Registrar el corte operativo del Bloque 59B y decidir si Agua Activa ERP puede
iniciar el piloto interno paralelo. Este bloque verifica usuarios, respaldos,
servidor, Docker, red y condiciones del Día 0 sin iniciar el piloto, cambiar
credenciales, modificar datos ni ejecutar una restauración.

Fecha del corte: **2026-07-28**.

## Actualización del Bloque 59D

El Bloque 59D repitió las verificaciones técnicas sin iniciar el piloto ni
modificar credenciales:

- el árbol Git estaba limpio al inicio y `git diff --check` aprobó;
- `db`, `api` y `web` continúan `healthy`;
- LAN y Tailscale responden desde `KERNELOS-PC`;
- Alembic continúa en `0026_user_roles` y PostgreSQL `5432` no está publicado;
- `admin` y `estherdelgado31` continúan activos con los roles esperados;
- la tarea de backup está `Ready`, su última ejecución fue
  2026-07-28 06:41:41 y `LastTaskResult` continúa en `0`;
- la próxima ejecución natural permanece programada para
  2026-07-28 23:30:30 como control rutinario;
- la suspensión con corriente alterna está configurada en `Nunca`;
- las pruebas desde los dispositivos reales terminaron OK;
- las credenciales definitivas fueron rotadas mediante entrada local oculta;
- George confirmó `KERNELOS-PC`, Docker y el método manual paralelo;
- George aceptó temporalmente el riesgo DHCP; la reserva continúa pendiente;
- faltan las reglas expresas de cuentas personales, las pruebas de cada titular
  después de la rotación, responsables operativos y autorización final.

La evidencia y la confirmación ejecutable actualizadas están en:

- [`51-usuarios-accesos-pre-piloto.md`](51-usuarios-accesos-pre-piloto.md);
- [`52-confirmacion-dia-0-pre-piloto.md`](52-confirmacion-dia-0-pre-piloto.md).

La decisión final 59D cambia a **LISTO CON RESERVAS PARA PILOTO CONTROLADO**.

## Decisión ejecutiva

**LISTO PARA PILOTO CONTROLADO, CON RIESGO DHCP ACEPTADO TEMPORALMENTE.**

La infraestructura productiva local está saludable, las cuentas requeridas
existen activas con los roles correctos y el Bloque 59C corrigió y validó la
tarea diaria con `LastTaskResult = 0`. Las credenciales, accesos reales,
servidor, método paralelo y decisión DHCP avanzaron en 59D. George cerró además
las reglas de cuentas personales, la confirmación posterior de cada titular y
los responsables de servidor, conciliación, incidencias y backup.

El piloto no fue iniciado. La autorización permite dejar preparado el inicio
controlado, que solo debe ejecutarse en el bloque siguiente. Los checklists
finales están en
[`49-checklist-dia-0-piloto.md`](49-checklist-dia-0-piloto.md) y
[`52-confirmacion-dia-0-pre-piloto.md`](52-confirmacion-dia-0-pre-piloto.md).

## Escala de estados

| Estado | Significado |
| --- | --- |
| Confirmado | Existe evidencia actual suficiente para cerrar el punto técnico |
| Parcial | Existe evidencia técnica, pero falta una confirmación humana o prueba en el dispositivo requerido |
| Bloqueador | Impide autorizar el Día 1 |
| Riesgo aceptado | No bloquea el piloto controlado; exige control y criterio de detención |
| No ejecutado | La acción requería autorización explícita o estaba fuera del alcance |

## Resultado de pendientes

| Pendiente | Estado | Evidencia o acción requerida |
| --- | --- | --- |
| Cuentas requeridas activas y con rol correcto | Confirmado | La base contiene `admin` activo con rol `admin_auditor`, creado el 2026-07-27 10:42:41, y `estherdelgado31` activa con rol `operator`, creada el 2026-07-27 11:28:11 |
| Cuentas individuales, sin uso compartido | Confirmado | `admin` pertenece a George y `estherdelgado31` a la persona de oficina; no se comparten |
| Operadora no usa la cuenta administrativa | Confirmado | `admin` se reserva para George y no se usa en operación diaria |
| George reconoce cuál cuenta corresponde a cada rol | Confirmado | George autorizó las acciones sobre `admin` y `estherdelgado31` con sus roles esperados |
| Contraseñas definitivas fuertes y vigentes | Confirmado | Rotación segura completada; no se documentaron valores |
| Tarea diaria registrada | Confirmado | `AguaActivaERP-BackupDiario` existe, está `Ready` y conserva su disparador diario |
| Última ejecución de la tarea exitosa | Confirmado | El Bloque 59C corrigió la tarea y `Start-ScheduledTask` terminó con resultado `0`; la próxima ejecución natural debe revisarse como control operativo |
| Backup existente reciente y legible | Confirmado | El juego creado por la tarea el 2026-07-28 06:41 tiene dump, checksum y metadata; el hash coincide, el JSON es válido y `pg_restore --list` aprobó |
| Backup manual nuevo del Bloque 59C | Confirmado | La prueba manual del script creó y validó un juego separado antes de probar la tarea |
| Endpoint LAN disponible | Confirmado | API y Web responden desde KERNELOS-PC en `192.168.100.220` |
| Prueba LAN desde el dispositivo de oficina | Confirmado | George informó resultado OK para `operator` desde el dispositivo real de oficina |
| Endpoint Tailscale disponible | Confirmado | API y Web responden desde KERNELOS-PC en `100.121.163.126` |
| Prueba Tailscale desde el dispositivo de George | Confirmado | George informó resultado OK para `admin_auditor` desde su dispositivo real |
| KERNELOS-PC identificado como servidor | Confirmado | George confirmó que será el servidor local durante el piloto |
| PC disponible durante el horario operativo | Confirmado | Permanecerá encendido; George es responsable del servidor |
| Docker Desktop disponible | Confirmado | Docker está operativo y George confirmó su disponibilidad durante el horario |
| Windows sin suspensión durante el uso | Confirmado | 59D reconfirmó `Sleep after = Nunca` con corriente y George confirmó que Windows no debe suspenderse |
| Docker y servicios saludables | Confirmado | `db`, `api` y `web` están `healthy`; health terminó con cero fallos y cero advertencias |
| PostgreSQL protegido | Confirmado | El puerto `5432` no está publicado |
| Migración vigente | Confirmado | Alembic está en `0026_user_roles` |
| Compose productivo válido | Confirmado | `docker compose ... config --quiet` terminó correctamente |
| Reserva DHCP | Riesgo aceptado | Continúa pendiente; George aceptó temporalmente el riesgo para el piloto controlado |
| Checklist Día 0 | Confirmado | George completó las confirmaciones finales y autorizó dejar el sistema listo con reserva DHCP |
| Piloto interno | No ejecutado | No se inició ninguna jornada ni se registró operación de piloto |

## Usuarios y contraseñas

La consulta se limitó a nombre de usuario, rol y estado activo. No se consultaron,
mostraron ni documentaron contraseñas o hashes.

| Usuario | Rol | Estado técnico | Confirmación humana |
| --- | --- | --- | --- |
| `admin` | `admin_auditor` | Activo | Cuenta personal de George; no se comparte ni se usa en operación diaria |
| `estherdelgado31` | `operator` | Activa | Cuenta personal de oficina; no se comparte |

- contraseña admin rotada correctamente;
- contraseña estherdelgado31 rotada correctamente.

Cada titular recibió su credencial de forma privada y volvió a iniciar sesión
con su propia cuenta después de la rotación.

## Backup diario

La comprobación posterior al Bloque 59C devolvió:

| Dato | Resultado |
| --- | --- |
| Tarea | `AguaActivaERP-BackupDiario` |
| Estado | `Ready` |
| Próxima ejecución | 2026-07-28 23:30:30 |
| Última ejecución | 2026-07-28 06:41:41 |
| Último resultado | `0` |
| Acción configurada | Script seguro `prod-local-backup-db.ps1` |
| Directorio de inicio | Raíz absoluta del repositorio |
| Tipo de inicio | Usuario interactivo, nivel limitado |
| Reintentos | 3, cada 5 minutos |
| Iniciar cuando esté disponible | Sí |

La causa del resultado histórico `1` fue la indisponibilidad de Docker: sus logs
registraron apagado del backend a las 23:28:06 y un error de conexión al motor a
las 23:30:01, inmediatamente antes de la tarea de las 23:30:30. La tarea no
tenía reintentos y el script no guardaba logs.

La corrección fijó el directorio de inicio, activó `StartWhenAvailable`, añadió
tres reintentos cada cinco minutos y creó logging seguro por ejecución en
`backups/logs`. La evidencia completa está en
[`50-diagnostico-backup-diario-desatendido.md`](50-diagnostico-backup-diario-desatendido.md).

## Backup generado por la tarea y validado

La tarea corregida creó el backup más reciente, comprobado sin restaurarlo:

- archivo: `agua-activa-postgres-20260728-064137.dump`;
- fecha local: 2026-07-28 06:41;
- tamaño: 281631 bytes;
- archivo `.dump`: presente;
- archivo `.sha256`: presente y coincide con el dump;
- archivo `.json`: presente y se puede interpretar;
- `pg_restore --list`: **OK**;
- copia temporal dentro de `db` usada solo por `pg_restore --list` y retirada
  después de la validación;
- log seguro `backup-task-20260728-064137.log` con resultado OK;
- ningún backup se añadió a Git.

La validación independiente solo ejecutó `pg_restore --list`; no creó una base
ni ejecutó restore.

## Acceso LAN

El health actual confirma:

- API LAN: `http://192.168.100.220:8010/api/v1/health`, **OK**;
- Web LAN: `http://192.168.100.220:3000/login`, **OK**.

George confirmó resultado **OK** desde el dispositivo real de oficina:

- [x] abrir `http://192.168.100.220:3000/login`;
- [x] iniciar sesión con la cuenta de rol `operator`;
- [x] cargar el dashboard;
- [x] comprobar los 22 destinos y restricciones administrativas;
- [x] abrir una pantalla operativa permitida.

## Acceso Tailscale

El health actual confirma:

- API Tailscale: `http://100.121.163.126:8010/api/v1/health`, **OK**;
- Web Tailscale: `http://100.121.163.126:3000/login`, **OK**.

George confirmó resultado **OK** desde su dispositivo real por Tailscale:

- [x] abrir `http://100.121.163.126:3000/login`;
- [x] iniciar sesión con la cuenta de rol `admin_auditor`;
- [x] cargar el dashboard y sus 33 destinos;
- [x] abrir reportes y comprobar una exportación, si aplica.

Las pruebas reales se suman a las comprobaciones desde `KERNELOS-PC`.

## PC servidor y energía

El equipo actual se identifica como `KERNELOS-PC`. Docker está disponible y los
tres servicios productivos están activos. El plan de energía activo es
`Ultimate Performance`; conectado a corriente, `Sleep after` y
`Hibernate after` están en `Nunca`.

Recomendaciones obligatorias para el piloto:

1. Mantener KERNELOS-PC conectada a corriente y encendida durante todo el
   horario acordado.
2. Mantener la sesión necesaria y Docker Desktop abiertos antes de la hora de
   operación y del backup.
3. No suspender, hibernar, reiniciar ni apagar el equipo durante una jornada sin
   un punto de corte y aviso a los participantes.
4. Comprobar el health al inicio del Día 0 y de cada jornada.
5. Mantener el método actual listo si Windows, Docker, LAN o Tailscale fallan.

George confirmó por escrito que `KERNELOS-PC` será el servidor local del piloto,
permanecerá encendido durante el horario de uso, Docker Desktop estará
disponible y Windows no debe suspenderse. Falta registrar la persona responsable
de revisión y el control de energía.

## Docker y salud

La ejecución actual de `prod-local-health.ps1` terminó:

- `db`: activo y `healthy`;
- `api`: activo y `healthy`;
- `web`: activo y `healthy`;
- API localhost: **OK**;
- API LAN: **OK**;
- Web LAN: **OK**;
- API Tailscale: **OK**;
- Web Tailscale: **OK**;
- Alembic: `0026_user_roles`;
- PostgreSQL `5432`: no publicado;
- `.env.production.local`: no versionado e ignorado por Git;
- resultado general: **OK, 0 fallos críticos y 0 advertencias**.

## DHCP

La reserva DHCP continúa pendiente por falta de credenciales del router.

Si la dirección `192.168.100.220` cambia, se deberá detener el acceso LAN hasta
actualizar y volver a comprobar, según corresponda:

- `.env.production.local`;
- reglas de Windows Firewall;
- scripts o accesos directos que dependan de la dirección;
- documentación y enlaces entregados a la oficina;
- Web, API, CORS y acceso LAN desde el dispositivo real.

`Riesgo DHCP aceptado temporalmente por George para piloto controlado`.

La reserva DHCP sigue pendiente. No se reseteó el router, no se abrieron
puertos y no se configuró port forwarding. Si cambia `192.168.100.220`, se
detiene el acceso hasta actualizar y volver a comprobar los componentes
afectados.

## Riesgos aceptados

George aceptó temporalmente el riesgo DHCP para el piloto controlado, con cambio
de IP o pérdida de acceso LAN como criterio de detención.

## Reservas y controles

No quedan bloqueadores para preparar el inicio controlado.

1. La reserva DHCP continúa pendiente con riesgo aceptado temporalmente.
2. George verifica diariamente que la IP siga siendo `192.168.100.220`.
3. Un cambio de IP o pérdida de acceso LAN detiene el uso hasta actualizar y
   verificar configuración, firewall, CORS, URLs y documentación.
4. George concilia al cierre del día después del cuadre de caja.
5. WhatsApp directo a George es el canal de incidencias; las importantes se
   registran también en la plantilla.
6. George revisa cada mañana `LastTaskResult = 0` y un backup reciente válido.
7. El piloto continúa no iniciado hasta el bloque siguiente.

## Checklist Día 0 resumido

| Control | Estado al corte |
| --- | --- |
| Usuarios activos y roles técnicos | Confirmado |
| Titularidad y no compartir cuentas | Confirmado |
| Contraseñas definitivas | Confirmado |
| Backup existente reciente validado | Confirmado |
| Backup diario mediante tarea | Confirmado en el Bloque 59C; revisar el siguiente disparador natural |
| Acceso secretaria / `operator` | Confirmado por George |
| Acceso George / `admin_auditor` | Confirmado por George |
| Permisos por rol | Confirmados por los Bloques 58B a 58D-2 |
| Plan de incidencias | Plantilla y WhatsApp directo a George confirmados |
| Método actual en paralelo | Confirmado; conciliación a cargo de George |
| Servidor y Docker actuales | Confirmados; responsable George |
| DHCP | Riesgo aceptado temporalmente; reserva pendiente |
| Producción definitiva | No corresponde; no se declarará |
| Aprobación de George | Listo para piloto controlado con reserva DHCP |

## Decisión final

- [ ] Listo para piloto.
- [x] **Listo con reservas para piloto controlado.**
- [ ] No listo.

George autoriza dejar el sistema listo con el riesgo DHCP aceptado
temporalmente. El piloto no comienza en 59D; su inicio debe registrarse en el
bloque siguiente.
