# 20 - Checklist de preparación del servidor local

La configuración del Bloque 55A ya está preparada en el repositorio. El bloque
permanece abierto hasta probarla en la PC y este checklist no autoriza ejecutar
todavía el traslado, Tailscale, una restauración oficial ni el piloto. La guía
operativa está en [`23-docker-produccion-local.md`](23-docker-produccion-local.md).

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
- [ ] Backup de línea base creado.
- [ ] Restore de ese backup aprobado en base aislada.
- [ ] Conteos y muestras funcionales coinciden tras restore.
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
- [ ] `BACKEND_CORS_ORIGINS` contiene solo orígenes exactos aprobados.
- [ ] No se usa `*` para CORS.
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

## 5. Red local

- [ ] PC servidor conectado por cable cuando sea posible.
- [ ] Reserva DHCP o IP fija documentada.
- [ ] Nombre DNS/local estable definido, si la red lo permite.
- [ ] Un PC cliente resuelve el nombre o alcanza la IP.
- [ ] Frontend abre desde el cliente.
- [ ] API health abre desde el cliente solo por el camino aprobado.
- [ ] Login funciona desde el cliente.
- [ ] CORS no genera errores.
- [ ] `NEXT_PUBLIC_API_URL` no apunta a `localhost` desde el cliente.
- [ ] No existe port forwarding en el router de Internet.
- [ ] No se usa DMZ del router.
- [ ] Red Wi-Fi usa cifrado moderno y contraseña controlada.
- [ ] Dispositivos invitados no alcanzan el servidor.

## 6. Firewall

- [ ] Política de entrada por defecto restrictiva.
- [ ] Puerto PostgreSQL `5432` bloqueado para todos los dispositivos remotos.
- [ ] Puertos web/API permitidos solo desde la subred local aprobada.
- [ ] Acceso Tailscale permitido solo por la interfaz/ACL correspondiente.
- [ ] Administración remota del sistema limitada a George.
- [ ] No hay reglas públicas `0.0.0.0/0`.
- [ ] Reglas probadas desde un equipo permitido.
- [ ] Reglas probadas desde un equipo/red no permitidos.
- [ ] Resultado y capturas de configuración guardados sin secretos.

## 7. Tailscale privado

- [ ] Configurar solo después de que LAN, firewall y roles estén aprobados.
- [ ] Cuenta Tailscale bajo control de George.
- [ ] MFA habilitado.
- [ ] PC servidor identificado con nombre claro.
- [ ] ACL permite solo a George y dispositivos autorizados.
- [ ] No habilitar Funnel ni exposición pública.
- [ ] PostgreSQL no se publica por Tailscale.
- [ ] Acceso remoto usa web/API, no la base directamente.
- [ ] Dispositivo perdido puede revocarse de inmediato.
- [ ] Claves/dispositivos expirados se revisan periódicamente.
- [ ] Prueba remota realizada desde una red externa.
- [ ] Prueba confirma que un usuario no autorizado no accede.

## 8. Pruebas de acceso

- [ ] `GET /api/v1/health` devuelve `status=ok`.
- [ ] `/login` carga sin error.
- [ ] Login operator válido.
- [ ] Login `admin_auditor` válido.
- [ ] Credenciales inválidas son rechazadas.
- [ ] Token vencido redirige a login.
- [ ] Operator no puede abrir ni invocar acciones administrativas.
- [ ] Ocultar enlace en frontend no es el único control.
- [ ] Dashboard carga.
- [ ] Caja diaria carga y conserva un cuadre por fecha.
- [ ] Historial y detalle cargan.
- [ ] Clientes, productos, inventario, producción y nómina cargan según rol.
- [ ] Panel gerencial y exportaciones respetan permisos.
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

- [ ] Backup PostgreSQL automático cada día.
- [ ] Hora del backup no interrumpe el cierre operativo.
- [ ] Fallo de backup genera alerta.
- [ ] Archivo tiene timestamp, checksum y tamaño mayor que cero.
- [ ] Backup se comprime.
- [ ] Backup se cifra antes de salir del servidor.
- [ ] Retención definida; recomendación inicial:
  - [ ] 7 diarios.
  - [ ] 4 semanales.
  - [ ] 12 mensuales.
- [ ] Existe al menos una copia en medio externo.
- [ ] La copia externa no está permanentemente expuesta a ransomware.
- [ ] `.env` y manual de reconstrucción se respaldan por canal seguro.
- [ ] Backups nunca entran a Git.
- [ ] Espacio de backups se monitorea.

## 11. Restauración

- [ ] Restore se realiza primero en un entorno aislado.
- [ ] Se confirma archivo, fecha, checksum y proyecto.
- [ ] Se crea backup del destino antes de restaurar.
- [ ] Se registra hora inicial y final.
- [ ] El proceso termina sin error.
- [ ] Alembic queda en la revisión esperada.
- [ ] Health y login funcionan.
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

- [ ] Base restaurable y backup de línea base.
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
