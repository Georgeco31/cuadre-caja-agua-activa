# 21 - Plan de correcciones preproducción

## Objetivo

Cerrar de forma verificable los riesgos encontrados en el Bloque 53 sin
mezclar cambios de negocio, infraestructura y recuperación en un solo paso.

## Estado del Bloque 54

El bloqueador base de roles quedó resuelto en código:

- [x] `operator` y `admin_auditor` definidos.
- [x] Usuarios existentes migran a `admin_auditor`.
- [x] Administración de cuentas personales protegida en backend.
- [x] Correcciones, anulaciones, precios, panel y exportaciones críticas
  protegidas con `403`.
- [x] Navegación y botones críticos limitados según rol.
- [x] No se puede desactivar o degradar al último administrador activo.
- [x] Suite backend, typecheck, build y migración local validados.

Esto no cierra los riesgos de servidor, red, backups, restore, auditoría
avanzada ni piloto. La matriz vigente está en
[`22-matriz-permisos-roles.md`](22-matriz-permisos-roles.md).

## Estado de los Bloques 55A y 55A-2

El repositorio ya contiene Compose productivo separado, Dockerfiles
productivos, plantilla de variables sin secretos, healthchecks, rotación de
logs y scripts seguros de arranque, health, logs y apagado. PostgreSQL no
publica 5432, la API no usa reload y la Web no usa el servidor de desarrollo.

La construcción, health, persistencia, migración `0026_user_roles`, login,
panel y exportaciones fueron probados en KERNELOS-PC. P0-05 queda comprobado
para esta prueba controlada. P0-06 mantiene pendiente únicamente la prueba
negativa de `5432` desde otro equipo de la red. La evidencia está en
[`24-prueba-docker-produccion-pc.md`](24-prueba-docker-produccion-pc.md).

## Estado del Bloque 55B-1

KERNELOS-PC usa la IPv4 privada `192.168.100.220` en Ethernet. La interfaz quedó
en perfil `Private`; Web y API se publican en 3000 y 8010 con reglas de Windows
Firewall limitadas a `Private` y `LocalSubnet`. CORS y
`NEXT_PUBLIC_API_URL` usan la IP LAN, Web fue reconstruida, health y login
funcionan desde la propia PC usando esa IP y PostgreSQL sigue sin publicar
5432.

La prueba desde otro dispositivo LAN fue confirmada como exitosa usando
`192.168.100.220`, por lo que P0-08 queda resuelto para la prueba controlada.
La reserva DHCP está pendiente porque no se tienen las credenciales del router
y debe configurarse antes del piloto, directamente o mediante el
proveedor/técnico. También queda pendiente confirmar desde otro equipo que
`5432` no es accesible. En este bloque no se configuraron Tailscale, port
forwarding, backups, restauración ni piloto. La evidencia está en
[`25-red-local-firewall-pc.md`](25-red-local-firewall-pc.md).

## Estado de los Bloques 55B-2 y 55B-2A

Tailscale 1.98.9 fue instalado en KERNELOS-PC desde el paquete estable oficial,
con checksum y firma digital comprobados. El nodo `kernelos-pc` está conectado
bajo la cuenta controlada por George y recibió una IPv4 privada Tailscale. Web y
API responden por esa dirección, el origen CORS exacto está permitido y Web fue
reconstruida con la nueva `NEXT_PUBLIC_API_URL`.

Las reglas entrantes generales que el instalador creó para las direcciones
Tailscale fueron deshabilitadas. El ERP solo permite TCP 3000 y 8010 por la
interfaz `Tailscale`, perfil `Private` y rango privado `100.64.0.0/10`.
PostgreSQL no publica 5432 y ese puerto no respondió por Tailscale. Funnel y
Serve no tienen configuración; no se tocaron router, port forwarding, subnet
router ni exit node.

George confirmó desde su iPhone con datos móviles el health, login
`admin_auditor`, dashboard, panel gerencial y exportaciones por Tailscale. Al
apagar Tailscale, el ERP dejó de responder.

La primera configuración reveló que una única `NEXT_PUBLIC_API_URL` compilada
rompía el acceso LAN sin Tailscale. El frontend ahora resuelve la API por el
hostname actual: LAN usa `192.168.100.220:8010` y Tailscale usa
`100.121.163.126:8010`, incluido el flujo de exportaciones. Typecheck, build,
Compose, CORS y pruebas de formulario por ambos hostnames aprobaron. George
confirmó desde el iPhone por Wi-Fi, con Tailscale apagado, el login, dashboard y
una pantalla operativa por LAN. El acceso dual LAN + Tailscale queda listo para
prueba controlada. La evidencia está en
[`26-tailscale-acceso-remoto-privado.md`](26-tailscale-acceso-remoto-privado.md).

## Estado del Bloque 55C

KERNELOS-PC dispone de scripts PowerShell nativos para iniciar, apagar sin
borrar datos, consultar health, logs y estado, y reconstruir después de una
actualización. La migración queda en un script separado que advierte sobre el
backup y no ejecuta seeds. Los scripts `.sh` continúan para macOS/Linux, pero
Windows ya no depende de WSL para la operación diaria.

El procedimiento, los accesos directos y los comandos prohibidos están en
[`27-scripts-powershell-servidor-local.md`](27-scripts-powershell-servidor-local.md).
Este bloque no implementa backups, restauración, tareas programadas, watchdog,
monitoreo externo ni piloto.

## Estado del Bloque 56A

El backup manual de PostgreSQL queda implementado en Windows con formato custom,
timestamp, tamaño, SHA256, metadata sin secretos y validación mediante
`pg_restore --list`. El dump se crea dentro de `db` y se copia al host sin
streaming binario de PowerShell.

También quedan preparados los scripts para registrar, consultar y quitar una
tarea diaria de Windows. El modo `-WhatIf` permite revisar el registro sin
modificar Task Scheduler; la tarea real no se registra sin aprobación. No se
implementan retención, copia externa automática, alertas, cifrado avanzado ni
restauración. El procedimiento está en
[`28-backups-postgresql-windows.md`](28-backups-postgresql-windows.md).

## Estado del Bloque 56B

La restauración real del backup
`agua-activa-postgres-20260727-133213.dump` quedó demostrada en un contenedor
`postgres:16-alpine` temporal y desechable. El contenedor no tuvo red, puertos
publicados ni volumen Docker, y nunca usó el servicio o volumen productivo.

SHA256, `pg_restore --list`, restore, Alembic `0026_user_roles`, 13 tablas
principales y conteos numéricos aprobaron. `db`, `api` y `web` permanecieron
healthy, PostgreSQL 5432 siguió sin publicarse y el contenedor temporal fue
eliminado. La evidencia segura está ignorada por Git y el procedimiento está en
[`29-restauracion-controlada-postgresql.md`](29-restauracion-controlada-postgresql.md).

Esto cierra la restauración demostrada del alcance 56B. Al cierre específico de
ese bloque, la tarea diaria de backup, las pruebas integrales y el piloto
continuaban pendientes.

## Estado del Bloque 56C

La tarea de Windows `AguaActivaERP-BackupDiario` quedó registrada en
KERNELOS-PC con disparador diario a las 23:30 y acción absoluta sobre
`scripts/prod-local-backup-db.ps1`. Usa el usuario interactivo con nivel
limitado y no almacena contraseñas.

El inicio manual controlado de la tarea terminó con resultado `0` y generó
`agua-activa-postgres-20260727-140219.dump`, su SHA256 y su metadata segura.
El hash coincidió, `pg_restore --list` aprobó tanto en la ejecución como en una
validación independiente, Alembic siguió en `0026_user_roles` y producción
permaneció saludable por LAN y Tailscale, sin publicar PostgreSQL 5432. La
evidencia está en
[`30-backup-diario-programado-windows.md`](30-backup-diario-programado-windows.md).

Esto activa y verifica operativamente la tarea diaria. Continúan pendientes la
copia externa periódica, retención, alertas, monitoreo, pruebas integrales y el
piloto.

## Estado del Bloque 58A

La matriz granular propuesta para `operator` quedó documentada, sin cambios de
código, datos, autenticación ni permisos efectivos. El inventario separa
guardas frontend, autorización backend y capacidades que hoy continúan abiertas
para ambos roles.

George resolvió las diez decisiones principales. El operador podrá cerrar caja,
registrar producción diaria y crear movimientos operativos `entry`/`exit` con
trazabilidad. Correcciones, anulaciones, precios, descargas, gerencia,
configuración crítica e inventario de ajuste quedan en administrador. La
gestión de empleados, anticipos, préstamos y nómina también será exclusiva de
`admin_auditor`.

Los asuntos no respondidos se clasifican como pendientes futuros y deben
denegarse a `operator` en 58B. La política, los riesgos y la secuencia 58B a 58E
están en
[`38-matriz-permisos-operador.md`](38-matriz-permisos-operador.md).

## Estado de los Bloques 58B y 58C

58B convirtió la matriz aprobada en protección backend efectiva. Las acciones
críticas del operador responden `403`, 42 pruebas específicas por rol pasaron y
la suite backend completa quedó en 972 pruebas aprobadas.

58C alineó el frontend con esa política sin cambiar backend, endpoints,
payloads, cálculos, autenticación ni roles. El operador conserva caja y cierre
diario, clientes, ventas, cobros, producción diaria e inventario
`entry`/`exit` sin costo. La interfaz retira sus accesos y controles de
correcciones, anulaciones, precios, gerencia, exportaciones, usuarios,
empleados/nómina, fórmulas, consumo de insumos, ajustes y costos.

El dashboard muestra 33 destinos para `admin_auditor` y 22 para `operator`. La
guarda común del dashboard bloquea también la navegación directa a pantallas
administrativas con un mensaje no técnico; el backend sigue siendo la frontera
de seguridad. Typecheck, build, Compose y el recorrido manual de ambos roles
aprobaron. La evidencia está en
[`40-bloque-58c-frontend-permisos-operador.md`](40-bloque-58c-frontend-permisos-operador.md).

## Correcciones obligatorias antes de producción

| ID | Bloque sugerido | Corrección | Responsable | Prioridad | Criterio de cierre |
| --- | --- | --- | --- | --- | --- |
| P0-01 | 54 | Roles `operator` y `admin_auditor`, cuentas personales y permisos backend | Desarrollo + George | Crítica | Matriz aprobada; pruebas permiten/deniegan cada grupo; secretaria no usa admin |
| P0-02 | 54 | Auditoría de acciones por usuario para correcciones/anulaciones críticas | Desarrollo | Crítica | Cada acción conserva usuario y motivo; pruebas lo verifican |
| P0-03 | 54 | Migración de roles revisada manualmente | Desarrollo | Crítica | Upgrade/downgrade aislados; diff no elimina índices/constraints históricos |
| P0-04 | 54B | Reconciliar deuda Alembic en bloque dedicado | Desarrollo | Alta | `alembic check` limpio o baseline de excepciones explícito y aprobado |
| P0-05 | 55A/55A-2 | Compose productivo endurecido (comprobado en KERNELOS-PC para prueba controlada) | Desarrollo/infraestructura | Crítica | Sin reload/dev; restart, healthchecks, logs, usuarios y volumen verificados en PC |
| P0-06 | 55A/55A-2/55B-1 | Retirar exposición de PostgreSQL (sin `ports`; sin listener en host; pendiente prueba desde otro equipo) | Infraestructura | Crítica | `5432` no accesible desde otro equipo; API sí conecta internamente |
| P0-07 | 55A | Rotar contraseña PostgreSQL y secretos productivos | George + infraestructura | Crítica | No hay defaults; health/login pasan; secretos no se publican |
| P0-08 | 55B-1 | Resolver URL de API, CORS, IP/DNS y firewall LAN (comprobado desde cliente LAN; reserva DHCP pendiente antes del piloto) | Infraestructura | Crítica | Login y módulos cargan desde PC cliente; origen no autorizado falla |
| P0-09 | 55A | Definir zona `America/Guayaquil` | Desarrollo/infraestructura | Alta | Host, API y reglas de negocio usan fecha esperada antes/después de 19:00 |
| P0-10 | 56A/56C y posteriores | Backup manual comprobado y tarea diaria registrada con inicio manual exitoso; faltan seguimiento de ejecuciones desatendidas, retención, cifrado, alertas y copia externa | Infraestructura + George | Crítica | Ejecución diaria comprobada de forma sostenida y alerta de fallo |
| P0-11 | 56B | Restauración real en ambiente aislado (demostrada; faltan pruebas integrales de login y muestras) | Infraestructura + George | Crítica | Restore, tablas, conteos, Alembic, health y cleanup aprobados; login y muestras pasan en pruebas integrales |
| P0-12 | 55B | Manual de recuperación y responsables | George + infraestructura | Alta | Documento puede seguirse de principio a fin y registra RPO/RTO |

## Correcciones recomendadas antes del piloto

| ID | Bloque sugerido | Corrección | Responsable | Prioridad | Criterio de cierre |
| --- | --- | --- | --- | --- | --- |
| P1-01 | 54/58C | Centralizar guardas y sesión frontend (avance: rutas administrativas del dashboard usan una política y un `layout` común) | Desarrollo | Alta | Todas las rutas usan un único mecanismo y pruebas cubren 401/403 |
| P1-02 | 58C | Limitar navegación según rol (implementado) | Desarrollo | Alta | Operator solo ve módulos permitidos; backend sigue siendo autoridad |
| P1-03 | 54/55A | Rate limit y registro de intentos de login | Desarrollo | Alta | Intentos excesivos se limitan sin bloquear operación legítima |
| P1-04 | 55A | Restringir documentación OpenAPI | Desarrollo | Media | `/docs` y `/openapi.json` no quedan públicos en producción |
| P1-05 | 55A | HTTPS local o acceso cifrado equivalente | Infraestructura | Alta | Credenciales/token no viajan en texto claro por red no confiable |
| P1-06 | 55A | Monitor de contenedores, health, disco y backups | Infraestructura | Alta | Fallos generan aviso útil para George |
| P1-07 | 55A | UPS y apagado limpio | George + infraestructura | Alta | Corte controlado no corrompe datos; reinicio queda documentado |
| P1-08 | 55B | Pruebas de integración PostgreSQL | Desarrollo | Alta | Locks, concurrencia, índices parciales y constraints pasan en PostgreSQL |
| P1-09 | 56 | Smoke E2E | Desarrollo | Media | Login, caja, historial, panel y exportaciones pasan en servidor |
| P1-10 | 56 | Capacitación y guía de secretaria | George | Alta | Operador completa flujo diario sin acceso administrativo |

## Mejoras que pueden esperar

| ID | Bloque sugerido | Mejora | Responsable | Criterio de cierre |
| --- | --- | --- | --- | --- |
| P2-01 | Postpiloto | Dividir `apps/web/lib/api.ts` por dominios | Desarrollo | Clientes API pequeños y sin cambio funcional |
| P2-02 | Postpiloto | Dividir páginas de más de 1.000 líneas | Desarrollo | Componentes/hooks extraídos con typecheck/build |
| P2-03 | Postpiloto | Dividir servicios Excel/PDF | Desarrollo | Generadores reutilizables y pruebas equivalentes |
| P2-04 | Postpiloto | Auditoría general de cambios de maestros | Desarrollo + George | Historial consultable por usuario, fecha y entidad |
| P2-05 | Mantenimiento | Resolver warning TestClient/httpx | Desarrollo | Suite sin warning y sin salto de versiones no probado |
| P2-06 | Mantenimiento | Pipeline CI y escaneo de dependencias | Desarrollo | Pruebas y build automáticos por rama/PR |
| P2-07 | Postpiloto | Evaluar cookies seguras y refresh tokens | Desarrollo | Decisión documentada y amenaza XSS/CSRF considerada |
| P2-08 | Postpiloto | Métricas y logs estructurados | Desarrollo/infraestructura | Incidentes trazables sin secretos |

## Secuencia propuesta

```text
Bloque 53 aprobado
  |
  v
Bloque 54: roles, cuentas y permisos
  |
  +--> revisión manual de su migración
  v
Bloque 54B: reconciliación Alembic controlada
  |
  v
Bloque 55A: servidor, red, zona horaria y seguridad Docker
  |
  v
Bloque 56A: backup manual y preparación de tarea diaria
  |
  v
Bloque 56B aprobado: restore aislado demostrado
  |
  v
Bloque 56C aprobado: backup diario registrado y prueba manual exitosa
  |
  v
Pruebas integrales, retención, copia externa y monitoreo
  |
  v
Piloto controlado, solo después de cerrar los pendientes
```

## Guardas obligatorias para el Bloque 54

1. Crear backup antes de aplicar la migración en cualquier base relevante.
2. Ejecutar `alembic heads` y `alembic current`.
3. No aceptar automáticamente la salida de autogenerate.
4. Revisar que el archivo solo incluya tablas/columnas/constraints de usuarios,
   roles o permisos aprobados.
5. Rechazar cualquier `drop_index`, `drop_constraint` o modificación de
   ventas/rutas/gastos/nómina no relacionada.
6. Probar upgrade y downgrade en base desechable.
7. Probar roles contra PostgreSQL.
8. Volver a ejecutar las 917 pruebas, typecheck y build.

## Matriz mínima aprobada para preparar 58B

El detalle de decisiones oficiales, trazabilidad y pendientes futuros está en
el documento 38:

| Capacidad | Operator | Admin-auditor |
| --- | --- | --- |
| Login y dashboard operativo | Sí | Sí |
| Caja abierta: conteo y gastos | Sí, con trazabilidad | Sí |
| Cierre de cuadre diario | Sí, con trazabilidad | Sí |
| Historial de caja | Lectura | Lectura |
| Correcciones de cuadre cerrado | No | Sí |
| Venta de contado | Sí, con trazabilidad | Sí |
| Anular ventas o cobros | No | Sí |
| Cambiar precios | No | Sí |
| Inventario `entry`/`exit` | Sí, con trazabilidad y sin cambiar costos | Sí |
| Ajustar o anular inventario | No | Sí |
| Registrar producción diaria | Sí, con trazabilidad | Sí |
| Aplicar producción o consumir insumos | Pendiente futuro; denegado en 58B | Sí |
| Gestionar empleados, anticipos, préstamos o nómina | No | Sí |
| Panel gerencial | No | Sí |
| Excel/PDF | No | Sí |
| Usuarios, roles y configuración | No | Sí |

## Criterio final de preproducción

La preproducción queda cerrada cuando:

- no quedan hallazgos críticos abiertos;
- los permisos se prueban en backend;
- PostgreSQL no es accesible desde la red;
- la aplicación funciona desde un PC cliente autorizado;
- fecha/hora reflejan Ecuador;
- backup automático y restore aislado están aprobados;
- pruebas y build pasan desde el commit etiquetado;
- el checklist 20 está completo y firmado por George.
