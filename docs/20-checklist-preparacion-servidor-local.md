# 20 - Checklist de preparación del servidor local

La configuración del Bloque 55A fue probada en KERNELOS-PC. El acceso del
Bloque 55B-1 también fue confirmado desde otro dispositivo LAN usando la IP
actual. Los Bloques 55B-2 y 55B-2A dejaron instalado y endurecido Tailscale, y
George confirmó Web, API, login, dashboard, panel gerencial y exportaciones
desde su iPhone con datos móviles. También confirmó login, dashboard y una
pantalla operativa por Wi-Fi/LAN con Tailscale apagado. La reserva DHCP sigue
pendiente y es obligatoria antes del piloto. El Bloque 56A implementa backup
manual y prepara la tarea diaria, y el Bloque 56B demuestra una restauración
real en un contenedor temporal aislado. El Bloque 56C registra la tarea diaria a
las 23:30 y valida su inicio manual controlado. Este checklist no autoriza una
restauración sobre producción ni el piloto. Las
evidencias están en
[`24-prueba-docker-produccion-pc.md`](24-prueba-docker-produccion-pc.md) y
[`25-red-local-firewall-pc.md`](25-red-local-firewall-pc.md), y el avance
Tailscale en
[`26-tailscale-acceso-remoto-privado.md`](26-tailscale-acceso-remoto-privado.md).
La restauración controlada está documentada en
[`29-restauracion-controlada-postgresql.md`](29-restauracion-controlada-postgresql.md).
La activación del backup diario está documentada en
[`30-backup-diario-programado-windows.md`](30-backup-diario-programado-windows.md).

## 1. Antes de mover a la PC

- [ ] Bloque 54 de roles y permisos aprobado.
- [ ] Cuentas personales creadas; ninguna contraseña compartida.
- [ ] Matriz `operator`/`admin_auditor` aprobada por George.
- [ ] Todos los hallazgos críticos del documento 19 cerrados.
- [ ] Rama `main` limpia y sincronizada.
- [ ] Commit exacto de despliegue registrado.
- [ ] Tag `pre-pilot-local-v1` creado.
- [ ] `git status --short` vacío.
- [ ] Backend: 930 o más pruebas aprobadas, sin fallos nuevos.
- [ ] Frontend: typecheck y build aprobados.
- [ ] `docker compose config` aprobado sin publicar su salida.
- [ ] `alembic heads`, `current` y base en `0026_user_roles`.
- [ ] Ninguna operación Alembic histórica no autorizada incluida.
- [x] Backup de línea base creado.
- [x] Restore de ese backup aprobado en base aislada.
- [x] Tablas principales y conteos numéricos validados tras el restore.
- [ ] Muestras funcionales e integrales comparadas tras el restore.
- [ ] Tiempo máximo de recuperación medido.
- [ ] Inventario físico del PC, disco y UPS documentado.

## 2. Instalación en la PC

- [ ] Usuario del sistema operativo exclusivo para el ERP.
- [ ] Contraseña fuerte y bloqueo de pantalla.
- [ ] Cifrado del disco habilitado.
- [ ] Actualizaciones del sistema operativo aplicadas.
- [ ] Docker/Compose instalado desde fuente oficial.
- [ ] Inicio automático del equipo tras recuperación eléctrica evaluado.
- [ ] Docker configurado para iniciar con el sistema.
- [ ] Espacio libre suficiente para DB, imágenes, logs y backups.
- [ ] Fecha/hora sincronizada por NTP.
- [ ] Zona de negocio definida como `America/Guayaquil`.
- [ ] Repositorio clonado en ruta estable, no en carpetas sincronizadas
  informalmente.
- [ ] `.env` creado localmente y excluido de Git.
- [ ] Permisos de `.env` limitados al usuario del ERP.
- [ ] No hay dumps ni credenciales en Escritorio, Descargas o nube personal.

## 3. Variables de entorno

- [ ] `ENVIRONMENT=production`.
- [ ] `POSTGRES_PASSWORD` nuevo, largo y único.
- [ ] `DATABASE_URL` usa exactamente la misma contraseña.
- [ ] `ADMIN_PASSWORD` no es default ni se comparte.
- [ ] `AUTH_SECRET_KEY` aleatorio, largo y distinto de otros entornos.
- [ ] `AUTH_ALGORITHM` restringido al algoritmo acordado.
- [ ] Expiración JWT revisada para el horario operativo.
- [ ] `NEXT_PUBLIC_API_URL` es accesible desde un PC cliente.
- [x] `BACKEND_CORS_ORIGINS` contiene solo orígenes exactos aprobados.
- [x] No se usa `*` para CORS.
- [ ] No se usan valores fallback `change-me`.
- [ ] No se imprime `docker compose config` en tickets o chats.
- [ ] Existe copia cifrada y controlada de la configuración necesaria para
  desastre.

## 4. Docker de producción

- [x] Archivo Compose de producción separado del desarrollo.
- [x] API configurada para ejecutar sin `--reload`.
- [x] Web configurada para ejecutar `next start`, no `next dev`.
- [ ] Imágenes construidas desde el commit etiquetado.
- [x] PostgreSQL configurado con volumen persistente nombrado separado.
- [x] Compose productivo no publica `5432` hacia el host.
- [ ] Verificar desde otra PC que PostgreSQL no es accesible por red.
- [ ] Si se mantiene el mapeo, se enlaza exclusivamente a `127.0.0.1`.
- [x] API y Web tienen healthchecks.
- [x] Servicios tienen política `restart: unless-stopped`.
- [x] Logs tienen rotación y límite básico.
- [ ] Límites de CPU/memoria revisados.
- [x] API y Web configuradas con usuarios no root.
- [ ] Versiones de imágenes fijadas y actualización planificada.
- [x] Migraciones documentadas como paso consciente y respaldado.
- [x] Seeds no se ejecutan automáticamente en cada arranque.
- [x] `docker compose down -v` está prohibido en operación.

Comandos operativos esperados, una vez aprobados:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production.local up -d
docker compose -f docker-compose.prod.yml --env-file .env.production.local ps
docker compose -f docker-compose.prod.yml --env-file .env.production.local down
```

Nunca:

```text
docker compose down -v
```

### Scripts PowerShell de Windows (Bloque 55C)

- [x] `prod-local-start.ps1` inicia sin `--build` y sin migraciones/seeds.
- [x] `prod-local-stop.ps1` apaga con `down` y conserva los volúmenes.
- [x] `prod-local-health.ps1` verifica Compose, contenedores, API, Web,
  Alembic, PostgreSQL 5432 y estado Git del archivo de entorno.
- [x] `prod-local-logs.ps1` filtra `api`, `web`, `db` o todos los servicios.
- [x] `prod-local-status.ps1` muestra estado y URL sin modificar nada.
- [x] `prod-local-rebuild.ps1` reconstruye sin borrar volúmenes.
- [x] `prod-local-migrate.ps1` queda separado, advertido y nunca ejecuta seeds.
- [x] Los scripts `.sh` permanecen disponibles para macOS/Linux y no son
  requeridos en Windows.
- [x] Los accesos directos y comandos prohibidos están documentados en
  [`27-scripts-powershell-servidor-local.md`](27-scripts-powershell-servidor-local.md).
- [x] Backup manual con SHA256, metadata y `pg_restore --list` implementado en
  el Bloque 56A.
- [x] Registro, consulta y desregistro de tarea diaria preparados.
- [x] Tarea `AguaActivaERP-BackupDiario` registrada a las 23:30 y validada
  mediante inicio manual controlado en el Bloque 56C.
- [x] Restauración demostrada en contenedor temporal aislado por el Bloque 56B.
- [ ] Piloto controlado; no se inicia con estos scripts.

## 5. Red local

- [x] PC servidor conectado por cable cuando sea posible.
- [ ] Reserva DHCP o IP fija configurada; recomendación y bloqueo documentados.
- [ ] Nombre DNS/local estable definido, si la red lo permite.
- [x] Un cliente LAN alcanza la IP.
- [x] Frontend abre desde el cliente.
- [x] API health abre desde el cliente solo por el camino aprobado.
- [x] Login funciona desde el cliente.
- [x] CORS no genera errores en la prueba LAN.
- [x] `NEXT_PUBLIC_API_URL` no apunta a `localhost` desde el cliente.
- [ ] No existe port forwarding en el router de Internet.
- [ ] No se usa DMZ del router.
- [ ] Red Wi-Fi usa cifrado moderno y contraseña controlada.
- [ ] Dispositivos invitados no alcanzan el servidor.

## 6. Firewall

- [ ] Política de entrada por defecto restrictiva.
- [x] Puerto PostgreSQL `5432` sin listener ni publicación en el host.
- [x] Puertos web/API permitidos solo desde la subred local aprobada.
- [x] Acceso Tailscale permitido solo por la interfaz y puertos 3000/8010
  correspondientes.
- [ ] Administración remota del sistema limitada a George.
- [x] No hay reglas ERP en el perfil `Public` ni reglas entrantes genéricas
  habilitadas para las direcciones Tailscale del nodo.
- [x] Reglas probadas desde un equipo permitido.
- [ ] Reglas probadas desde un equipo/red no permitidos.
- [x] Resultado de configuración guardado sin secretos.

## 7. Tailscale privado

- [x] Configurar solo después de que LAN, firewall y roles estén aprobados.
- [x] Cuenta Tailscale bajo control de George.
- [ ] MFA habilitado.
- [x] PC servidor identificado como `kernelos-pc`.
- [ ] ACL permite solo a George y dispositivos autorizados.
- [x] No habilitar Funnel ni exposición pública.
- [x] PostgreSQL no se publica por Tailscale.
- [x] Acceso remoto usa web/API, no la base directamente.
- [ ] Dispositivo perdido puede revocarse de inmediato.
- [ ] Claves/dispositivos expirados se revisan periódicamente.
- [x] Prueba remota realizada desde datos móviles en el iPhone de George.
- [ ] Prueba confirma que un usuario no autorizado no accede.

## 8. Pruebas de acceso

- [x] `GET /api/v1/health` devuelve `status=ok` desde la LAN.
- [x] `/login` carga sin error desde la LAN.
- [x] `GET /api/v1/health` y `/login` responden por la IPv4 Tailscale desde
  KERNELOS-PC.
- [x] Login, dashboard, panel gerencial y exportaciones comprobados desde el
  iPhone de George conectado a Tailscale.
- [x] Login, dashboard y pantalla operativa comprobados por LAN desde el iPhone
  conectado por Wi-Fi y con Tailscale apagado.
- [ ] Login operator válido.
- [x] Login `admin_auditor` válido por la IP LAN.
- [ ] Credenciales inválidas son rechazadas.
- [ ] Token vencido redirige a login.
- [ ] Operator no puede abrir ni invocar acciones administrativas.
- [ ] Ocultar enlace en frontend no es el único control.
- [x] Dashboard carga por la IP LAN.
- [ ] Caja diaria carga y conserva un cuadre por fecha.
- [ ] Historial y detalle cargan.
- [ ] Clientes, productos, inventario, producción y nómina cargan según rol.
- [x] Panel gerencial carga con `admin_auditor`; exportaciones ya verificadas
  en el Bloque 55A-2.
- [ ] Un Excel y un PDF se descargan.
- [ ] Rango sin datos devuelve archivo válido y estado vacío.
- [ ] Ninguna consulta/report/export modifica conteos.
- [ ] Vista móvil o tablet funciona para la secretaria.
- [ ] Impresora/PDF, si aplica, produce salida legible.

## 9. Seguridad operativa

- [ ] Cada persona usa su propia cuenta.
- [ ] No se pegan tokens ni contraseñas en chats.
- [ ] No se comparte `.env`.
- [ ] El navegador del puesto tiene actualizaciones.
- [ ] No se instalan extensiones innecesarias.
- [ ] El equipo de secretaria no usa cuenta de administrador del SO.
- [ ] Sesión se cierra al terminar turno.
- [ ] Correcciones y anulaciones requieren motivo.
- [ ] Acciones críticas se revisan diariamente durante el piloto.
- [ ] `/docs` y `/openapi.json` restringidos o deshabilitados en producción.
- [ ] Login tiene rate limit y registro de intentos.
- [ ] Logs no contienen contraseñas, tokens ni datos completos de personas.

## 10. Backups

- [x] Script de backup manual PostgreSQL implementado.
- [x] Destino `backups/postgres` ignorado por Git.
- [x] Destino `backups/restore-tests` ignorado por Git.
- [x] Archivo manual con timestamp, checksum, metadata y tamaño mayor que cero.
- [x] Formato custom validado con `pg_restore --list`.
- [x] Preparación de tarea diaria implementada con modo `-WhatIf`.
- [x] Tarea de backup PostgreSQL diario registrada a las 23:30.
- [x] Inicio manual de la tarea generó `.dump`, `.sha256` y `.json`, con
  resultado `0`, SHA256 coincidente y `pg_restore --list` aprobado.
- [ ] Hora del backup no interrumpe el cierre operativo.
- [ ] Fallo de backup genera alerta.
- [x] Backup manual usa formato custom comprimido de PostgreSQL.
- [ ] Backup se cifra antes de salir del servidor.
- [ ] Retención definida; recomendación inicial:
  - [ ] 7 diarios.
  - [ ] 4 semanales.
  - [ ] 12 mensuales.
- [ ] Existe al menos una copia en medio externo.
- [ ] La copia externa no está permanentemente expuesta a ransomware.
- [ ] `.env` y manual de reconstrucción se respaldan por canal seguro.
- [x] Backups nunca entran a Git por las reglas actuales de `.gitignore`.
- [ ] Espacio de backups se monitorea.

## 11. Restauración

- [x] Restore se realiza primero en un entorno aislado, sin red ni puertos.
- [x] Se confirma archivo, fecha, checksum y proyecto.
- [ ] Se crea backup del destino antes de restaurar.
- [ ] Se registra hora inicial y final.
- [x] El proceso termina sin error.
- [x] Alembic queda en la revisión esperada `0026_user_roles`.
- [x] Tablas principales existen y sus conteos son numéricos.
- [x] Health productivo aprueba antes y después; 5432 sigue sin publicarse.
- [x] Contenedor temporal eliminado al finalizar.
- [ ] Login y flujos integrales funcionan sobre un entorno restaurado accesible.
- [ ] Conteos de tablas coinciden con el origen.
- [ ] Se revisan muestras de caja, gastos, ventas, inventario, producción,
  compras y nómina.
- [ ] Excel y PDF funcionan en el restaurado.
- [ ] RPO y RTO alcanzados se documentan.
- [ ] Procedimiento de recuperación puede seguirlo otra persona autorizada.

## 12. Energía y continuidad

- [ ] UPS dimensionado para PC servidor, router y switch principal.
- [ ] UPS probado bajo corte controlado.
- [ ] Apagado limpio documentado.
- [ ] Reinicio tras energía probado.
- [ ] Temperatura y ventilación adecuadas.
- [ ] Equipo protegido de agua, polvo y acceso físico no autorizado.
- [ ] Disco revisado y con alerta de espacio/salud.

## 13. Piloto

- [x] Base restaurable y backup de línea base.
- [ ] Un `operator` y un `admin_auditor` definidos.
- [ ] Alcance limitado: productos/clientes/ruta seleccionados.
- [ ] Controles actuales se mantienen en paralelo.
- [ ] Conciliación diaria de caja, ventas, cobros, rutas e inventario.
- [ ] Registro de incidentes sin secretos ni datos personales innecesarios.
- [ ] Reunión diaria corta durante la primera semana.
- [ ] Criterios de pausa definidos.
- [ ] Criterios de éxito definidos.
- [ ] Cierre del piloto incluye restauración de prueba y revisión de riesgos.

## Criterio de autorización

El servidor puede entrar a piloto únicamente cuando:

- todos los ítems críticos estén marcados;
- no haya acceso remoto a PostgreSQL;
- roles se validen en backend;
- backup automático y restore aislado tengan evidencia;
- las pruebas técnicas estén aprobadas;
- George autorice explícitamente el inicio.
