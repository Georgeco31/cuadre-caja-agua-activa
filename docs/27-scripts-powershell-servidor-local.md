# 27 - Scripts PowerShell del servidor local

## Objetivo

El Bloque 55C permite operar Agua Activa ERP en KERNELOS-PC con Windows
PowerShell, desde cualquier ubicación y sin depender de WSL ni de scripts
`.sh`. Los scripts resuelven la raíz del repositorio, validan los archivos
requeridos y usan siempre:

```text
docker-compose.prod.yml
.env.production.local
```

Ningún script imprime el contenido de `.env.production.local`. El apagado no
elimina volúmenes y el inicio normal no reconstruye imágenes.

## Requisitos

- Windows con PowerShell 5.1 o posterior.
- Docker Desktop iniciado y Docker Compose v2 disponible.
- Repositorio en una ruta estable.
- `docker-compose.prod.yml`.
- `.env.production.local` local, completo, no versionado y nunca compartido.

La ruta actual documentada es:

```text
C:\Users\Administrator\Desktop\cuadre-caja-agua-activa
```

Los scripts pueden ejecutarse desde otra ubicación porque calculan la raíz a
partir de su propia carpeta.

## Scripts disponibles

| Script | Uso | Modifica estado |
| --- | --- | --- |
| `prod-local-start.ps1` | Inicia `db`, `api` y `web` sin reconstruir | Inicia contenedores |
| `prod-local-stop.ps1` | Apaga el Compose sin `-v` | Detiene y retira contenedores; conserva datos |
| `prod-local-health.ps1` | Comprueba Compose, contenedores, API, Web, Alembic, puerto 5432 y Git | No |
| `prod-local-logs.ps1` | Muestra logs recientes de todos o un servicio | No |
| `prod-local-status.ps1` | Muestra `docker compose ps` y las URL | No |
| `prod-local-rebuild.ps1` | Reconstruye imágenes después de una actualización | Reconstruye/recrea contenedores; conserva volúmenes |
| `prod-local-migrate.ps1` | Aplica `alembic upgrade head` de forma explícita | Sí, modifica el esquema |

`prod-local-common.ps1` contiene validaciones compartidas y no se ejecuta
directamente.

Los scripts `.sh` siguen siendo útiles en macOS/Linux. No son requeridos para
operar el ERP desde Windows.

## Iniciar el ERP

Desde la raíz del repositorio:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-start.ps1
```

El inicio usa:

```text
docker compose -f docker-compose.prod.yml --env-file .env.production.local up -d
```

No usa `--build`, no ejecuta migraciones, no ejecuta seeds y no elimina
volúmenes. Al terminar muestra las URL LAN y Tailscale.

## Verificar el ERP

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-health.ps1
```

La salida usa `OK`, `FAIL` o `WARNING` por sección y comprueba:

- `docker compose config --quiet`;
- estado y health de `db`, `api` y `web`;
- API por localhost y LAN;
- API por Tailscale como comprobación informativa;
- Web por LAN;
- Web por Tailscale como comprobación informativa;
- revisión de Alembic mediante `psql` dentro de `db`;
- ausencia de publicación de PostgreSQL 5432 en configuración y estado;
- que `.env.production.local` no esté versionado por Git.

Si Tailscale está apagado, sus comprobaciones muestran `WARNING` y no convierten
por sí solas el resultado general en fallo. LAN, contenedores, PostgreSQL y
Alembic sí son comprobaciones críticas.

## Consultar estado

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-status.ps1
```

Este script solo muestra `docker compose ps`, los servicios principales y las
URL de acceso.

## Ver logs

Los últimos 100 registros de todos los servicios:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-logs.ps1
```

Filtrar por servicio:

```powershell
.\scripts\prod-local-logs.ps1 -Service api
.\scripts\prod-local-logs.ps1 -Service web -Tail 200
.\scripts\prod-local-logs.ps1 -Service db -Tail 50
```

`-Service` acepta `api`, `web`, `db` o `all`. `-Tail` acepta un entero positivo
y su valor predeterminado es 100. El script no lee ni muestra el archivo de
entorno; los propios logs de la aplicación deben revisarse periódicamente para
confirmar que no registran tokens, contraseñas o datos personales completos.

## Apagar sin borrar datos

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-stop.ps1
```

El apagado usa exactamente `down`, sin `-v`. Conserva el volumen
`postgres_prod_data`; no borra imágenes, backups ni `.env.production.local`.

## Uso diario

1. Iniciar el ERP con `prod-local-start.ps1`.
2. Verificarlo con `prod-local-health.ps1`.
3. Usar el sistema por LAN o Tailscale privado.
4. Si hay un problema, consultar `prod-local-status.ps1` y
   `prod-local-logs.ps1`.
5. Apagar con `prod-local-stop.ps1` únicamente cuando sea necesario.

No es obligatorio apagar el ERP al final de cada jornada si KERNELOS-PC debe
permanecer como servidor y Docker Desktop está configurado para operar de forma
continua.

## Actualizar el sistema

1. Confirmar que el cambio a instalar está aprobado.
2. Ejecutar `git pull` por el procedimiento autorizado.
3. Crear y comprobar un backup antes de actualizar. El backup automático y su
   restauración demostrada siguen pendientes y no forman parte de estos
   scripts.
4. Reconstruir:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-rebuild.ps1
   ```

5. Si la actualización incluye migraciones aprobadas, y solo después del
   backup:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-migrate.ps1
   ```

6. Ejecutar `prod-local-health.ps1`.

`prod-local-rebuild.ps1` ejecuta `up -d --build`; no ejecuta `down -v`, no borra
volúmenes y no aplica migraciones automáticamente.

`prod-local-migrate.ps1` ejecuta `alembic upgrade head`, muestra la revisión
guardada en `alembic_version` y no ejecuta seeds. En este bloque la revisión
esperada sigue siendo `0026_user_roles`.

## Seed inicial

No se creó `prod-local-seed.ps1`. El seed existente solo se documenta para una
base vacía o instalación inicial y no debe formar parte de la operación diaria.
Nunca debe usarse para cambiar la contraseña de un usuario existente ni para
reparar datos.

## URL actuales

| Acceso | URL |
| --- | --- |
| Web LAN | `http://192.168.100.220:3000/login` |
| API LAN | `http://192.168.100.220:8010/api/v1/health` |
| Web Tailscale | `http://100.121.163.126:3000/login` |
| API Tailscale | `http://100.121.163.126:8010/api/v1/health` |

La reserva DHCP sigue pendiente. Si cambia la IP LAN, hay que actualizar
`.env.production.local`, firewall, documentos y scripts. Si cambia la IP
Tailscale, hay que actualizar `.env.production.local`, documentos y scripts.
Esos cambios deben hacerse en un bloque controlado; estos scripts no configuran
red, firewall, Tailscale ni router.

## Accesos directos en Windows

Para cada acceso directo:

1. Clic derecho en el Escritorio.
2. Elegir **Nuevo > Acceso directo**.
3. Pegar uno de los comandos siguientes como ubicación.
4. Asignar el nombre indicado.
5. Opcionalmente, en **Propiedades > Iniciar en**, usar
   `C:\Users\Administrator\Desktop\cuadre-caja-agua-activa`.

**Iniciar ERP Agua Activa**

```text
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Administrator\Desktop\cuadre-caja-agua-activa\scripts\prod-local-start.ps1"
```

**Verificar ERP Agua Activa**

```text
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Administrator\Desktop\cuadre-caja-agua-activa\scripts\prod-local-health.ps1"
```

**Ver logs ERP Agua Activa**

```text
powershell.exe -NoExit -ExecutionPolicy Bypass -File "C:\Users\Administrator\Desktop\cuadre-caja-agua-activa\scripts\prod-local-logs.ps1"
```

**Apagar ERP Agua Activa**

```text
powershell.exe -ExecutionPolicy Bypass -File "C:\Users\Administrator\Desktop\cuadre-caja-agua-activa\scripts\prod-local-stop.ps1"
```

`-NoExit` se recomienda para logs para que la ventana permanezca abierta. Si el
repositorio cambia de ubicación, hay que actualizar los accesos directos.

## Comandos y acciones prohibidos

No ejecutar en operación:

```text
docker compose down -v
docker compose down --volumes
docker volume rm ...
docker volume prune
docker system prune
```

También está prohibido:

- borrar manualmente `postgres_prod_data`;
- publicar PostgreSQL 5432;
- subir o compartir `.env.production.local`;
- mostrar secretos en tickets, chats o documentación;
- compartir la cuenta administradora;
- ejecutar seeds como reparación o en operación diaria;
- restaurar datos sin el procedimiento y backup aprobados;
- abrir router, habilitar Funnel o ampliar firewall como parte de este bloque.

## Pendientes

- Reserva DHCP para la IP LAN.
- Backup automático, retención y copia externa.
- Restauración demostrada en un entorno aislado.
- Rotar contraseñas antes del piloto.
- Piloto paralelo controlado.
- Programador de tareas, servicio de Windows, watchdog y monitoreo externo,
  todos fuera del Bloque 55C.
