# 50 - Diagnóstico del backup diario desatendido

## Objetivo

El Bloque 59C diagnostica y corrige el resultado `1` de la tarea de Windows
`AguaActivaERP-BackupDiario`. El alcance se limita al backup, su tarea
programada, observabilidad segura y validaciones operativas. No inicia el
piloto, no restaura datos y no modifica frontend, backend, migraciones, seeds,
permisos ni `.env.production.local`.

Fecha del diagnóstico: **2026-07-28**.

## Problema detectado en el Bloque 59B

La tarea estaba registrada y `Ready`, pero su ejecución del
2026-07-27 23:30:30 terminó con `LastTaskResult = 1`. No creó un juego de backup
a esa hora. El script anterior no escribía un log por ejecución y el canal
`Microsoft-Windows-TaskScheduler/Operational` estaba deshabilitado, por lo que
el error textual de PowerShell no quedó conservado.

La consulta inicial confirmó:

| Dato | Estado inicial |
| --- | --- |
| Ejecutable | Correcto, PowerShell de Windows |
| Argumentos | Correctos, `-NoProfile -ExecutionPolicy Bypass -File` y ruta absoluta |
| Directorio de inicio | No configurado |
| Usuario | Cuenta local `Administrator` |
| Inicio | Interactivo |
| Nivel | Limitado |
| Disparador | Diario a las 23:30 |
| Iniciar cuando esté disponible | No |
| Reintentos | Ninguno |
| Último resultado | `1` |

El script ya resolvía la raíz mediante `$PSScriptRoot` y hacía
`Push-Location` al repositorio, por lo que el directorio ausente no explica por
sí solo el fallo, aunque sí era una carencia de configuración.

## Causa encontrada

Los logs locales de Docker Desktop permiten correlacionar el fallo sin mostrar
su contenido:

- a las 23:28:06, hora local, Docker registró eventos de apagado del backend;
- a las 23:30:01 registró un error que menciona conexión e indisponibilidad del
  motor Docker;
- la tarea comenzó a las 23:30:30 y terminó con código `1`;
- no existe un dump de esa ejecución.

La causa operacional del código `1` fue que el motor Docker no estaba disponible
para el backup al momento del disparador. La falta de log propio y de reintentos
hizo que el fallo transitorio terminara sin evidencia diagnóstica útil ni una
nueva oportunidad automática.

## Corrección aplicada

### Script de backup

`scripts/prod-local-backup-db.ps1` ahora crea un log por ejecución en:

```text
backups/logs/backup-task-YYYYMMDD-HHMMSS.log
```

El log registra únicamente:

- fecha y hora;
- ruta del repositorio;
- disponibilidad de Docker y Compose;
- estado seguro de los servicios;
- nombre del backup;
- pasos `pg_dump`, copia y creación de artefactos;
- resultado de `pg_restore --list`;
- error textual controlado si falla.

El logger normaliza saltos de línea y redacta asignaciones de
`POSTGRES_PASSWORD`, `AUTH_SECRET_KEY`, `ADMIN_PASSWORD` y credenciales
embebidas en una URL PostgreSQL. No imprime ni copia el contenido de
`.env.production.local`.

### Tarea programada

La tarea existente fue actualizada sin cambiar su usuario, nivel, disparador ni
hora:

| Dato | Configuración final |
| --- | --- |
| Tarea | `AguaActivaERP-BackupDiario` |
| Estado | `Ready` |
| Ejecutable | `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` |
| Argumentos | `-NoProfile -ExecutionPolicy Bypass -File "<ruta-absoluta-del-script>"` |
| Directorio de inicio | Raíz absoluta del repositorio |
| Usuario | Cuenta local `Administrator` |
| Inicio | Interactivo |
| Nivel | Limitado |
| Disparador | Diario a las 23:30 |
| Iniciar cuando esté disponible | Sí |
| Reintentos | 3 |
| Intervalo de reintento | 5 minutos |
| Instancias simultáneas | Ignorar una nueva |
| Límite de ejecución | 2 horas |
| Batería | Puede iniciar y continuar |

`scripts/prod-local-backup-register-task.ps1` conserva esa misma configuración
para registros futuros.

### Comprobador de tarea

`scripts/prod-local-backup-check-task.ps1` ya no convierte silenciosamente un
`Access denied` en `Estado: no existe`. Si Windows niega la consulta, el script
termina con un error explícito que pide permisos suficientes.

## Prueba manual del script

La ejecución manual controlada terminó correctamente:

```text
agua-activa-postgres-20260728-064021.dump
agua-activa-postgres-20260728-064021.dump.sha256
agua-activa-postgres-20260728-064021.dump.json
```

Resultado:

| Control | Resultado |
| --- | --- |
| Tamaño del dump | 281631 bytes |
| SHA256 lateral | Coincide |
| SHA256 en metadata | Coincide |
| JSON | Válido |
| Alembic en metadata | `0026_user_roles` |
| `pg_restore --list` | OK |
| Log | `backup-task-20260728-064020.log`, OK |
| Asignaciones sensibles sin redactar en log | No detectadas |

## Prueba manual de la tarea programada

La prueba se inició con `Start-ScheduledTask`, de modo que Windows ejecutó la
acción, el principal, el directorio de inicio y las condiciones reales de la
tarea. El resultado final fue:

| Control | Resultado |
| --- | --- |
| Estado final | `Ready` |
| `LastRunTime` | 2026-07-28 06:41:41 |
| `LastTaskResult` | `0` |
| Próxima ejecución | 2026-07-28 23:30:30 |
| Backup creado por la tarea | `agua-activa-postgres-20260728-064137.dump` |
| Tamaño | 281631 bytes |
| `.sha256` | Presente y coincide |
| `.json` | Presente, válido y coincide |
| Metadata `validation_status` | `OK: pg_restore --list` |
| Log | `backup-task-20260728-064137.log`, OK |

El dump generado por la tarea también aprobó una segunda ejecución independiente
de `pg_restore --list`. Solo se copió temporalmente al contenedor `db`; no se
creó una base ni se ejecutó restore.

La ejecución manual del script y la ejecución manual de la tarea crearon
backups distintos y no reemplazaron respaldos existentes.

## Salud posterior

`scripts/prod-local-health.ps1` terminó con cero fallos críticos y cero
advertencias:

| Control | Resultado |
| --- | --- |
| Compose | Válido |
| `db` | `running`, `healthy` |
| `api` | `running`, `healthy` |
| `web` | `running`, `healthy` |
| API localhost | OK |
| API LAN | OK |
| Web LAN | OK |
| API Tailscale | OK |
| Web Tailscale | OK |
| Alembic | `0026_user_roles` |
| PostgreSQL 5432 | No publicado |
| `.env.production.local` | Ignorado y no versionado |

## Git y seguridad

- `backups/` continúa ignorado por `.gitignore`;
- el `.dump`, `.sha256`, `.json` y los logs no aparecen en `git status`;
- no se añadió nada al staging;
- no se mostró ni modificó `.env.production.local`;
- no se ejecutó restore;
- no se borraron backups ni datos;
- no se hizo `git add`, commit o push.

## Limitaciones operativas

- La PC debe estar encendida.
- Docker Desktop debe estar disponible para el usuario de la tarea.
- Si Windows está suspendido, la tarea no se ejecuta mientras dure la
  suspensión.
- Si Docker no inicia o permanece indisponible después de los tres reintentos,
  el backup puede fallar.
- La prueba del Bloque 59C usó `Start-ScheduledTask`; la siguiente ejecución por
  el disparador natural de las 23:30 debe revisarse como control operativo.
- Un backup en el mismo disco no sustituye una copia externa.

## Estado final

**Bloqueador técnico del código `1`: resuelto.**

La tarea corregida termina con `LastTaskResult = 0`, genera `.dump`, `.sha256`,
`.json` y log, y el backup aprueba `pg_restore --list`. El piloto permanece
**NO INICIADO** y Agua Activa ERP continúa **NO LISTO** por los demás
bloqueadores pre-piloto: credenciales definitivas, cuentas personales,
dispositivos reales, continuidad del servidor, DHCP y cierre del Día 0.
