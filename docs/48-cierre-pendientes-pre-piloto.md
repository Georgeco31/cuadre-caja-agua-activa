# 48 - Cierre de pendientes pre-piloto

## Objetivo

Registrar el corte operativo del Bloque 59B y decidir si Agua Activa ERP puede
iniciar el piloto interno paralelo. Este bloque verifica usuarios, respaldos,
servidor, Docker, red y condiciones del Día 0 sin iniciar el piloto, cambiar
credenciales, modificar datos ni ejecutar una restauración.

Fecha del corte: **2026-07-28**.

## Decisión ejecutiva

**NO LISTO para iniciar el piloto.**

La infraestructura productiva local está saludable y las cuentas requeridas
existen activas con los roles correctos. Sin embargo, la última ejecución
desatendida de la tarea diaria terminó con código `1`, no existe confirmación de
rotación de las contraseñas definitivas, faltan las pruebas actuales desde los
dispositivos reales y George todavía debe confirmar las reglas de cuentas,
servidor, método paralelo y DHCP.

El piloto no fue iniciado. La decisión debe revisarse después de cerrar todos
los bloqueadores de este documento y completar
[`49-checklist-dia-0-piloto.md`](49-checklist-dia-0-piloto.md).

## Escala de estados

| Estado | Significado |
| --- | --- |
| Confirmado | Existe evidencia actual suficiente para cerrar el punto técnico |
| Parcial | Existe evidencia técnica, pero falta una confirmación humana o prueba en el dispositivo requerido |
| Bloqueador | Impide autorizar el Día 1 |
| No ejecutado | La acción requería autorización explícita o estaba fuera del alcance |

## Resultado de pendientes

| Pendiente | Estado | Evidencia o acción requerida |
| --- | --- | --- |
| Cuentas requeridas activas y con rol correcto | Confirmado | La base contiene `admin` activo con rol `admin_auditor` y `estherdelgado31` activa con rol `operator` |
| Cuentas individuales, sin uso compartido | Bloqueador | George y la operadora deben confirmar titularidad, no préstamo y uso exclusivo de cada cuenta |
| Operadora no usa la cuenta administrativa | Bloqueador | Requiere confirmación y prueba desde el puesto real |
| George reconoce cuál cuenta corresponde a cada rol | Bloqueador | Requiere confirmación expresa en el Día 0 |
| Contraseñas definitivas fuertes y vigentes | Bloqueador | No se rotaron ni se recibió confirmación segura durante este bloque |
| Tarea diaria registrada | Confirmado | `AguaActivaERP-BackupDiario` existe, está `Ready` y conserva su disparador diario |
| Última ejecución desatendida exitosa | Bloqueador | La ejecución de 2026-07-27 23:30:30 terminó con resultado `1`; se requiere una ejecución por disparador con resultado `0` |
| Backup existente reciente y legible | Confirmado | El juego más reciente del 2026-07-28 05:15 tiene dump, checksum y metadata; el hash coincide, el JSON es válido y `pg_restore --list` aprobó |
| Backup manual nuevo del Bloque 59B | No ejecutado | No hubo autorización explícita de George; se validó el backup existente sin crear otro |
| Endpoint LAN disponible | Confirmado | API y Web responden desde KERNELOS-PC en `192.168.100.220` |
| Prueba LAN desde el dispositivo de oficina | Bloqueador | Faltan login `operator`, dashboard y una pantalla operativa desde el equipo real |
| Endpoint Tailscale disponible | Confirmado | API y Web responden desde KERNELOS-PC en `100.121.163.126` |
| Prueba Tailscale desde el dispositivo de George | Bloqueador | Faltan login `admin_auditor`, dashboard y reportes/exportaciones desde el dispositivo real |
| KERNELOS-PC identificado como servidor | Parcial | El nombre del equipo coincide y los servicios están activos; George debe confirmar que será el servidor durante el piloto |
| PC disponible durante el horario operativo | Bloqueador | Falta horario, responsable y compromiso de no apagar el equipo |
| Docker Desktop disponible | Parcial | Docker está operativo ahora; falta confirmar su arranque y disponibilidad durante toda la jornada |
| Windows sin suspensión durante el uso | Parcial | Con corriente, suspensión e hibernación están configuradas en `Nunca`; debe mantenerse esa configuración y evitar suspensión manual |
| Docker y servicios saludables | Confirmado | `db`, `api` y `web` están `healthy`; health terminó con cero fallos y cero advertencias |
| PostgreSQL protegido | Confirmado | El puerto `5432` no está publicado |
| Migración vigente | Confirmado | Alembic está en `0026_user_roles` |
| Compose productivo válido | Confirmado | `docker compose ... config --quiet` terminó correctamente |
| Reserva DHCP | Bloqueador | Continúa pendiente por falta de credenciales del router; no existe aceptación temporal registrada |
| Checklist Día 0 | Bloqueador | La plantilla está creada, pero todavía no está completada ni confirmada por George |
| Piloto interno | No ejecutado | No se inició ninguna jornada ni se registró operación de piloto |

## Usuarios y contraseñas

La consulta se limitó a nombre de usuario, rol y estado activo. No se consultaron,
mostraron ni documentaron contraseñas o hashes.

| Usuario | Rol | Estado técnico | Confirmación humana pendiente |
| --- | --- | --- | --- |
| `admin` | `admin_auditor` | Activo | George confirma que es su cuenta personal y que solo él la usará |
| `estherdelgado31` | `operator` | Activa | La operadora confirma que es su cuenta personal y que no usará `admin` |

No es posible demostrar que una contraseña sea conocida solo por su titular a
partir del hash almacenado. Como no hubo autorización explícita para rotarla, el
estado de ambas contraseñas queda como **bloqueador**. Cuando George realice la
acción por un canal seguro, la única evidencia documental permitida será
`rotada correctamente`, sin fecha sensible, valor, pista ni captura del secreto.

## Backup diario

La comprobación actual de la tarea devolvió:

| Dato | Resultado |
| --- | --- |
| Tarea | `AguaActivaERP-BackupDiario` |
| Estado | `Ready` |
| Próxima ejecución | 2026-07-28 23:30:30 |
| Última ejecución | 2026-07-27 23:30:30 |
| Último resultado | `1` |
| Acción configurada | Script seguro `prod-local-backup-db.ps1` |
| Tipo de inicio | Usuario interactivo, nivel limitado |

El resultado `1` no cierra la prueba desatendida. No se encontraron eventos
operativos disponibles que permitan afirmar una causa. Antes del piloto debe
revisarse que la sesión de Windows y Docker Desktop estén disponibles, dejar
actuar el siguiente disparador y confirmar resultado `0` y un nuevo juego
`.dump`, `.sha256` y `.json`.

## Backup existente validado

No se creó un backup manual nuevo. El backup existente más reciente fue
comprobado sin restaurarlo:

- fecha local: 2026-07-28 05:15;
- tamaño: 281631 bytes;
- archivo `.dump`: presente;
- archivo `.sha256`: presente y coincide con el dump;
- archivo `.json`: presente y se puede interpretar;
- `pg_restore --list`: **OK**;
- carpeta montada en solo lectura dentro de un contenedor temporal sin red para
  la validación;
- ningún backup se añadió a Git.

Este resultado demuestra que el respaldo existente es legible, pero no
convierte la ejecución desatendida fallida en exitosa.

## Acceso LAN

El health actual confirma:

- API LAN: `http://192.168.100.220:8010/api/v1/health`, **OK**;
- Web LAN: `http://192.168.100.220:3000/login`, **OK**.

Falta la prueba obligatoria desde el dispositivo real de oficina:

- [ ] abrir `http://192.168.100.220:3000/login`;
- [ ] iniciar sesión con la cuenta personal de rol `operator`;
- [ ] cargar el dashboard;
- [ ] abrir una pantalla operativa permitida;
- [ ] confirmar el resultado sin escribir la contraseña en chat o documento.

## Acceso Tailscale

El health actual confirma:

- API Tailscale: `http://100.121.163.126:8010/api/v1/health`, **OK**;
- Web Tailscale: `http://100.121.163.126:3000/login`, **OK**.

Falta la prueba obligatoria desde el dispositivo real de George:

- [ ] abrir `http://100.121.163.126:3000/login`;
- [ ] iniciar sesión con la cuenta personal de rol `admin_auditor`;
- [ ] cargar el dashboard;
- [ ] abrir reportes y comprobar una exportación, si aplica;
- [ ] confirmar el resultado sin escribir la contraseña en chat o documento.

Las comprobaciones hechas desde KERNELOS-PC demuestran disponibilidad de los
endpoints, no sustituyen el recorrido desde los dispositivos reales.

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

George todavía debe confirmar por escrito que KERNELOS-PC será el servidor del
piloto, su horario de disponibilidad y la persona responsable de encendido.

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

No existe confirmación de George para aceptar temporalmente este riesgo. El
estado se mantiene como **bloqueador**. Solo puede cambiar a
`riesgo aceptado temporal` mediante una confirmación explícita de George,
registrando fecha, alcance, control diario de la IP y criterio de detención.

## Riesgos aceptados

**Ninguno registrado en este corte.**

En particular, no se presume aceptado el riesgo DHCP, el fallo del backup diario
ni el uso de evidencia histórica de acceso.

## Bloqueadores restantes

1. Rotar o confirmar por canal seguro las contraseñas definitivas de ambas
   cuentas; documentar únicamente `rotada correctamente`.
2. Confirmar que las cuentas son personales, que no se comparten, que la
   operadora no usará la cuenta administrativa y que George reconoce ambos
   roles.
3. Obtener una ejecución realmente desatendida de
   `AguaActivaERP-BackupDiario` con resultado `0` y validar el nuevo juego de
   archivos.
4. Probar LAN desde el dispositivo real de oficina con `operator`.
5. Probar Tailscale desde el dispositivo real de George con `admin_auditor`.
6. Confirmar KERNELOS-PC como servidor, horario, responsable, Docker Desktop y
   prohibición de suspensión durante la operación.
7. Configurar la reserva DHCP o registrar la aceptación temporal explícita del
   riesgo con sus controles.
8. Confirmar que el método actual estará disponible en paralelo y que la
   plantilla y el canal de incidencias están listos.
9. Completar y firmar el checklist Día 0.
10. Registrar la autorización explícita de George para iniciar el Día 1.

## Checklist Día 0 resumido

| Control | Estado al corte |
| --- | --- |
| Usuarios activos y roles técnicos | Confirmado |
| Titularidad y no compartir cuentas | Bloqueador |
| Contraseñas definitivas | Bloqueador |
| Backup existente reciente validado | Confirmado |
| Backup diario desatendido | Bloqueador |
| Acceso secretaria / `operator` | Bloqueador |
| Acceso George / `admin_auditor` | Bloqueador |
| Permisos por rol | Confirmados por los Bloques 58B a 58D-2 |
| Plan de incidencias | Plantilla disponible; responsable y canal pendientes |
| Método actual en paralelo | Regla documentada; disponibilidad real pendiente |
| Servidor y Docker actuales | Saludables; compromiso operativo pendiente |
| DHCP | Bloqueador sin riesgo aceptado |
| Producción definitiva | No corresponde; no se declarará |
| Aprobación de George | Pendiente |

## Decisión final

- [ ] Listo para piloto.
- [ ] Listo con reservas.
- [x] **No listo.**

Motivo: existen bloqueadores de credenciales, backup desatendido, accesos desde
dispositivos reales, continuidad del servidor y DHCP. La salud técnica actual
no reemplaza esas confirmaciones.

