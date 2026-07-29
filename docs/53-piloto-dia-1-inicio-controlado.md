# 53 - Piloto Día 1: inicio controlado

## Objetivo

Registrar el Bloque 60A y acompañar el inicio controlado del Día 1 del piloto
de Agua Activa ERP. La operación se realiza con datos reales ingresados
exclusivamente por sus responsables y mantiene el método manual actual en
paralelo.

Este documento no reemplaza soportes del negocio, no contiene contraseñas y no
autoriza cambios técnicos, restore, eliminación de datos ni acciones fuera del
alcance aprobado.

## Estado del piloto

| Dato | Registro |
| --- | --- |
| Fecha de inicio | 2026-07-28 |
| Hora del control de apertura | 08:22, hora local (-05:00) |
| Bloque | 60A |
| Jornada | Día 1 de 5 |
| Estado | **INICIADO DE FORMA CONTROLADA** |
| Responsable general | George |
| Responsable de operación diaria | Persona de oficina con rol `operator` |
| Método paralelo | Confirmado; ERP y método manual actual |
| Producción definitiva | No declarada |

El inicio documental y técnico no significa que Codex haya ingresado datos. Los
movimientos reales solo pueden ser registrados por George o por la persona de
oficina, con sus propias cuentas y a partir de soportes reales.

## Estado técnico inicial

Comprobación realizada antes de habilitar la operación:

| Control | Resultado |
| --- | --- |
| Git al inicio | Limpio; staging vacío |
| Compose productivo | Válido |
| `db` | Activo y `healthy` |
| `api` | Activo y `healthy` |
| `web` | Activo y `healthy` |
| API localhost | OK |
| API LAN | OK |
| Web LAN | OK |
| API Tailscale | OK |
| Web Tailscale | OK |
| Alembic | `0026_user_roles` |
| PostgreSQL | Puerto `5432` no publicado |
| Resultado del health | OK; cero fallos críticos y cero advertencias |
| IP LAN usada | `192.168.100.220` |
| URL de oficina | `http://192.168.100.220:3000/login` |
| IP Tailscale | `100.121.163.126` |

No se modificó `.env.production.local`, Docker, código, permisos, migraciones,
seeds ni scripts.

## Estado del backup al abrir el Día 1

| Dato | Resultado |
| --- | --- |
| Tarea | `AguaActivaERP-BackupDiario` |
| Existe | Sí |
| Estado | `Ready` |
| Última ejecución | 2026-07-28 06:41:41 |
| `LastTaskResult` | `0` |
| Próxima ejecución | 2026-07-28 23:30:30 |
| Backup reciente | 2026-07-28 06:41 |
| `.dump` | Presente |
| `.sha256` | Presente |
| `.json` | Presente |
| Validación previa | Checksum, metadata y `pg_restore --list`, OK |

La ejecución natural de las 23:30 se revisará como control rutinario. Un
resultado distinto de `0` se registra como incidencia y bloquea la siguiente
jornada hasta diagnosticarlo.

## Usuarios del Día 1

| Cuenta | Rol | Uso autorizado | Uso real del día |
| --- | --- | --- | --- |
| `estherdelgado31` | `operator` | Ingreso de operación diaria | Registrar al cierre |
| `admin` | `admin_auditor` | Supervisión, auditoría y revisión | Registrar al cierre |

Reglas:

- cada persona usa únicamente su cuenta;
- no se comparten sesiones;
- `admin` no se usa para operación diaria;
- no se registran contraseñas, tokens ni capturas de secretos;
- el nombre del usuario que ejecutó cada flujo debe conservarse en la
  evidencia operativa.

## Módulos habilitados para el Día 1

Están habilitados únicamente cuando exista una necesidad real del día y un
soporte del negocio. La columna de uso se completa durante la jornada.

| Módulo | Condición | ¿Se usó? | Observación sin datos sensibles |
| --- | --- | --- | --- |
| Login | Obligatorio | [ ] | |
| Dashboard | Consulta inicial | [ ] | |
| Cuadre de caja | Flujo principal del Día 1 | [ ] | |
| Gastos de caja | Solo gastos reales del día | [ ] | |
| Clientes | Solo clientes necesarios del día | [ ] | |
| Ventas de contado | Si aplica | [ ] | |
| Ventas a crédito | Si aplica y el proceso real está aprobado | [ ] | |
| Cobros | Si aplica | [ ] | |
| Producción | Si aplica | [ ] | |
| Inventario `entry`/`exit` | Si aplica; sin ajustes delicados | [ ] | |

Habilitado no significa obligatorio. No se deben crear registros de prueba,
relleno o demostración.

## Módulos y acciones excluidos

- [x] Nómina.
- [x] Empleados y control laboral.
- [x] Anticipos y préstamos.
- [x] Fórmulas y costos.
- [x] Cambios de precios.
- [x] Anulaciones.
- [x] Correcciones administrativas.
- [x] Ajustes delicados de inventario.
- [x] Cambios masivos.
- [x] Administración de usuarios o permisos durante la operación.
- [x] Restore, migraciones, seeds, rebuild o `docker compose down -v`.

Una necesidad fuera de alcance se registra como incidencia y se mantiene en el
método manual. No se improvisa una excepción durante la jornada.

## Checklist antes de ingresar datos

- [x] George autorizó iniciar el Bloque 60A.
- [x] El cierre 59D quedó listo con reserva DHCP aceptada.
- [x] `KERNELOS-PC` está identificado como servidor.
- [x] Docker Desktop y los tres servicios están saludables.
- [x] La IP LAN sigue siendo `192.168.100.220`.
- [x] La Web LAN responde.
- [x] La tarea de backup está `Ready`.
- [x] `LastTaskResult = 0`.
- [x] Existe un backup reciente validado.
- [x] El método manual está disponible en paralelo.
- [x] Las cuentas personales y los roles están confirmados.
- [x] La plantilla de incidencias está disponible.
- [x] WhatsApp directo a George es el canal de aviso.
- [x] El riesgo DHCP y su criterio de detención están recordados.
- [ ] La persona operadora confirma que tiene los soportes reales del primer
  movimiento.
- [ ] George confirma la hora exacta en que comienza el primer ingreso real.

Las dos últimas casillas las completan los participantes inmediatamente antes
del primer registro. Codex no las marca ni ingresa el movimiento.

## Checklist durante la operación

- [ ] Iniciar sesión con la cuenta personal correspondiente.
- [ ] Confirmar usuario, rol y fecha antes de registrar.
- [ ] Usar únicamente un módulo habilitado.
- [ ] Registrar solo información real tomada de un soporte válido.
- [ ] Registrar el mismo período y movimiento en el método manual.
- [ ] Evitar duplicados: comprobar antes de volver a guardar.
- [ ] No usar `admin` para resolver una restricción de `operator`.
- [ ] No ejecutar anulaciones, correcciones administrativas o ajustes
  delicados.
- [ ] Registrar en este documento los módulos realmente usados.
- [ ] Avisar por WhatsApp directo a George si aparece una incidencia.
- [ ] Registrar toda incidencia importante en
  [`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md).
- [ ] No corregir a ciegas una diferencia entre ERP y método manual.
- [ ] Si cambia la IP o falla LAN, detener el ingreso y continuar con el método
  manual desde una hora de corte clara.

## Registro de módulos usados

Completar sin copiar datos personales, importes detallados ni secretos:

| Hora | Usuario | Módulo | Flujo realizado | Resultado | Referencia de incidencia |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Registro de incidencias

1. Detener únicamente el flujo afectado.
2. Mantener el método manual desde una hora de corte definida.
3. Avisar por WhatsApp directo a George.
4. Registrar la incidencia importante en
   [`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md).
5. Incluir hora, usuario, módulo, acción, resultado y efecto operativo.
6. No incluir contraseñas, tokens, hashes, contenido del entorno ni datos
   innecesarios.
7. No borrar, anular, corregir históricos ni ejecutar restore para ocultar la
   diferencia.

| Control de incidencias | Registro |
| --- | --- |
| ¿Hubo incidencias? | Completar al cierre |
| Cantidad | |
| Críticas | |
| Abiertas al cierre | |
| Referencias en documento 46 | |

## Método manual paralelo

- [x] El método manual actual permanece activo durante todo el Día 1.
- [x] El ERP no reemplaza oficialmente el método actual.
- [x] George es responsable de la conciliación diaria.
- [x] La revisión ocurre al cierre, después del cuadre de caja.
- [x] Se revisan caja, ventas, cobros, gastos, producción/inventario si aplica e
  incidencias del día.

Una diferencia no significa que el ERP sea automáticamente incorrecto. Se
conservan ambos registros, se documenta la evidencia y se analiza antes de
cambiar datos.

## Reservas activas

### DHCP

- la reserva DHCP continúa pendiente;
- George aceptó temporalmente el riesgo;
- se verifica diariamente la IP `192.168.100.220`;
- un cambio de IP o pérdida de LAN detiene el ingreso;
- cualquier actualización de configuración, firewall, CORS, URLs o
  documentación requiere un bloque controlado separado.

No resetear el router, abrir puertos ni configurar port forwarding.

### Backup

- George revisa cada mañana `LastTaskResult`;
- debe existir un backup reciente válido;
- la siguiente ejecución natural está programada para las 23:30:30;
- un fallo se registra y se diagnostica antes de la siguiente jornada;
- no se ejecuta restore durante el piloto sin un bloque separado y autorizado.

### IP y servidor

- verificar la IP LAN antes de operar;
- mantener `KERNELOS-PC` encendido;
- mantener Docker Desktop disponible;
- impedir suspensión de Windows;
- no usar `docker compose down -v`.

## Checklist de cierre del Día 1

- [ ] Registrar la hora del último ingreso.
- [ ] Cerrar o dejar en estado correcto el cuadre según el flujo real aprobado.
- [ ] Conciliar ERP y método manual.
- [ ] Revisar caja.
- [ ] Revisar ventas de contado, si se usaron.
- [ ] Revisar ventas a crédito, si se usaron.
- [ ] Revisar cobros, si se usaron.
- [ ] Revisar gastos, si se usaron.
- [ ] Revisar producción e inventario, si se usaron.
- [ ] Completar la tabla de módulos usados.
- [ ] Completar el resumen de incidencias.
- [ ] Confirmar que no quedan duplicados conocidos.
- [ ] Confirmar que no queda una diferencia material sin explicar.
- [ ] Registrar qué cuenta operó y cuál supervisó.
- [ ] Mantener el método manual disponible para el Día 2.
- [ ] Registrar la decisión de continuar, pausar o corregir antes del Día 2.

| Dato de cierre | Registro |
| --- | --- |
| Hora del último ingreso | |
| Responsable de conciliación | George |
| Resultado de conciliación | Pendiente |
| Diferencias detectadas | Pendiente |
| Incidencias | Pendiente |
| Estado del cuadre | Pendiente |
| Decisión para el Día 2 | Pendiente |
| Confirmación de George | Pendiente |

## Conclusión provisional

El Día 1 del piloto queda **INICIADO DE FORMA CONTROLADA** el 2026-07-28, con
health, IP LAN, backup, cuentas, método paralelo y reservas comprobados.

El ingreso de datos reales y el cierre de la jornada permanecen bajo
responsabilidad de George y de la persona operadora. Este documento no declara
el Día 1 cerrado, no reemplaza el método manual y no declara producción
definitiva.

## Seguimiento Bloques 60B y 60B-2

El 2026-07-29 se documentó una incidencia al intentar anular ventas de contado
y a crédito con rol `admin_auditor`: primero la interfaz mostró `Load failed` y
después el mensaje operativo de imposibilidad de contactar al servidor.

La revisión ampliada corrigió el diagnóstico inicial. El `OPTIONS` y el
`POST /api/v1/sales/{id}/void` sí llegaron al API; el `POST` devolvió `500`
porque PostgreSQL no permite aplicar `FOR UPDATE` al lado anulable de los
`LEFT JOIN` usados para cargar la venta, su carga, ruta y vehículo. El health
LAN permaneció en `200`, por lo que no era una caída general de la API.

En 60B-2 se limitó el lock a la tabla `sales` con `FOR UPDATE OF sales`. También
se centralizó la construcción de URL y el único `fetch` frontend: LAN usa el
host LAN en `8010`, Tailscale usa el host Tailscale en `8010`, localhost usa
localhost en `8010` y solo SSR conserva `NEXT_PUBLIC_API_URL`. Las descargas
Excel/PDF quedaron en el mismo camino que login, dashboard, ventas, cobros,
clientes, reportes y demás módulos.

Las 973 pruebas backend, las 7 pruebas de URL, typecheck, build y la consulta
real PostgreSQL con rollback aprobaron. Se reconstruyeron y recrearon solo
`api` y `web` con `--no-deps`; `db` mantuvo su contenedor y no se tocaron
volúmenes ni `.env.production.local`. El health posterior aprobó localhost,
LAN, Tailscale, Alembic `0026_user_roles` y PostgreSQL no publicado, sin fallos
ni advertencias.

Codex no anuló ninguna venta real. El detalle técnico y operativo está en
[`54-incidencia-60b-anulacion-ventas.md`](54-incidencia-60b-anulacion-ventas.md).
Hasta que George autorice y compruebe una operación real con
`admin_auditor`, la incidencia permanece **en revisión operativa** y el método
manual paralelo continúa activo.

## Seguimiento Bloque 60B-3

George informó que el login desde MacBook e iPhone por WiFi/LAN quedaba en
`Iniciando...`, incluso en navegación privada, mientras Web y health LAN
seguían disponibles y localhost sí funcionaba. Quedaron descartados caché,
PWA, accesos directos antiguos y caída general de red/API.

Los logs mostraron que al menos un flujo alcanzaba
`POST /api/v1/auth/login`: el preflight respondió `200`, dos intentos
respondieron `401` y un intento posterior respondió `200`, seguido de
`GET /api/v1/auth/me 200`. Como esos access logs no guardan `Origin`, no
demostraban que los intentos LAN fallidos hubieran llegado. Pruebas con
credenciales falsas confirmaron `OPTIONS 200`, `POST 401` y CORS correcto en
LAN, Tailscale y localhost. El contrato permanece JSON; no se cambió el
backend.

El frontend ahora lee los valores reales enviados por el formulario para
proteger el autorrelleno de Safari, limita login y `/auth/me` a 15 segundos,
libera siempre el botón, muestra errores accesibles y usa una navegación
completa al dashboard tras el éxito. Las pruebas, typecheck, build, prueba Web
LAN normal/móvil y health aprobaron.

Solo se recreó `web`; `api` y `db` no se reiniciaron. La comprobación física
posterior con las cuentas reales en Safari de MacBook/iPhone y por Tailscale
queda a cargo de George. El método manual paralelo continúa activo hasta esa
confirmación.

## Seguimiento Bloque 60B-4

La prueba física posterior a 60B-3 confirmó una diferencia decisiva:
localhost y Tailscale funcionaban, pero MacBook e iPhone por WiFi/LAN seguían
agotando el timeout. Navegación privada también falló. En la ventana de esos
intentos LAN no apareció el `POST /api/v1/auth/login` en el API, mientras una
sesión por Tailscale sí dejó el flujo completo de auth y dashboard.

La causa exacta estaba en el cliente central: `apiFetch` llama
`buildApiUrl(path)` sin pasar `location`, y la implementación anterior
interpretaba ese argumento ausente como contexto SSR. En consecuencia usaba el
`NEXT_PUBLIC_API_URL` compilado —Tailscale en producción— incluso dentro del
navegador. Un dispositivo LAN sin Tailscale no podía llegar a ese destino; el
servidor y los clientes Tailscale sí podían. Las pruebas anteriores habían
inyectado `location` y por eso no reproducían la llamada productiva.

`buildApiUrl` ahora consulta `window.location` cuando se invoca sin argumento
en navegador y reserva el fallback para SSR. La matriz automatizada comprueba,
mediante esa misma llamada productiva, LAN, Tailscale, localhost, `127.0.0.1`,
`::1` y SSR. No se cambió el entorno, CORS, backend, payload JSON, credenciales,
permisos ni reglas de negocio.

Aprobaron las pruebas de URL y login, typecheck, build de 38 rutas, 122 pruebas
dirigidas de permisos/anulación, preflight y `POST` falso controlado en LAN,
Tailscale y localhost. La UI servida por LAN y Tailscale mostró
`Usuario o contraseña incorrectos.`, reactivó el botón y no produjo errores de
consola. Solo se reconstruyó/recreó `web` con `--no-deps`; `api` y `db`
conservaron sus contenedores y el health final quedó correcto.

Codex no usó contraseñas reales ni anuló otra venta. La validación física final
de ambas cuentas en MacBook/iPhone por WiFi/LAN, localhost y Tailscale queda a
cargo de George. Hasta registrarla, la incidencia continúa **en revisión
operativa** y el método manual paralelo permanece activo.

## Seguimiento Bloque 60C

George identificó la necesidad de corregir la fecha de una venta real sin
anularla ni volverla a registrar. El Bloque 60C preparó una corrección
administrativa limitada a `sale_date`, disponible solo para
`admin_auditor`, con motivo obligatorio y auditoría de fecha anterior, fecha
nueva, usuario y timestamp.

La implementación conserva cliente, partidas, cantidades, precios, montos,
saldo, pagos y estado de anulación. Las ventas anuladas y las fechas o cargas
ligadas a cierres se bloquean con `409`. Los reportes consultan la nueva fecha
y los pagos conservan sus propias fechas.

En el Bloque 60C-2 se creó y comprobó el backup previo, se construyeron y
recrearon solo `api` y `web`, y se aplicó la migración
`0027_sale_date_corrections` sin reiniciar PostgreSQL ni cambiar conteos del
negocio. El health posterior aprobó localhost, LAN y Tailscale; la tabla de
auditoría quedó creada y vacía.

Codex no corrigió ninguna venta real. Permanecen pendientes la comprobación
visual productiva con sesiones `admin_auditor`/`operator` y una corrección real
expresamente autorizada, conciliada contra auditoría y reportes. El detalle
está en
[`55-bloque-60c-correccion-fecha-ventas.md`](55-bloque-60c-correccion-fecha-ventas.md).

## Seguimiento Bloque 60D

Durante la preparación de producción y rutas, George intentó cargar un camión y
el sistema no encontró stock disponible en la ubicación de origen. El rechazo
es la protección esperada: una carga traslada inventario de bodega hacia un
vehículo y no puede crear producto.

La regla queda incorporada al piloto:

> No cargar un carro hasta contar, registrar y comprobar el stock disponible
> en la ubicación de origen.

El corte técnico del 2026-07-29 confirmó Compose válido, `db`, `api` y `web`
saludables, acceso localhost/LAN/Tailscale, Alembic
`0027_sale_date_corrections` y PostgreSQL 5432 no publicado. También aprobaron
342 pruebas dirigidas de inventario, producción, fórmulas, consumo, cargas,
retornos, cierres, permisos y reportes. No se modificó código ni se ingresaron
datos del negocio.

La auditoría confirmó:

- `operator` puede registrar producción y movimientos `entry`/`exit` sin costo;
- aplicar producción, consumir insumos, cargar vehículos, registrar retornos,
  ajustar y anular siguen bajo `admin_auditor`;
- registrar producción no aumenta stock ni consume insumos;
- consumo y aplicación son confirmaciones explícitas e independientes;
- la carga rechaza de forma atómica cantidades mayores al stock;
- el retorno mueve sobrante del vehículo a una ubicación no vehicular;
- las ventas asociadas a carga no descuentan inventario del vehículo;
- el cierre de ruta es financiero y todavía no liquida físicamente
  carga − venta − retorno;
- el bidón retornable requiere un control separado del consumo de tapas,
  sellos o etiquetas.

Antes de incorporar este flujo al piloto se debe completar el Día 0 y obtener
la autorización de George. Documentos de ejecución:

- [`56-preparacion-produccion-inventario-agosto.md`](56-preparacion-produccion-inventario-agosto.md):
  auditoría, reglas, flujo y brechas;
- [`57-checklist-stock-inicial-agosto.md`](57-checklist-stock-inicial-agosto.md):
  conteo físico y registro de apertura;
- [`58-guia-produccion-inventario-operador.md`](58-guia-produccion-inventario-operador.md):
  instrucciones para la persona operadora;
- [`59-plan-arranque-agosto-produccion-inventario.md`](59-plan-arranque-agosto-produccion-inventario.md):
  Día 0 y cinco jornadas de validación.

El stock inicial recomendado se registra con movimientos `entry`, una fila por
producto y ubicación, usando el motivo
`Stock inicial agosto 2026 - conteo físico`. Las cantidades deben provenir de
la hoja firmada; Codex no las registra ni las estima.
