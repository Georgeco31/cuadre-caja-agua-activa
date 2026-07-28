# 51 - Usuarios y accesos pre-piloto

## Objetivo

Registrar el Bloque 59D y cerrar, cuando exista evidencia suficiente, los
pendientes humanos y operativos anteriores al piloto: cuentas reales,
contraseñas definitivas, accesos desde dispositivos reales, continuidad del PC
servidor, decisión DHCP, backup automático y confirmaciones del Día 0.

Fecha del corte: **2026-07-28**.

Este bloque no inicia el piloto, no cambia código, migraciones, seeds, permisos,
Docker ni `.env.production.local`, y no ejecuta restauraciones. Tampoco
documenta contraseñas, hashes, tokens o secretos.

## Decisión ejecutiva

**LISTO PARA PILOTO CONTROLADO, CON RESERVA DHCP ACEPTADA.**

Las dos cuentas reales están activas con los roles esperados, la producción
local está saludable y la tarea automática de backup continúa con resultado
`0`. George confirmó las pruebas reales por LAN y Tailscale, el servidor,
Docker, el método manual paralelo y la aceptación temporal del riesgo DHCP.
Las credenciales definitivas fueron rotadas mediante entrada local oculta.

George confirmó las cuentas personales no compartidas, la prohibición de usar
`admin` para operación diaria, la entrega privada y prueba posterior de cada
credencial, y los responsables de servidor, conciliación, incidencias y backup.

La clasificación operativa es **LISTO CON RESERVAS** por la reserva DHCP
pendiente y sus controles aceptados. El piloto continúa **NO INICIADO** y el
Día 1 solo comienza en el bloque siguiente.

## Evidencia técnica del corte

| Control | Resultado |
| --- | --- |
| Estado Git inicial | Limpio; `git status --short` sin salida |
| Consistencia Git inicial | `git diff --check`, OK |
| Compose | Configuración válida |
| `db` | Activo y `healthy` |
| `api` | Activo y `healthy` |
| `web` | Activo y `healthy` |
| API localhost | OK |
| API LAN | OK en `192.168.100.220:8010` |
| Web LAN | OK en `192.168.100.220:3000/login` |
| API Tailscale | OK en `100.121.163.126:8010` |
| Web Tailscale | OK en `100.121.163.126:3000/login` |
| Alembic | `0026_user_roles` |
| PostgreSQL | Puerto `5432` no publicado |
| Archivo de entorno | `.env.production.local` ignorado y no versionado |
| Resultado general del health | OK; cero fallos críticos y cero advertencias |

El health posterior a la rotación volvió a terminar con cero fallos críticos y
cero advertencias.

## Usuarios reales confirmados

La consulta se limitó a `username`, `role`, `is_active` y `created_at`. No se
consultó ni imprimió `password_hash`.

| Usuario | Rol | Activo | Creado |
| --- | --- | --- | --- |
| `admin` | `admin_auditor` | Sí | 2026-07-27 10:42:41, hora local |
| `estherdelgado31` | `operator` | Sí | 2026-07-27 11:28:11, hora local |

Uso esperado:

- `admin`: George; administración, auditoría, reportes y exportaciones;
- `estherdelgado31`: oficina/secretaría; operación diaria.

Reglas confirmadas:

- [x] Cada cuenta pertenece a una sola persona y no se comparte.
- [x] La operadora usa exclusivamente `estherdelgado31`.
- [x] La operadora no conoce ni usa la credencial de `admin`.
- [x] George reserva `admin` para administración, auditoría y control.
- [x] La cuenta administrativa no se usa para la operación diaria.
- [x] Nadie presta su sesión para evitar una restricción de permisos.

## Contraseñas definitivas

- contraseña admin rotada correctamente;
- contraseña estherdelgado31 rotada correctamente.

## Prueba LAN real de `operator`

Estado: **OK después de la rotación, confirmado por George el 2026-07-28**.

La prueba se realizó desde el dispositivo real de oficina en:

`http://192.168.100.220:3000/login`

| Control | Resultado |
| --- | --- |
| Dispositivo real de oficina | Confirmado |
| Pantalla de login carga | OK |
| Login con `estherdelgado31` | OK |
| Dashboard `operator` carga | OK |
| Se muestran 22 destinos operativos | OK |
| No aparecen Reportes/Gerencia/Exportaciones/Usuarios/Precios/Nómina | OK |
| Se abre una pantalla permitida | OK |
| Resultado final | OK |

Pantallas válidas para la comprobación: caja, clientes, ventas, cobros,
producción o inventario `entry`/`exit`. La evidencia no puede contener
contraseñas, tokens ni datos innecesarios.

## Prueba Tailscale real de `admin_auditor`

Estado: **OK después de la rotación, confirmado por George el 2026-07-28**.

La prueba se realizó desde el dispositivo real de George, con Tailscale activo,
en:

`http://100.121.163.126:3000/login`

| Control | Resultado |
| --- | --- |
| Dispositivo real de George | Confirmado |
| Tailscale activo en el dispositivo | OK |
| Pantalla de login carga | OK |
| Login con `admin` | OK |
| Dashboard `admin_auditor` carga | OK |
| Se muestran 33 destinos | OK |
| Reportes/Gerencia abre | OK |
| Exportación Excel/PDF responde, si se prueba | OK |
| Resultado final | OK |

Las pruebas reales se suman a las pruebas integrales anteriores de la política
de 22/33 destinos y permisos por rol.

## PC servidor y Docker

| Control | Estado |
| --- | --- |
| Nombre del PC | Confirmado: `KERNELOS-PC` |
| Docker accesible para el usuario actual de Windows | Confirmado |
| `db`, `api` y `web` saludables | Confirmado |
| Espacio disponible en la unidad del servidor | 84,26 GB; suficiente para el corte |
| Suspensión con corriente alterna | Configurada en `Nunca` |
| Suspensión con batería | 15 minutos; no usar esta condición durante la operación |
| PC designado formalmente como servidor del piloto | Confirmado por George |
| Permanecerá encendido durante el horario de uso | Confirmado por George |
| Responsable de encendido y revisión | George |
| Continuidad durante el horario de operación | Confirmada por George |
| Docker disponible durante toda la jornada y a las 23:30 | Confirmado por George |
| Windows no debe suspenderse | Confirmado por George |
| Prohibición de `docker compose down -v` | Confirmada por George |

Reglas obligatorias:

1. Mantener `KERNELOS-PC` encendido y conectado a corriente durante el horario
   acordado.
2. Mantener Docker Desktop abierto o disponible.
3. No permitir suspensión durante la operación.
4. No apagar o reiniciar sin confirmar el punto de corte operativo.
5. Después de un reinicio, ejecutar `prod-local-health.ps1`.
6. No usar `docker compose down -v` ni borrar volúmenes.

## DHCP

IP LAN actual: `192.168.100.220`.

La reserva DHCP continúa pendiente porque no están disponibles las credenciales
del router. En este bloque no se cambió ni reinició el router, no se abrieron
puertos y no se configuró port forwarding.

Decisión registrada por George:

- [ ] **Opción A — DHCP bloquea piloto.** No comenzar hasta reservar la IP en el
  router o confirmar una IP fija confiable.
- [x] **Opción B — Riesgo aceptado temporalmente.**
  `Riesgo DHCP aceptado temporalmente por George para piloto controlado`.

Si se acepta temporalmente el riesgo, debe comprobarse la IP cada día antes de
operar. Si cambia, se detiene el acceso hasta revisar de forma controlada
`.env.production.local`, CORS, URL pública de API, firewall, documentación y
URLs entregadas. Este documento no autoriza esos cambios.

Estado actual: **riesgo aceptado temporalmente; la reserva DHCP continúa
pendiente**.

## Backup automático

Comprobación del 2026-07-28:

| Dato | Resultado |
| --- | --- |
| Tarea | `AguaActivaERP-BackupDiario` |
| Existe | Sí |
| Estado | `Ready` |
| Última ejecución | 2026-07-28 06:41:41 |
| `LastTaskResult` | `0` |
| Próxima ejecución | 2026-07-28 23:30:30 |
| Último backup de la tarea | `agua-activa-postgres-20260728-064137.dump` |
| `.sha256` | Presente |
| `.json` | Presente |
| Validación previa independiente | Checksum, JSON y `pg_restore --list`, OK |

La siguiente ejecución natural de las 23:30 queda como control rutinario. Si el
resultado vuelve a ser distinto de `0`, pasa a ser bloqueador y no se autoriza
el piloto hasta diagnosticarlo.

No se ejecutó restore, no se borraron backups y no se añadió ningún backup o
log a Git.

## Método paralelo e incidencias

- La plantilla
  [`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md)
  existe y está lista para completar.
- [x] George confirma que el método actual se mantendrá en paralelo durante
  todo el piloto.
- [x] Responsable de conciliación diaria: George.
- [x] Revisión: al cierre del día, después del cuadre de caja.
- [x] La conciliación revisa caja, ventas, cobros, gastos,
  producción/inventario si aplica e incidencias del día.
- [x] Canal de incidencias: WhatsApp directo a George.
- [x] Toda incidencia importante también se registra en la plantilla.
- [x] El ERP todavía no reemplaza oficialmente el método actual.

Responsable de revisar el backup diario: George, cada mañana antes de iniciar
operación. Debe comprobar `LastTaskResult = 0` y la existencia de un backup
reciente válido.

## Reservas y controles posteriores

1. La reserva DHCP continúa pendiente.
2. Antes de cada jornada se confirma que la IP LAN sigue siendo
   `192.168.100.220`.
3. Si cambia la IP, se detiene el acceso hasta actualizar y verificar
   configuración, firewall, CORS, URLs y documentación.
4. George revisa cada mañana el backup y `LastTaskResult`.
5. La ejecución natural de las 23:30 continúa como control rutinario.
6. El bloque siguiente debe registrar el inicio efectivo del Día 1; 59D no lo
   inicia.

## Decisión final

- [ ] Listo para piloto.
- [x] **Listo con reservas para piloto controlado.**
- [ ] No listo.

George autoriza dejar el sistema listo para el piloto controlado con el riesgo
DHCP aceptado temporalmente. Esta decisión no inicia el Día 1.
