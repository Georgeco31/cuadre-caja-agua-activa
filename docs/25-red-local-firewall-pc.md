# 25 - Red local y firewall en PC

## Alcance

- Bloque: 55B-1.
- Fecha: 2026-07-27 11:10:28 -05:00.
- PC: KERNELOS-PC.
- Estado operativo: prueba controlada; esta PC todavía no se declara servidor
  oficial.
- No se configuraron Tailscale, port forwarding, DMZ ni puertos públicos del
  router.
- No se restauró la base oficial y no se inició piloto.

## Red detectada

- Interfaz activa: `Ethernet`.
- Adaptador: Intel(R) Ethernet Controller I226-V.
- IPv4 privada: `192.168.100.220`.
- Máscara: `255.255.255.0` (`/24`).
- Puerta de enlace: `192.168.100.1`.
- DNS IPv4: `192.168.100.1`.
- Asignación IPv4: DHCP habilitado.
- Perfil encontrado al inicio: `Public`.
- Perfil aplicado a la interfaz identificada: `Private`.

La recomendación para una instalación estable es crear una **reserva DHCP** en
el router para la interfaz Ethernet de KERNELOS-PC. Se prefiere una reserva
DHCP sobre fijar manualmente la IP en Windows porque centraliza la asignación y
reduce el riesgo de duplicar direcciones. Antes de reservar
`192.168.100.220`, el administrador de la red debe confirmar que la dirección
puede quedar fuera de asignaciones conflictivas y registrar la reserva. Este
bloque no modificó el router.

Mientras no exista la reserva, la dirección puede cambiar después de reinicios
del router o de la concesión DHCP. Si cambia, se deben actualizar CORS y
`NEXT_PUBLIC_API_URL`, reconstruir Web y volver a verificar las reglas y las
pruebas LAN.

## Configuración local de producción

Se actualizó `.env.production.local` únicamente en KERNELOS-PC. El archivo
permanece ignorado por Git y no se reproduce completo en este documento.

- `CORS_ORIGINS` conserva los orígenes locales y agrega exactamente
  `http://192.168.100.220:3000`.
- `NEXT_PUBLIC_API_URL` apunta a
  `http://192.168.100.220:8010/api/v1`.
- API usa el puerto `8010` y escucha en las interfaces del host.
- Web usa el puerto `3000` y escucha en las interfaces del host.
- No se modificaron ni documentaron contraseñas, tokens o claves.

Como `NEXT_PUBLIC_API_URL` forma parte del build del frontend, se ejecutó una
reconstrucción de Web con Docker Compose. La pila se detuvo con `down` sin
`-v`; no se eliminó ningún volumen.

## Docker y base de datos

Después de la reconstrucción:

- `db`, `api` y `web` quedaron saludables.
- Web publicó `0.0.0.0:3000->3000/tcp`.
- API publicó `0.0.0.0:8010->8000/tcp`.
- PostgreSQL mostró únicamente `5432/tcp` dentro de Docker.
- `docker inspect` devolvió `{"5432/tcp":null}` para los puertos publicados de
  PostgreSQL.
- `netstat` no mostró listeners del host en `:5432`.
- Alembic siguió en `0026_user_roles`.
- No se crearon migraciones y no se modificaron seeds.

Que Web y API escuchen en `0.0.0.0` permite llegar por la IP de la PC; la
restricción a la red privada se aplica con el perfil y las reglas de Windows
Firewall descritas abajo. PostgreSQL no tiene publicación equivalente.

## Windows Firewall

Se crearon dos reglas entrantes:

| Regla | Perfil | Origen remoto | Protocolo | Puerto | Acción |
| --- | --- | --- | --- | --- | --- |
| Agua Activa ERP Web 3000 Private | Private | LocalSubnet | TCP | 3000 | Allow |
| Agua Activa ERP API 8010 Private | Private | LocalSubnet | TCP | 8010 | Allow |

Ambas reglas están habilitadas y tienen `EdgeTraversalPolicy=Block`. No se creó
una regla para `5432`, para el perfil `Public` ni para redes remotas fuera de
`LocalSubnet`.

## Pruebas desde KERNELOS-PC por la IP LAN

- `http://192.168.100.220:3000/login` respondió HTTP 200.
- `http://192.168.100.220:8010/api/v1/health` respondió HTTP 200 con
  `status=ok`.
- La respuesta a un request con origen
  `http://192.168.100.220:3000` incluyó
  `Access-Control-Allow-Origin: http://192.168.100.220:3000`.
- Una prueba con el origen no aprobado `http://192.168.100.221:3000` no
  recibió el encabezado `Access-Control-Allow-Origin`.
- Las pruebas TCP a `192.168.100.220:3000` y
  `192.168.100.220:8010` fueron exitosas.
- El navegador cargó `/login` usando la IP LAN.
- El login del administrador temporal local funcionó sin exponer sus
  credenciales.
- El navegador redirigió a `/dashboard`.
- `/dashboard/management` cargó sus indicadores.
- No se observaron errores de consola durante esta prueba.
- No se repitieron exportaciones en este bloque; ya habían sido comprobadas en
  la prueba Docker anterior.

Estas verificaciones prueban la publicación por IP, el build del frontend, el
origen CORS y el flujo local. Posteriormente fueron complementadas con la
confirmación desde otro dispositivo de la red.

## Prueba desde otro dispositivo LAN

El 2026-07-27 se recibió confirmación de que la prueba LAN fue exitosa desde
otro dispositivo usando la IP actual `192.168.100.220`. Con esta evidencia se
considera validado el acceso al ERP desde un cliente de la misma red local,
incluido el flujo de acceso solicitado para Web, API health y login. No se
documentaron credenciales ni datos sensibles de la prueba.

La comprobación confirma la dirección actual. Si DHCP asigna otra IPv4, el
resultado deja de ser suficiente hasta actualizar la configuración y repetir
la prueba.

## Problemas encontrados

- La interfaz Ethernet estaba clasificada como `Public`. Se cambió únicamente
  esa interfaz identificada al perfil `Private` antes de crear las reglas.
- Web y API estaban enlazadas a `127.0.0.1`; se ajustaron localmente para
  permitir acceso LAN.
- La IP depende de DHCP y todavía no tiene una reserva configurada en el
  router.
- No se tienen las credenciales administrativas del router para crear la
  reserva DHCP.

## Pendientes

### Antes del piloto

- Confirmar desde otro equipo que PostgreSQL no acepta conexiones en `5432`.
- Solicitar las credenciales del router o pedir al proveedor/técnico que
  configure una reserva DHCP para KERNELOS-PC usando la tarjeta Ethernet.
- Registrar la dirección reservada sin configurar port forwarding.
- Si la IP cambia antes de crear la reserva, actualizar CORS y
  `NEXT_PUBLIC_API_URL`, reconstruir Web y repetir las pruebas LAN.

### Para 55B-2

- Configurar Tailscale solo después de cerrar y aprobar la prueba LAN.
- No habilitar Funnel ni ninguna exposición pública.

### Para el Bloque 56

- Implementar backup automático, retención, checksum, cifrado y copia externa.
- Demostrar restauración en un ambiente aislado.
- Mantener el piloto bloqueado hasta que backup y restauración estén aprobados.

## Conclusión

**Acceso LAN listo para prueba controlada, con reserva DHCP pendiente antes del
piloto.**

Web, API, CORS, login por IP y firewall fueron verificados en el servidor, y el
acceso fue confirmado desde otro dispositivo LAN usando `192.168.100.220`.
PostgreSQL continúa sin publicación hacia el host. La falta de reserva DHCP no
impide esta prueba controlada, pero debe resolverse antes del piloto para evitar
que una renovación cambie la IP. La PC continúa como equipo de prueba
controlada y no como servidor oficial definitivo.
