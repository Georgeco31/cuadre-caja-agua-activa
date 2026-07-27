# 24 - Prueba Docker produccion local en PC

## Fecha y equipo

- Fecha: 2026-07-27 10:49:18 -05:00.
- PC usada: KERNELOS-PC.
- Ruta local del repo: `C:\Users\Administrator\Desktop\cuadre-caja-agua-activa`.
- Resultado general: la PC puede ejecutar Agua Activa ERP en modo Docker de produccion local para prueba controlada.
- Estado operativo: esta PC no queda declarada como servidor oficial.

## Resultado de la prueba

- Repo actualizado: `git pull` respondio `Already up to date`.
- `.env.production.local` fue creado localmente desde `.env.production.example`.
- `.env.production.local` esta ignorado por Git mediante `.gitignore`.
- Los secretos locales fueron generados para esta prueba y no se documentan.
- API y Web quedaron publicados solo en `127.0.0.1`.
- PostgreSQL no publica `5432` hacia el host.
- Docker Compose valido la configuracion con `config --quiet`.
- Docker Desktop / Docker Compose funciono correctamente para construir e iniciar la pila.
- Servicios iniciados: `db`, `api` y `web`.
- API health respondio `{"status":"ok","service":"agua-activa-erp-api"}`.
- Web respondio HTTP 200 en `/login`.
- Alembic quedo en `0026_user_roles`.
- Login con el admin temporal local funciono.
- Dashboard cargo despues del login.
- `/dashboard/management` cargo con rol `admin_auditor`.
- `/dashboard/exports` cargo con rol `admin_auditor`.
- Exportacion Excel verificada: archivo `.xlsx` generado con firma `PK`.
- Exportacion PDF verificada: archivo `.pdf` generado con firma `%PDF`.

## Migraciones y seed

- Se ejecutaron migraciones manualmente con Docker Compose hasta `head`.
- La revision aplicada fue `0026_user_roles`.
- Antes del seed, la base estaba vacia para las tablas semilla: `users=0`, `denominations=0`.
- Se ejecuto el seed inicial una sola vez.
- Despues del seed quedaron `users=1` y `denominations=12`.
- El usuario inicial quedo activo con rol `admin_auditor`.
- No se crearon migraciones.
- No se modificaron seeds.
- No se restauraron datos oficiales.
- No se crearon datos falsos adicionales.

## PostgreSQL

- `docker compose ps` mostro `db` con `5432/tcp` interno.
- `docker inspect` mostro `{"5432/tcp":null}` para los puertos publicados de PostgreSQL.
- No existe mapeo tipo `0.0.0.0:5432->5432/tcp`.
- API y Web quedaron en:
  - `127.0.0.1:8010->8000/tcp`
  - `127.0.0.1:3000->3000/tcp`

## Persistencia

- Se apago la pila con `docker compose down`.
- No se uso `down -v`.
- No se borro ningun volumen.
- Se inicio de nuevo la pila con el mismo volumen.
- Despues del reinicio:
  - API health siguio respondiendo `status=ok`.
  - Web siguio respondiendo HTTP 200 en `/login`.
  - Alembic siguio en `0026_user_roles`.
  - Persistieron `users=1` y `denominations=12`.
  - El admin temporal local pudo iniciar sesion de nuevo.

## Problemas encontrados

- Los scripts `.sh` no pudieron ejecutarse directamente porque Windows Subsystem for Linux no tiene distribuciones instaladas en esta PC.
- Se usaron los comandos Docker Compose equivalentes desde PowerShell, sin cambiar logica del proyecto.
- `Invoke-WebRequest` requirio `-UseBasicParsing` en esta instalacion de PowerShell.
- El navegador integrado de Codex no soporta eventos de descarga; por eso las descargas se verificaron con API autenticada y archivos temporales fuera del repo.
- Durante el build de Web, `npm ci` reporto vulnerabilidades de severidad alta ya conocidas por la documentacion del bloque anterior. No se ejecuto `npm audit fix`.

## Pendientes para Bloque 55B

- No configurar todavia IP fija o reserva DHCP.
- No configurar todavia firewall.
- No configurar todavia Tailscale.
- No abrir puertos en router.
- No publicar puertos publicos.
- No restaurar todavia la base oficial.
- No declarar esta PC como servidor oficial.
- Definir CORS y `NEXT_PUBLIC_API_URL` para red LAN solo cuando ese bloque sea aprobado.
- Preparar estrategia de backups, restauracion comprobada, retencion y monitoreo.
- Ejecutar prueba desde cliente LAN autorizado y cliente no autorizado cuando corresponda.
- Resolver o aceptar formalmente el riesgo de dependencias reportado por `npm audit`.
- Mantener esta base como base local de prueba controlada hasta nueva aprobacion.

## Seguridad y Git

- No se documentaron passwords, tokens, dumps, backups ni `AUTH_SECRET_KEY`.
- No se subio `.env.production.local`.
- No se ejecuto `git add`.
- No se hizo commit.
- No se hizo push.
- No se inicio piloto.
