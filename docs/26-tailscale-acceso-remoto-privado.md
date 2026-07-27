# 26 - Acceso remoto privado por Tailscale y acceso dual

## Ficha de la prueba

- Bloques: 55B-2 y 55B-2A.
- Fecha: 2026-07-27 11:52:45 -05:00.
- Actualización acceso dual: 2026-07-27 12:23:41 -05:00.
- Cierre de evidencia final: 2026-07-27 12:36:58 -05:00.
- PC: KERNELOS-PC.
- Estado: acceso remoto Tailscale y acceso LAN validados desde el iPhone de
  George. Acceso dual LAN/Tailscale listo para prueba controlada.
- Esta PC continúa como equipo de prueba controlada y no se declara servidor
  oficial definitivo.

## Objetivo

Permitir que George acceda a Web y API del ERP desde fuera de Agua Activa por
una red privada Tailscale, sin publicar servicios en Internet, abrir el router,
usar port forwarding ni exponer PostgreSQL.

En este proyecto, Tailscale crea una red privada cifrada entre los dispositivos
autorizados de George. La dirección `100.x.y.z` asignada al equipo pertenece a
esa red privada; no es una IP pública. Este bloque usa directamente esa
dirección para Web y API. No configura Funnel, Serve, subnet router ni exit
node.

## Instalación y conexión del equipo

- Sistema comprobado: Windows 10 Pro, versión 10.0.19045.
- Cliente instalado: Tailscale 1.98.9 para Windows x64.
- Fuente: paquete MSI del canal estable oficial de Tailscale.
- Integridad: checksum SHA-256 coincidente.
- Firma digital: válida, emitida para Tailscale Inc.
- Servicio Windows: `Tailscale`, inicio automático y estado `Running`.
- Cuenta: sesión bajo control de George; no se registró el identificador de la
  cuenta ni ninguna credencial.
- Nombre del nodo: `kernelos-pc`.
- Estado del nodo: conectado.
- IPv4 Tailscale de KERNELOS-PC: `100.121.x.x` (enmascarada).
- Dispositivo remoto comprobado: iPhone de George, identificado después como
  peer del mismo tailnet.

No se usaron auth keys, tokens ni credenciales en comandos, archivos
versionados o documentación.

## Configuración local del ERP

Se actualizó `.env.production.local` solo en KERNELOS-PC:

- `CORS_ORIGINS` conserva localhost, `127.0.0.1` y la IP LAN, y agrega el origen
  Web exacto de Tailscale.
- `NEXT_PUBLIC_API_URL` conserva la API Tailscale como fallback para
  renderizado de servidor y localhost.
- No se cambió ni reprodujo ningún secreto.
- El archivo sigue ignorado por Git y no aparece en `git status --short`.

Como `NEXT_PUBLIC_API_URL` se incorpora al bundle del frontend, se validó
Compose, se detuvo la pila con `down` sin `-v` y se reconstruyó con
`up -d --build`. No se borraron volúmenes.

El primer build Tailscale reveló que una única URL compilada rompía el flujo LAN
para clientes sin Tailscale. Se corrigió `apps/web/lib/api.ts` para resolver la
API en tiempo de ejecución usando el hostname actual del navegador:

- Web LAN usa `http://192.168.100.220:8010/api/v1`.
- Web Tailscale usa `http://100.121.163.126:8010/api/v1`.
- localhost y renderizado de servidor conservan `NEXT_PUBLIC_API_URL` como
  fallback.
- Las solicitudes JSON y las descargas Excel/PDF usan el mismo helper.

La función pura de resolución fue comprobada para LAN, Tailscale, localhost y
renderizado de servidor. `npm run typecheck`, `npm run build` y el build Docker
productivo aprobaron las 38 rutas del frontend.

Después de la reconstrucción:

- `db`, `api` y `web` quedaron saludables.
- Web publicó únicamente el puerto de aplicación `3000`.
- API publicó únicamente el puerto de aplicación `8010`.
- PostgreSQL mostró `5432/tcp` solo dentro de Docker, sin publicación al host.
- Alembic permaneció en `0026_user_roles (head)`.
- No se crearon migraciones y no se modificaron seeds.

## Windows Firewall

La interfaz `Tailscale` quedó en perfil `Private`. El instalador creó reglas
entrantes generales vinculadas a las direcciones del nodo. Esas dos reglas
`Tailscale-In` se deshabilitaron y se sustituyeron por el mínimo requerido para
el ERP:

| Regla | Perfil | Interfaz | Origen remoto | Protocolo | Puerto |
| --- | --- | --- | --- | --- | --- |
| Agua Activa ERP Web 3000 Tailscale | Private | Tailscale | `100.64.0.0/10` | TCP | 3000 |
| Agua Activa ERP API 8010 Tailscale | Private | Tailscale | `100.64.0.0/10` | TCP | 8010 |

Las reglas LAN anteriores siguen limitadas a `Private` y `LocalSubnet`. No
existe regla ERP para el perfil `Public` ni para el puerto 5432. La regla UDP
del proceso firmado `tailscaled.exe` se conserva porque transporta la red
Tailscale, pero se limitó también al perfil `Private`; no publica Web, API ni
PostgreSQL por sí misma.

## Evidencia técnica desde KERNELOS-PC

| Verificación | Resultado |
| --- | --- |
| Web `/login` por IPv4 Tailscale | HTTP 200 |
| API `/api/v1/health` por IPv4 Tailscale | HTTP 200 |
| Web `/login` por IP LAN después del cambio | HTTP 200 |
| API health por IP LAN después del cambio | HTTP 200 |
| Preflight CORS desde el origen Web LAN | HTTP 200 y origen exacto permitido |
| Preflight CORS desde el origen Web Tailscale | HTTP 200 y origen exacto permitido |
| Preflight desde un origen no aprobado | HTTP 400, sin `Access-Control-Allow-Origin` |
| Resolución dinámica desde Web LAN | API LAN en puerto 8010 |
| Resolución dinámica desde Web Tailscale | API Tailscale en puerto 8010 |
| Formulario LAN después del build final | Alcanzó la API y rechazó credenciales ficticias |
| Formulario Tailscale después del build final | Alcanzó la API y rechazó credenciales ficticias |
| TCP Tailscale 3000 | Accesible |
| TCP Tailscale 8010 | Accesible |
| TCP LAN 5432 | No accesible |
| TCP Tailscale 5432 | No accesible |
| Listener del host en 5432 | Ninguno |
| Tailscale Funnel | `No serve config` |
| Tailscale Serve | `No serve config` |
| Compose `config --quiet` | Aprobado |
| Alembic `current` y `heads` | `0026_user_roles (head)` |

El navegador cargó ambos formularios reales después del build final. Las
pruebas automatizadas usaron únicamente credenciales ficticias, alcanzaron la
API correspondiente y recibieron el rechazo normal. Los campos se limpiaron
al terminar. No se cambió ninguna contraseña ni se ejecutó el seed.

## Prueba final desde el iPhone de George

### Wi-Fi sin Tailscale

George confirmó el 2026-07-27 la prueba desde un iPhone conectado al Wi-Fi de
Agua Activa y con Tailscale apagado:

- Login LAN: aprobado.
- Dashboard LAN: aprobado.
- Pantalla operativa LAN: aprobada.

### Datos móviles con Tailscale

George confirmó el 2026-07-27 la prueba desde el mismo iPhone usando datos
móviles y Tailscale activo:

- API health por la IPv4 Tailscale: aprobada.
- Web `/login`: aprobada.
- Login con la cuenta vigente `admin_auditor`: aprobado.
- `/dashboard`: aprobado.
- `/dashboard/management`: aprobado.
- `/dashboard/exports`: aprobado.
- Al desactivar Tailscale en el iPhone, el ERP dejó de responder: aprobado.

Esta evidencia confirma que el acceso remoto depende del tailnet privado, que
no existe un camino equivalente desde Internet sin Tailscale y que la selección
dinámica de API conserva el acceso local por LAN.

## Ausencia de exposición pública

- `tailscale funnel status` y `tailscale serve status` devolvieron
  `No serve config`.
- No se configuró Tailscale Funnel.
- No se configuraron subnet router ni exit node.
- No se abrió ni administró el router.
- No se creó port forwarding, DMZ, dominio, IP pública ni HTTPS público.
- Las reglas ERP de Windows Firewall no usan el perfil `Public`.
- PostgreSQL no se publicó en Docker, no tiene listener en el host y no
  respondió en 5432 por la IPv4 Tailscale.

La prueba negativa desde Internet sin Tailscale fue confirmada desde el iPhone:
al apagar Tailscale usando datos móviles, el ERP dejó de responder.

## Manejo de credenciales

Durante el diagnóstico inicial, una herramienta del navegador mostró
temporalmente el valor del campo de contraseña de bootstrap en la salida de la
sesión. El valor no se reproduce aquí, no se escribió en el repositorio y no
autenticó contra la base vigente. Los campos se limpiaron inmediatamente. No se
documentan valores de credenciales. Se mantiene pendiente rotar las contraseñas
de `admin` y `operator` antes de producción.

## Pendientes

- Crear la reserva DHCP antes del piloto, sin configurar port forwarding.
- Rotar las contraseñas de `admin` y `operator` antes de producción.
- Implementar backup automático, retención, checksum, cifrado y copia externa.
- Demostrar la restauración en un ambiente aislado.
- Preparar los scripts PowerShell operativos en su bloque correspondiente.
- Ejecutar el piloto paralelo cuando sus prerrequisitos estén aprobados.

## Conclusión

**Acceso dual LAN + Tailscale listo para prueba controlada.**

La instalación, conexión del nodo, build dinámico, Web, API, login remoto,
dashboard, panel gerencial, exportaciones, CORS, firewall, ausencia de Funnel y
cierre de PostgreSQL quedaron comprobados. El iPhone también aprobó login,
dashboard y pantalla operativa por Wi-Fi/LAN con Tailscale apagado. Esto no
declara la PC como servidor oficial ni cierra los pendientes de preproducción.
