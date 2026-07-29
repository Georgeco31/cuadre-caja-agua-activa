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

## Estado del Bloque 58D

El código actual aprobó 42 pruebas específicas de permisos, la suite backend de
972 casos, typecheck, build de 38 rutas y el recorrido visual de ambos roles.
`admin_auditor` conservó 33 destinos y `operator` mostró 22. También aprobaron
URLs directas, cierre de caja con corrección posterior denegada, Excel/PDF y
los cuatro viewports.

El health productivo aprobó sin fallos: Docker healthy, LAN y Tailscale
responden, Alembic continúa en `0026_user_roles` y PostgreSQL 5432 no está
publicado. 58D detectó que las imágenes productivas no correspondían al código
validado: una instancia desechable de la imagen API permitió lecturas de
empleados y nómina al operador y la imagen web no contenía el bloqueo compilado
de 58C.

George autorizó 58D-2. Se creó y verificó un backup manual, se reconstruyeron
`api` y `web` sin borrar volúmenes, y el smoke productivo backend aprobó 26/26
comprobaciones. El operador ahora recibe `403` real en empleados, nómina,
usuarios, precios, gerencia, exportaciones, correcciones y anulaciones; conserva
`200` en los módulos operativos. Excel y PDF administrativos devolvieron `200`.
La imagen web nueva contiene el bloqueo compilado de 58C. George completó los
inicios de sesión reales sin compartir ni modificar credenciales. El recorrido
visual productivo aprobó 33 destinos para `admin_auditor`, 22 para `operator`,
las siete URLs restringidas, módulos permitidos, Excel/PDF y los cuatro
viewports sin desbordamiento horizontal. 58D queda aprobado sin reserva por
deriva de despliegue.

La evidencia y la guía interna están en:

- [`41-bloque-58d-pruebas-integrales-permisos.md`](41-bloque-58d-pruebas-integrales-permisos.md);
- [`42-guia-operativa-permisos-usuarios.md`](42-guia-operativa-permisos-usuarios.md).

## Estado del Bloque 59A

El Bloque 59A deja preparada la documentación para un piloto interno paralelo
de cinco días. Define alcance, responsabilidades, conciliación diaria,
incidencias, criterios de éxito y reglas de pausa o detención. No cambia
código, datos, permisos, credenciales ni infraestructura y no inicia el piloto.

Antes del Día 1 continúan como bloqueadores explícitos:

- confirmar el primer backup diario realmente desatendido;
- rotar las contraseñas definitivas de `admin_auditor` y `operator`;
- confirmar usuarios reales, activos, individuales y sin cuentas compartidas;
- configurar la reserva DHCP;
- confirmar que KERNELOS-PC permanecerá encendida y que Docker Desktop inicia;
- probar el acceso de la secretaria desde su equipo real;
- probar el acceso de George por Tailscale;
- completar el Día 0 y registrar la autorización de George.

La lista completa y las guías de ejecución están en:

- [`43-preparacion-piloto-interno.md`](43-preparacion-piloto-interno.md);
- [`44-guia-piloto-secretaria-operador.md`](44-guia-piloto-secretaria-operador.md);
- [`45-guia-piloto-george-admin.md`](45-guia-piloto-george-admin.md);
- [`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md);
- [`47-plan-piloto-5-dias.md`](47-plan-piloto-5-dias.md).

## Estado del Bloque 59B

El corte operativo del 2026-07-28 verificó la infraestructura sin iniciar el
piloto ni modificar código o datos:

- `db`, `api` y `web` están `healthy`;
- API y Web responden por LAN y Tailscale desde KERNELOS-PC;
- PostgreSQL `5432` no está publicado;
- Alembic continúa en `0026_user_roles`;
- `admin` está activo con rol `admin_auditor`;
- `estherdelgado31` está activa con rol `operator`;
- el backup existente más reciente tiene checksum y metadata válidos y aprobó
  `pg_restore --list`;
- la tarea `AguaActivaERP-BackupDiario` existe, pero su última ejecución
  desatendida terminó con resultado `1`.

La decisión es **no listo**. Continúan como bloqueadores las contraseñas
definitivas, la prueba desatendida con resultado `0`, las confirmaciones de
cuentas personales y servidor, los recorridos actuales desde los dispositivos
reales, DHCP o su aceptación temporal expresa, y la firma del Día 0.

Evidencia y checklist:

- [`48-cierre-pendientes-pre-piloto.md`](48-cierre-pendientes-pre-piloto.md);
- [`49-checklist-dia-0-piloto.md`](49-checklist-dia-0-piloto.md).

## Estado del Bloque 59C

El diagnóstico correlacionó la ejecución fallida de las 23:30:30 con el apagado
del backend de Docker a las 23:28:06 y un error de conexión al motor a las
23:30:01. La tarea no tenía reintentos y el script no conservaba logs.

La corrección añadió directorio de inicio absoluto, `StartWhenAvailable`, tres
reintentos cada cinco minutos y un log seguro por ejecución en `backups/logs`.
La prueba manual del script y la prueba mediante `Start-ScheduledTask` crearon
juegos independientes `.dump`, `.sha256` y `.json`; ambos aprobaron checksum y
`pg_restore --list`. La tarea terminó con `LastTaskResult = 0` y producción
permaneció saludable.

El bloqueador técnico del resultado `1` queda resuelto. Siguen pendientes el
seguimiento del siguiente disparador natural, copia externa, retención y
alertas. La evidencia está en
[`50-diagnostico-backup-diario-desatendido.md`](50-diagnostico-backup-diario-desatendido.md).

## Estado del Bloque 59D

El corte de usuarios y accesos pre-piloto reconfirmó sin consultar hashes ni
secretos:

- `admin` activo con rol `admin_auditor`;
- `estherdelgado31` activa con rol `operator`;
- producción saludable por localhost, LAN y Tailscale;
- Alembic en `0026_user_roles` y PostgreSQL `5432` no publicado;
- `KERNELOS-PC` como host comprobado, Docker disponible y suspensión con
  corriente alterna configurada en `Nunca`;
- tarea `AguaActivaERP-BackupDiario` en `Ready`, última ejecución
  2026-07-28 06:41:41, `LastTaskResult = 0` y siguiente ejecución
  2026-07-28 23:30:30.

George autorizó y completó la rotación segura de ambas credenciales, confirmó
las pruebas reales por LAN y Tailscale, designó `KERNELOS-PC` como servidor,
confirmó Docker y el método manual paralelo, y aceptó temporalmente el riesgo
DHCP mientras la reserva continúa pendiente.

George confirmó después la titularidad y uso exclusivo de las cuentas, el login
posterior de cada titular y los responsables de servidor, conciliación,
incidencias y backup.

La decisión final 59D es **listo con reservas para piloto controlado** por el
riesgo DHCP aceptado temporalmente. La reserva DHCP continúa pendiente y el
piloto no se inició; el comienzo efectivo del Día 1 corresponde al bloque
siguiente. Evidencia y checklist:

- [`51-usuarios-accesos-pre-piloto.md`](51-usuarios-accesos-pre-piloto.md);
- [`52-confirmacion-dia-0-pre-piloto.md`](52-confirmacion-dia-0-pre-piloto.md).

## Estado del Bloque 60A

George autorizó el inicio controlado del piloto Día 1 el 2026-07-28. El control
de apertura aprobó:

- health productivo con cero fallos y advertencias;
- LAN en `192.168.100.220`;
- `db`, `api` y `web` saludables;
- Alembic `0026_user_roles`;
- PostgreSQL `5432` no publicado;
- tarea `AguaActivaERP-BackupDiario` en `Ready`;
- `LastTaskResult = 0` y backup reciente con `.dump`, `.sha256` y `.json`;
- método manual actual disponible en paralelo.

El piloto queda iniciado, pero Codex no ingresó datos del negocio. La operación,
los módulos usados, las incidencias y el cierre del Día 1 se registran en
[`53-piloto-dia-1-inicio-controlado.md`](53-piloto-dia-1-inicio-controlado.md).
La reserva DHCP sigue activa y no se declara producción definitiva.

## Estado del Bloque 60C

La necesidad operativa de corregir fechas de ventas reales quedó cubierta en
el workspace con una acción exclusiva de `admin_auditor`, motivo obligatorio,
auditoría dedicada y bloqueos de anulaciones, cierres de ruta y cierres de caja.
Contado y crédito comparten el mismo endpoint y conservan identidad, cliente,
partidas, montos, pagos y estado.

La migración `0027_sale_date_corrections` pasó upgrade, downgrade y segundo
upgrade en PostgreSQL temporal aislado. En el Bloque 60C-2 también se comprobó
el backup, se migró producción a `0027_sale_date_corrections` y se recrearon
solo `api` y `web`; PostgreSQL no se reinició y los conteos quedaron intactos.
Permanecen pendientes la comprobación visual productiva por rol y una
corrección real expresamente autorizada, auditada y conciliada. Ver
[`55-bloque-60c-correccion-fecha-ventas.md`](55-bloque-60c-correccion-fecha-ventas.md).

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
| P0-08 | 55B-1/59D | Resolver URL de API, CORS, IP/DNS y firewall LAN (comprobado desde cliente LAN; reserva DHCP pendiente con riesgo aceptado para el piloto controlado) | Infraestructura | Crítica | Login y módulos cargan desde PC cliente; origen no autorizado falla; reserva antes de producción definitiva |
| P0-09 | 55A | Definir zona `America/Guayaquil` | Desarrollo/infraestructura | Alta | Host, API y reglas de negocio usan fecha esperada antes/después de 19:00 |
| P0-10 | 56A/56C/59B/59C y posteriores | Backup manual y tarea diaria comprobados; 59C resolvió el resultado `1` con `LastTaskResult = 0`, log seguro y reintentos; faltan seguimiento sostenido, retención, cifrado, alertas y copia externa | Infraestructura + George | Crítica | Ejecución diaria comprobada de forma sostenida y alerta de fallo |
| P0-11 | 56B | Restauración real en ambiente aislado (demostrada; faltan pruebas integrales de login y muestras) | Infraestructura + George | Crítica | Restore, tablas, conteos, Alembic, health y cleanup aprobados; login y muestras pasan en pruebas integrales |
| P0-12 | 55B | Manual de recuperación y responsables | George + infraestructura | Alta | Documento puede seguirse de principio a fin y registra RPO/RTO |
| P0-13 | 58D-2 | Sincronizar las imágenes productivas con las protecciones 58B y el frontend 58C (cerrado) | Desarrollo + George | Crítica | Aprobado: rebuild autorizado; `operator` recibe `403` en familias sensibles; dashboard 22/33, Excel/PDF, LAN, Tailscale y health pasan sobre las imágenes nuevas |

## Correcciones recomendadas antes del piloto

| ID | Bloque sugerido | Corrección | Responsable | Prioridad | Criterio de cierre |
| --- | --- | --- | --- | --- | --- |
| P1-01 | 54/58C | Centralizar guardas y sesión frontend (avance: rutas administrativas del dashboard usan una política y un `layout` común) | Desarrollo | Alta | Todas las rutas usan un único mecanismo y pruebas cubren 401/403 |
| P1-02 | 58C/58D-2 | Limitar navegación según rol (implementado y validado en producción) | Desarrollo | Alta | Aprobado: operator solo ve módulos permitidos; backend sigue siendo autoridad |
| P1-03 | 54/55A | Rate limit y registro de intentos de login | Desarrollo | Alta | Intentos excesivos se limitan sin bloquear operación legítima |
| P1-04 | 55A | Restringir documentación OpenAPI | Desarrollo | Media | `/docs` y `/openapi.json` no quedan públicos en producción |
| P1-05 | 55A | HTTPS local o acceso cifrado equivalente | Infraestructura | Alta | Credenciales/token no viajan en texto claro por red no confiable |
| P1-06 | 55A | Monitor de contenedores, health, disco y backups | Infraestructura | Alta | Fallos generan aviso útil para George |
| P1-07 | 55A | UPS y apagado limpio | George + infraestructura | Alta | Corte controlado no corrompe datos; reinicio queda documentado |
| P1-08 | 55B | Pruebas de integración PostgreSQL | Desarrollo | Alta | Locks, concurrencia, índices parciales y constraints pasan en PostgreSQL |
| P1-09 | 56/58D-2 | Smoke E2E por rol en servidor (aprobado) | Desarrollo | Media | Aprobado: login, módulos permitidos, restricciones, panel y exportaciones pasan en servidor |
| P1-10 | 56/58D/59A | Guía de secretaria preparada en el documento 44; capacitación y práctica del Día 0 pendientes | George | Alta | Operador completa flujo diario sin acceso administrativo |
| P1-11 | 60B/60B-2/60B-3/60B-4 | Anulación de ventas: corregido el lock PostgreSQL que devolvía `500`. Login remoto: corregida la llamada productiva de `buildApiUrl` que, sin `location`, usaba el fallback Tailscale en navegadores LAN; se conserva timeout, liberación del loading y errores claros. Comprobación física real pendiente | Desarrollo + George | Alta | Contado y crédito se anulan con motivo por `admin_auditor`; `operator` recibe `403`; una venta con abonos muestra `409`; login `admin_auditor`/`operator` funciona desde MacBook/iPhone por WiFi/LAN, localhost y Tailscale; el flujo real autorizado queda comprobado |
| P1-12 | 60C/60C-2 | Corrección administrativa auditada de `sale_date` para ventas reales registradas con fecha incorrecta, sin anular, duplicar ni editar otros datos. Backup y migración productiva a 0027 aprobados; falta validación operativa real por rol | Desarrollo + George | Alta | `admin_auditor` corrige contado/crédito con motivo; `operator` recibe `403`; cierres y anuladas devuelven `409`; auditoría, pagos inmutables, reportes y frontend quedan comprobados con una venta real autorizada |

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
Bloques 58A-58D: matriz, backend, frontend y código validados
  |
  v
Bloque 58D-2 aprobado: rebuild y smoke productivo integral por rol
  |
  v
Bloque 59A: checklist, guías, incidencias y plan paralelo documentados
  |
  v
Bloque 59B: corte no listo; cerrar backup, credenciales, accesos, servidor y DHCP
  |
  v
Bloque 59C: resultado 1 diagnosticado; tarea corregida y validada con resultado 0
  |
  v
Bloque 59D: cierre humano aprobado; listo con reserva DHCP, piloto no iniciado
  |
  v
Completar y firmar el Día 0 de los documentos 48, 49, 51 y 52
  |
  v
Bloque 60A: Día 1 iniciado de forma controlada; operación y cierre en documento 53
  |
  v
Continuar piloto controlado de cinco días según conciliación e incidencias
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
- el checklist 20 está completo y firmado por George;
- los pendientes obligatorios del documento 43 están cerrados;
- el Día 0 del documento 47 está aprobado por George.
