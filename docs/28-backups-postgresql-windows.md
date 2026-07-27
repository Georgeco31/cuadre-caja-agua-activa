# 28 - Backups PostgreSQL en Windows

## Objetivo

El Bloque 56A incorpora un procedimiento seguro para crear backups manuales de
la base PostgreSQL de Agua Activa ERP en KERNELOS-PC y deja preparada, sin
registrarla automáticamente, una tarea diaria de Windows.

Un backup comprobado es obligatorio antes del piloto porque un error operativo,
una actualización fallida o una avería pueden dejar la información del ERP
inutilizable. Este bloque reduce el riesgo de pérdida, pero no demuestra aún que
el sistema pueda recuperarse: la restauración controlada corresponde al Bloque
56B.

## Alcance

Se respalda:

- la base de datos PostgreSQL usada por el ERP;
- en formato custom de PostgreSQL (`pg_dump -Fc`);
- con nombre fechado, hash SHA256 y metadata segura.

No se respalda en este bloque:

- archivos externos que el ERP pueda incorporar en el futuro;
- `.env.production.local` ni otro archivo con secretos;
- imágenes Docker, código fuente o configuración del sistema operativo.

Tampoco se implementan restauración, retención o eliminación automática,
cifrado avanzado, copia automática a USB/nube ni notificaciones.

## Carpeta y archivos

Los backups se guardan en:

```text
backups/postgres
```

`backups/` y los archivos `*.dump` están ignorados por Git. Cada ejecución
correcta genera tres archivos relacionados:

```text
agua-activa-postgres-YYYYMMDD-HHMMSS.dump
agua-activa-postgres-YYYYMMDD-HHMMSS.dump.sha256
agua-activa-postgres-YYYYMMDD-HHMMSS.dump.json
```

El `.dump` contiene la base. El `.sha256` permite comprobar integridad. El
`.json` contiene fecha, PC, ruta del repositorio, nombre y tamaño del backup,
SHA256, revisión Alembic, commit Git, estado resumido de servicios y resultado
de `pg_restore --list`.

La metadata no incluye contraseñas, tokens, contenido del archivo de entorno ni
datos de negocio en texto plano.

## Crear un backup manual

Requisitos:

- Windows PowerShell 5.1 o posterior;
- Docker Desktop iniciado;
- Docker Compose v2 disponible;
- `docker-compose.prod.yml` y `.env.production.local` presentes;
- servicio `db` corriendo.

Desde la raíz del repositorio:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-db.ps1
```

El script:

1. valida archivos, Docker, Compose y el servicio `db`;
2. comprueba con Git que el destino está ignorado;
3. genera el dump dentro de `db` en una ruta temporal `/tmp`;
4. copia el archivo con `docker compose cp`, sin redirigir binario desde
   PowerShell;
5. exige tamaño mayor que cero y valida `pg_restore --list`;
6. calcula SHA256 y escribe metadata sin secretos;
7. elimina únicamente el temporal creado dentro del contenedor.

No apaga contenedores, no restaura, no modifica tablas, no borra backups
anteriores y no elimina volúmenes.

Al terminar debe mostrar la ruta, el tamaño, el hash y:

```text
Validacion: OK: pg_restore --list
```

La validación de formato no sustituye una restauración. El backup todavía debe
probarse en el Bloque 56B.

## Listar backups

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-list.ps1
```

La lista se ordena del más reciente al más antiguo y muestra fecha, nombre,
tamaño y presencia de los archivos SHA256 y JSON. Es una operación de solo
lectura.

## Preparar la tarea diaria

El script de registro usa por defecto:

```text
Nombre: AguaActivaERP-BackupDiario
Hora: 23:30
```

Revisar el plan sin registrar nada:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-register-task.ps1 -WhatIf
```

Registrar la tarea únicamente después de la aprobación de George:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-register-task.ps1
```

Elegir otro nombre u hora:

```powershell
.\scripts\prod-local-backup-register-task.ps1 `
  -TaskName "AguaActivaERP-BackupDiario" `
  -Time "22:45"
```

La acción registrada ejecuta:

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<repo>\scripts\prod-local-backup-db.ps1"
```

La tarea usa el usuario actual con inicio de sesión interactivo y no guarda
contraseñas. Docker Desktop debe estar iniciado y accesible para ese usuario.
Si la PC está apagada o el usuario no mantiene una sesión activa a la hora
programada, el backup no se ejecutará. El script explica errores de permisos o
dependencias de la sesión sin solicitar secretos.

Crear el archivo del script no registra ni ejecuta la tarea. Durante el Bloque
56A solo se valida el modo `-WhatIf`; la activación real queda bajo aprobación
manual.

## Consultar la tarea

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-check-task.ps1
```

El resultado indica si existe, estado, próxima ejecución, última ejecución y
último resultado. El valor `0` como último resultado significa éxito. Este
script no modifica nada.

## Quitar la tarea

Con confirmación interactiva:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-unregister-task.ps1
```

En una operación ya aprobada, `-Force` evita la pregunta:

```powershell
.\scripts\prod-local-backup-unregister-task.ps1 -Force
```

También admite `-WhatIf`. Quitar la tarea no borra backups, no toca PostgreSQL
y no cambia Docker.

## Copia externa

Un backup guardado únicamente en el mismo disco de KERNELOS-PC no protege ante
daño físico del disco, robo, ransomware o pérdida total del equipo. Copiar
periódicamente los backups importantes a un disco externo desconectado o a una
ubicación segura aprobada.

La copia debe conservar juntos `.dump`, `.sha256` y `.json`. El medio externo no
debe permanecer conectado permanentemente. La política de retención y el
cifrado avanzado siguen pendientes.

## Qué no hacer

- No subir backups a GitHub ni a ningún repositorio.
- No compartir `.env.production.local`.
- No mostrar contraseñas, tokens o contenido del archivo de entorno.
- No usar `docker compose down -v`.
- No usar `docker volume prune` ni `docker system prune`.
- No borrar el volumen de PostgreSQL.
- No restaurar sobre producción.
- No considerar `pg_restore --list` como prueba suficiente de recuperación.

## Estado del Bloque 56A

- Backup manual: implementado y comprobado.
- Preparación de backup automático: implementada mediante scripts de registro,
  consulta y desregistro; la tarea real no se registra sin aprobación.
- Restauración demostrada: pendiente para el Bloque 56B.
- Piloto: pendiente.

## Evidencia de la prueba en KERNELOS-PC

El 27 de julio de 2026 se ejecutó el backup manual y se repitió después del
ajuste final de limpieza del temporal, sin borrar el backup anterior:

- el backup final de prueba fue
  `agua-activa-postgres-20260727-133213.dump`, con 281631 bytes;
- se crearon los archivos `.sha256` y `.json`;
- el hash del dump coincidió con el archivo SHA256 y la metadata;
- la metadata registró Alembic `0026_user_roles` y solo los campos seguros
  previstos;
- `pg_restore --list` aprobó;
- Git confirmó que el dump está ignorado;
- `prod-local-backup-list.ps1` mostró los tres componentes;
- `prod-local-backup-check-task.ps1` confirmó que la tarea no existe;
- el registro con `-WhatIf` aprobó sin crear ninguna tarea;
- `prod-local-health.ps1` aprobó sin fallos ni advertencias;
- `db`, `api` y `web` continuaron healthy;
- Docker Compose siguió válido y PostgreSQL conservó bindings `{}`, sin publicar
  5432.

No se ejecutó restauración, no se modificó la base, no se apagaron contenedores,
no se borraron volúmenes y no se registró la tarea diaria.
