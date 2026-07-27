# 30 - Backup diario programado en Windows

## Objetivo

El Bloque 56C activa y verifica operativamente el backup diario de PostgreSQL de
Agua Activa ERP en KERNELOS-PC. La tarea usa el script seguro implementado en el
Bloque 56A y se valida mediante un inicio manual controlado desde el Programador
de tareas de Windows.

Este bloque no restaura sobre producción, no borra backups ni volúmenes y no
modifica `.env.production.local`, frontend, backend, migraciones o seeds.

## Datos de la activación

| Dato | Valor |
| --- | --- |
| Fecha | 27 de julio de 2026 |
| PC | `KERNELOS-PC` |
| Tarea | `AguaActivaERP-BackupDiario` |
| Ruta de tarea | `\` |
| Hora configurada | 23:30, disparador diario |
| Script | `C:\Users\Administrator\Desktop\cuadre-caja-agua-activa\scripts\prod-local-backup-db.ps1` |
| Ejecutable | `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` |
| Argumentos | `-NoProfile -ExecutionPolicy Bypass -File "<ruta-absoluta-del-script>"` |
| Usuario | `KERNELOS-PC\Administrator`, inicio interactivo |
| Nivel | Limitado |

La tarea no guarda contraseñas. Docker Desktop debe estar iniciado y disponible
para el mismo usuario. Si la PC está apagada o no existe una sesión activa a la
hora programada, el backup no se ejecutará.

## Registro y consulta

La consulta inicial devolvió `Estado: no existe`. El registro se realizó con:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-register-task.ps1 -Time "23:30"
```

Resultado:

```text
Tarea registrada: AguaActivaERP-BackupDiario
```

La inspección posterior confirmó:

- estado `Ready`;
- acción con `powershell.exe` y la ruta absoluta correcta;
- `StartBoundary` en `2026-07-27T23:30:00-05:00`;
- usuario interactivo y nivel limitado;
- ausencia de contraseñas almacenadas.

`Get-ScheduledTaskInfo` mostró la próxima ejecución como `2026-07-27 23:30:30`;
el disparador configurado permanece exactamente a las 23:30.

Consultar en cualquier momento:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-check-task.ps1
```

## Ejecución manual controlada

La prueba se inició sin cambiar el disparador diario:

```powershell
Start-ScheduledTask -TaskName "AguaActivaERP-BackupDiario"
```

El Programador de tareas registró:

| Verificación | Resultado |
| --- | --- |
| Inicio manual | 27 de julio de 2026, 14:02:02 |
| Estado final | `Ready` |
| Último resultado | `0`, éxito |
| Backup nuevo | `agua-activa-postgres-20260727-140219.dump` |
| Tamaño | 281631 bytes |

La prueba creó, sin reemplazar ni borrar backups anteriores:

```text
agua-activa-postgres-20260727-140219.dump
agua-activa-postgres-20260727-140219.dump.sha256
agua-activa-postgres-20260727-140219.dump.json
```

## Validación del backup nuevo

Se comprobó:

- `.dump` presente y con tamaño mayor que cero;
- `.sha256` presente;
- `.json` presente;
- SHA256 calculado igual al archivo `.sha256` y a la metadata;
- metadata limitada a los campos seguros previstos, sin secretos ni datos de
  negocio;
- metadata con `validation_status = "OK: pg_restore --list"`;
- `pg_restore --list` repetido de forma independiente y aprobado;
- Alembic registrado como `0026_user_roles`;
- `prod-local-backup-list.ps1` muestra los tres componentes.

La validación independiente solo copió el dump a una ruta temporal de `db`,
ejecutó `pg_restore --list` y retiró ese temporal. No creó una base, no ejecutó
restore y no modificó producción.

## Git y protección de archivos locales

Git confirmó que:

- `backups/` está ignorado por `.gitignore`;
- el nuevo `.dump`, `.sha256` y `.json` no aparecen en `git status`;
- `.env.production.local` está ignorado y no está versionado;
- no se añadieron backups ni evidencias al staging.

Los tres archivos del backup deben conservarse juntos. No deben subirse a Git ni
adjuntarse a tickets o documentación.

## Salud de producción después de la prueba

`prod-local-health.ps1` terminó con cero fallos críticos y cero advertencias:

| Control | Resultado |
| --- | --- |
| `docker compose config --quiet` | OK |
| `db` | `running`, `healthy` |
| `api` | `running`, `healthy` |
| `web` | `running`, `healthy` |
| API LAN | OK |
| Web LAN | OK |
| API Tailscale | OK |
| Web Tailscale | OK |
| Alembic | `0026_user_roles` |
| PostgreSQL 5432 | interno del contenedor, sin publicación al host |
| `.env.production.local` | ignorado y no versionado |

La prueba no apagó contenedores, no borró volúmenes y no cambió la base
productiva.

## Verificación operativa periódica

1. Mantener KERNELOS-PC encendida, con sesión del usuario de la tarea y Docker
   Desktop disponibles antes de las 23:30.
2. Consultar periódicamente:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-check-task.ps1
   ```

3. Confirmar que `Último resultado` sea `0` y revisar la fecha de última
   ejecución.
4. Confirmar la creación del backup más reciente:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-list.ps1
   ```

5. Si el resultado no es `0` o no aparece un nuevo juego de tres archivos, no
   borrar backups ni restaurar sobre producción. Verificar sesión de Windows,
   Docker Desktop, espacio disponible y salud del ERP, y registrar el incidente
   sin secretos.

## Fuera de alcance

- Restauración automática o sobre producción.
- Borrado automático de backups antiguos.
- Backup automático a nube o USB.
- Cifrado avanzado.
- Notificaciones por email.
- Inicio del piloto.

## Pendientes

- Copiar backups periódicamente a disco externo.
- Rotar contraseñas definitivas antes del piloto.
- Configurar reserva DHCP antes del piloto.
- Ejecutar pruebas integrales finales.
- Iniciar el piloto paralelo únicamente después de autorización explícita.
