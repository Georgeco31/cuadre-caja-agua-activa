# 23 - Docker para producción local

## Estado y objetivo

El Bloque 55A preparó una configuración Docker separada para Agua Activa ERP y
el Bloque 55A-2 la probó en KERNELOS-PC. El Bloque 55C añade operación nativa
con PowerShell. Esta evidencia permite la prueba controlada, pero **no convierte
todavía el equipo en servidor oficial** ni autoriza el piloto.

Los bloques posteriores documentaron LAN y Tailscale privado sin Funnel. El
Bloque 56A incorpora backup manual seguro y prepara la tarea diaria de Windows
sin registrarla automáticamente. Siguen pendientes la reserva DHCP, la
ejecución automática comprobada, restauración demostrada y piloto. Ninguno de
estos bloques mueve o restaura una base oficial, crea migraciones, ejecuta seeds
o cambia reglas de negocio.

## Desarrollo frente a producción local

| Tema | Desarrollo | Producción local |
| --- | --- | --- |
| Compose | `docker-compose.yml` | `docker-compose.prod.yml` |
| Variables | `.env` | `.env.production.local` |
| API | `apps/api/Dockerfile` | `apps/api/Dockerfile.prod` |
| Web | `apps/web/Dockerfile` | `apps/web/Dockerfile.prod` |
| PostgreSQL | Volumen `postgres_data`; puerto configurable en host | Volumen `postgres_prod_data`; sin puerto publicado |
| API | Uvicorn en `0.0.0.0:8000`, sin reload | Uvicorn en `0.0.0.0:8000`, sin reload y usuario no root |
| Web | Imagen existente | `npm run build` en imagen y `npm run start` al ejecutar |
| Arranque | Scripts `local-*` | Scripts `prod-local-*` |
| Migraciones/seeds | Pasos manuales | Pasos manuales, nunca automáticos al arrancar |

El Compose de desarrollo no fue reemplazado. Los volúmenes también están
separados para impedir que una prueba productiva reutilice accidentalmente la
base de desarrollo.

## Archivos del Bloque 55A

- `docker-compose.prod.yml`: servicios `db`, `api` y `web`, healthchecks,
  reinicio automático y rotación básica de logs.
- `apps/api/Dockerfile.prod`: imagen FastAPI productiva sin `--reload`.
- `apps/web/Dockerfile.prod`: build multi-stage y arranque con
  `npm run start`.
- `.env.production.example`: plantilla versionable sin secretos reales.
- `scripts/prod-local-common.sh`: validaciones compartidas sin cargar el
  archivo de entorno como código de shell.
- `scripts/prod-local-start.sh`: valida, construye e inicia.
- `scripts/prod-local-health.sh`: revisa contenedores, API, Web y Alembic.
- `scripts/prod-local-logs.sh`: muestra los últimos 200 registros.
- `scripts/prod-local-stop.sh`: apaga sin eliminar volúmenes.
- `scripts/prod-local-*.ps1`: operación equivalente y ampliada para Windows,
  con inicio sin build por defecto, estado, rebuild y migración consciente.
- `scripts/prod-local-backup-*.ps1`: backup PostgreSQL, listado y preparación
  segura de la tarea diaria de Windows del Bloque 56A.

Los `.sh` son útiles en macOS/Linux. En KERNELOS-PC se usan los `.ps1` del
Bloque 55C, documentados en
  [`27-scripts-powershell-servidor-local.md`](27-scripts-powershell-servidor-local.md).
El backup del Bloque 56A está en
[`28-backups-postgresql-windows.md`](28-backups-postgresql-windows.md).

## Aislamiento de PostgreSQL

El servicio `db` no tiene una sección `ports`. PostgreSQL escucha en el puerto
5432 solo dentro de la red Docker interna `backend`; únicamente la API está
conectada a esa red. La Web y la API tienen puertos publicados porque el
navegador de la LAN deberá alcanzarlas en una etapa posterior.

La ausencia de publicación se puede comprobar sin modificar datos:

```bash
docker compose \
  -f docker-compose.prod.yml \
  --env-file .env.production.local \
  ps
```

La fila de `db` no debe mostrar un mapeo como `0.0.0.0:5432->5432/tcp`.
El texto `5432/tcp` por sí solo describe el puerto interno del contenedor y no
es una publicación. No se debe agregar un mapeo de 5432 para facilitar
administración.

## Preparar `.env.production.local`

Desde la raíz del repositorio:

```bash
cp .env.production.example .env.production.local
chmod 600 .env.production.local
```

`.env.production.local` está ignorado por Git. No debe copiarse a tickets,
chats, commits, nubes personales ni carpetas compartidas. La plantilla contiene
marcadores y no puede usarse directamente para iniciar.

Antes de construir se deben reemplazar, como mínimo:

- `POSTGRES_PASSWORD`: contraseña nueva, larga y exclusiva para PostgreSQL.
- `DATABASE_URL`: debe contener el mismo usuario, contraseña y base. Si la
  contraseña contiene caracteres reservados de URL, deben codificarse en esta
  variable.
- `AUTH_SECRET_KEY`: secreto aleatorio de al menos 32 caracteres, distinto a
  otros entornos.
- `ADMIN_PASSWORD`: contraseña inicial fuerte y no compartida.
- `CORS_ORIGINS`: lista JSON de orígenes exactos permitidos, sin `*`.
- `NEXT_PUBLIC_API_URL`: URL que el navegador cliente puede alcanzar.

Los secretos se pueden generar localmente sin guardarlos en el historial:

```bash
openssl rand -hex 24
openssl rand -hex 32
```

El primer resultado puede servir como contraseña alfanumérica URL-safe y el
segundo como `AUTH_SECRET_KEY`. Cada valor debe ser distinto.

Para una prueba solo en el MacBook se permiten temporalmente:

```dotenv
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
NEXT_PUBLIC_API_URL=http://localhost:8010/api/v1
```

En la futura PC se debe reemplazar `localhost` por la IP o el nombre LAN real,
después de aprobar la red en el Bloque 55B. Una URL `localhost` compilada en la
Web apuntaría al propio PC cliente y no al servidor.

Variables incluidas:

- Aplicación: `PROJECT_NAME`, `API_SERVICE_NAME`, `API_V1_PREFIX`,
  `ENVIRONMENT` y `TZ`.
- Base: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` y `DATABASE_URL`.
- Autenticación: `AUTH_SECRET_KEY`, `AUTH_ALGORITHM` y
  `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Seed inicial: `ADMIN_USERNAME`, `ADMIN_PASSWORD` y `ADMIN_IS_ACTIVE`.
- Red: `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, `API_BIND_ADDRESS`, `API_PORT`,
  `WEB_BIND_ADDRESS` y `WEB_PORT`.

`NEXT_PUBLIC_API_URL` se incorpora al bundle durante `npm run build`. Cambiarla
en el archivo de entorno requiere reconstruir la imagen Web.

## Validar y construir

Validar Compose sin imprimir la configuración resuelta, que puede contener
secretos:

```bash
docker compose \
  -f docker-compose.prod.yml \
  --env-file .env.production.local \
  config --quiet
```

Construir sin iniciar:

```bash
docker compose \
  -f docker-compose.prod.yml \
  --env-file .env.production.local \
  build
```

## Iniciar

En Windows:

```powershell
.\scripts\prod-local-start.ps1
```

Este inicio usa `up -d` sin `--build`. Para reconstruir después de una
actualización aprobada se usa `prod-local-rebuild.ps1`, siempre después de un
backup comprobado.

En macOS/Linux:

```bash
./scripts/prod-local-start.sh
```

El script:

1. exige Docker Compose v2 y `.env.production.local`;
2. rechaza variables obligatorias vacías, marcadores de ejemplo, CORS `*` y
   secretos con longitud insuficiente;
3. valida Compose;
4. inicia `db`, `api` y `web`; el `.ps1` no construye por defecto;
5. no aplica migraciones y no ejecuta seeds.

El `.ps1` requiere imágenes ya construidas. La primera reconstrucción con
`prod-local-rebuild.ps1` puede tardar; los inicios diarios reutilizan esas
imágenes. Las URL locales por defecto son:

```text
http://localhost:3000/login
http://localhost:8010/api/v1/health
```

## Aplicar migraciones conscientemente

Antes de migrar una base que contenga información se debe crear y comprobar un
backup. Para la primera base vacía o después de ese respaldo:

```bash
docker compose \
  -f docker-compose.prod.yml \
  --env-file .env.production.local \
  run --rm api alembic upgrade head
```

En este bloque `head` debe seguir siendo `0026_user_roles`. El arranque no
ejecuta este comando automáticamente para evitar cambios de esquema
inadvertidos.

Consultar la revisión aplicada:

```bash
docker compose \
  -f docker-compose.prod.yml \
  --env-file .env.production.local \
  exec -T api alembic current
```

## Seed inicial: solo con base vacía

Después de migrar una base nueva y confirmar que está vacía:

```bash
docker compose \
  -f docker-compose.prod.yml \
  --env-file .env.production.local \
  run --rm api python -m app.seeds.run
```

Este paso crea las denominaciones y el administrador inicial de forma
idempotente. `ADMIN_PASSWORD` debe haberse cambiado antes de ejecutarlo y la
cuenta admin no debe compartirse.

Si el usuario indicado ya existe, volver a ejecutar el seed **no cambia su
contraseña**. Cambiar `ADMIN_PASSWORD` en el archivo de entorno tampoco rota la
contraseña de una cuenta existente; se necesitará el flujo autorizado de
administración o reset correspondiente. No se debe usar el seed como mecanismo
de cambio de contraseña.

## Verificación

Después de migrar:

```powershell
.\scripts\prod-local-health.ps1
```

En macOS/Linux también permanece disponible:

```bash
./scripts/prod-local-health.sh
```

La verificación confirma:

- los contenedores `db`, `api` y `web` están activos;
- `/api/v1/health` devuelve `status=ok`;
- `/login` responde;
- Alembic contiene `0026_user_roles`;
- PostgreSQL 5432 no está publicado;
- `.env.production.local` no está versionado.

El healthcheck no crea ni cambia datos. Si la base todavía no fue migrada, la
consulta de Alembic fallará de forma intencional.

## Logs

En Windows, mostrar los últimos 100 registros de todos los servicios o filtrar:

```powershell
.\scripts\prod-local-logs.ps1
.\scripts\prod-local-logs.ps1 -Service api
.\scripts\prod-local-logs.ps1 -Service web -Tail 200
```

En macOS/Linux, mostrar los últimos 200 registros de todos los servicios:

```bash
./scripts/prod-local-logs.sh
```

Limitar a uno o más servicios:

```bash
./scripts/prod-local-logs.sh api
./scripts/prod-local-logs.sh db web
```

Los logs Docker rotan con un máximo de cinco archivos de 10 MB por servicio.
Aun así, se debe revisar que la aplicación no registre contraseñas, tokens o
datos personales completos.

## Apagar sin borrar datos

En Windows:

```powershell
.\scripts\prod-local-stop.ps1
```

En macOS/Linux:

```bash
./scripts/prod-local-stop.sh
```

El script ejecuta `down` sin `--volumes`; el volumen
`postgres_prod_data` se conserva.

Está prohibido en operación:

```text
docker compose down -v
```

También está prohibido borrar manualmente el volumen, restaurar sobre la base
sin backup o ejecutar seeds repetidamente para intentar reparar usuarios.

## Seguridad mínima de esta etapa

- No subir `.env.production.local`, dumps ni backups a Git.
- No reutilizar contraseñas de desarrollo ni compartir la cuenta admin.
- No publicar PostgreSQL hacia el host o la LAN.
- No abrir puertos en el router ni habilitar DMZ.
- CORS debe contener solo los orígenes exactos aprobados.
- La futura PC debe usar un usuario del sistema protegido por contraseña,
  bloqueo de pantalla y cifrado de disco.
- Se recomienda una UPS para PC, router y switch.
- Se requiere backup comprobado antes de cada actualización.
- Los puertos 3000 y 8010 todavía no se consideran seguros para una red no
  confiable; firewall y HTTPS/acceso cifrado quedan pendientes.

## Qué no hacer en el Bloque 55A

- No mover ni restaurar la base oficial.
- No insertar datos reales o falsos.
- No crear migraciones ni modificar seeds.
- No configurar IP fija, firewall, Tailscale, router o puertos públicos.
- No crear cuentas reales para la secretaria.
- No iniciar el piloto.
- No usar esta preparación como autorización de producción.

## Checklist antes de llevar el proyecto a la PC

- [ ] Cambios del Bloque 55A revisados y commit manual identificado.
- [x] Backend, typecheck, build y ambos Compose aprobados en el MacBook.
- [x] Alembic sigue exactamente en `0026_user_roles`.
- [x] No existe una migración `0027`.
- [x] `.env.production.local` no está versionado.
- [ ] Secretos productivos se generarán directamente en la PC.
- [ ] Backup reciente y restauración aislada comprobados antes de mover datos.
- [ ] Inventario de hardware, disco disponible y UPS documentados.
- [ ] George autoriza expresamente la prueba en la PC, no el piloto.

## Evidencia del smoke test en MacBook

El 26 de julio de 2026 se validó una pila Docker aislada, sin reutilizar los
puertos ni el volumen de desarrollo:

- las imágenes productivas de API y Web se construyeron correctamente;
- `db`, `api` y `web` alcanzaron estado healthy;
- la API respondió `status=ok` y la Web respondió en `/login`;
- las migraciones existentes se aplicaron a una base aislada y vacía hasta
  `0026_user_roles`;
- no se ejecutó ningún seed;
- la API ejecutó Uvicorn sin reload como usuario no root;
- la Web ejecutó `npm run start` como usuario no root;
- la inspección de Docker devolvió bindings de puertos `{}` para PostgreSQL;
- `prod-local-logs.sh` mostró los logs recientes;
- `prod-local-stop.sh` apagó los servicios y conservó el volumen;
- el archivo temporal `.env.production.local` se eliminó al terminar.

Esta evidencia valida la preparación en el MacBook, no sustituye la prueba
pendiente en la PC ni autoriza datos reales.

## Checklist de prueba en PC para el Bloque 55A-2

- [ ] Instalar Docker/Compose desde una fuente oficial.
- [ ] Crear un usuario del sistema exclusivo y protegido.
- [ ] Clonar el commit aprobado en una ruta estable.
- [ ] Crear `.env.production.local` con permisos restrictivos y secretos nuevos.
- [ ] Definir la IP/nombre LAN solo en el bloque autorizado.
- [ ] Ejecutar `config --quiet` y construir las imágenes.
- [ ] Iniciar con `prod-local-start.sh`.
- [ ] Migrar una base vacía y confirmar `0026_user_roles`.
- [ ] Ejecutar el seed inicial una sola vez con credenciales de prueba
  autorizadas, sin datos reales.
- [ ] Confirmar que `db` no publica 5432.
- [ ] Confirmar API y Web saludables.
- [ ] Abrir `/login`, dashboard, panel gerencial y exportaciones.
- [ ] Apagar y volver a iniciar; confirmar persistencia del volumen.
- [ ] Apagar con `prod-local-stop.sh` sin borrar datos.
- [ ] Registrar resultados sin incluir secretos.

## Riesgos y bloques pendientes

Docker de producción local queda **preparado y probado en KERNELOS-PC para la
prueba controlada**, sin que esto autorice el piloto. Continúan pendientes:

- IP fija o reserva DHCP y nombre LAN.
- Firewall restrictivo.
- CORS con la dirección LAN real.
- HTTPS local o acceso cifrado equivalente.
- Tailscale privado de los Bloques 55B-2 y 55B-2A: acceso remoto y acceso
  Wi-Fi/LAN comprobados desde el iPhone de George, sin Funnel; acceso dual listo
  para prueba controlada.
- Contraseña PostgreSQL y secretos productivos creados en la PC.
- Ejecución comprobada de la tarea diaria; el backup manual con checksum y su
  preparación automática ya están implementados en el Bloque 56A.
- Retención, cifrado avanzado, alertas y copia externa.
- Restauración demostrada en un entorno aislado.
- Reserva DHCP para conservar estable la IP LAN usada en configuración,
  documentos y scripts.
- Monitoreo, alertas, revisión de disco y prueba de UPS.
- Restricción de OpenAPI y rate limiting del login.
- Auditoría y remediación controlada de dependencias: durante el build,
  `npm ci --omit=dev` informó dos vulnerabilidades de severidad alta. No se
  ejecutó `npm audit fix --force` porque podría introducir cambios
  incompatibles fuera del alcance de este bloque.
- Pruebas desde un cliente LAN autorizado y desde uno no autorizado.
- Smoke E2E, capacitación y piloto controlado del Bloque 56.

Ninguno de estos puntos debe darse por cerrado solo porque el Compose funcione
en el MacBook.
