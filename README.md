# Agua Activa ERP

Aplicacion web responsive y modular para la operacion interna del negocio Agua Activa.

El proyecto inicio como un sistema para ordenar el cierre de caja diario mediante el registro de monedas, billetes, gastos realizados con dinero de caja, totales calculados, cierre diario, historial, correcciones y resumen acumulado.

A partir del Bloque 23, el proyecto evoluciona estrategicamente hacia **Agua Activa ERP**, un sistema interno modular para controlar produccion, inventario, ventas, caja, rutas, empleados, compras, camiones y rentabilidad. El modulo actual de caja se mantiene como el primer modulo funcional del ERP y no se elimina.

En esta etapa ya existe backend FastAPI con autenticacion JWT, frontend Next.js protegido, modulo operativo de caja, modulos base de clientes, productos, empleados, rutas, vehiculos y proveedores, control administrativo de asistencia, anticipos y préstamos de empleados, roles de pago base, registro comercial de ventas de contado y a credito, cartera de cobros y cuentas por cobrar, inventario base, produccion, formulas con insumos y costos estimados, consumo controlado y reversible de insumos, carga y retorno de camion, consulta de actividad comercial, cierre financiero asociado a una ruta, compras administrativas, listas de precios, gastos operativos generales, reportes diarios y mensuales, un panel gerencial base y exportaciones autenticadas de solo lectura en Excel y PDF.

## Problema que resuelve

El cuadre de caja necesita una forma clara y consistente de registrar:

- Cantidades de monedas y billetes por denominacion.
- Gastos realizados con dinero de caja antes o despues del conteo.
- Totales calculados automaticamente.
- Estado del cuadre diario.
- Correcciones con trazabilidad cuando un cuadre ya este cerrado.

## Alcance actual

El sistema mantiene el modulo de caja como base operativa e incorpora clientes, productos, empleados, rutas, vehiculos y ventas como primeros modulos nuevos del ERP:

- Registro de cuadre diario.
- Separacion de monedas y billetes.
- Registro de gastos antes del conteo y despues del conteo.
- Calculo automatico de totales.
- Guardado en base de datos.
- Consulta de historial con filtros.
- Correcciones con trazabilidad.
- Resumen acumulado de caja.
- Operacion local con backup y restauracion.
- Registro, consulta, busqueda y edicion de clientes.
- Activacion e inactivacion de clientes sin borrado fisico.
- Registro, consulta, busqueda y edicion de productos.
- Precio base, costo estimado y presentacion por producto.
- Clasificacion de productos como terminado, materia prima, insumo, empaque,
  servicio u otro.
- Activacion e inactivacion de productos sin borrado fisico.
- Registro, consulta, busqueda, edicion y activacion de proveedores.
- Registro de compras con items de producto opcional, snapshots y calculos
  oficiales en backend.
- Consulta, filtros, detalle y anulacion logica de compras con motivo.
- Categorias y gastos operativos generales separados del cuadre diario.
- Plantillas recurrentes con generación manual y resumen oficial agrupado.
- Registro, consulta, busqueda y edicion de empleados.
- Datos base de cargo, tipo, sueldo referencial y frecuencia de pago.
- Activacion e inactivacion de empleados sin borrado fisico.
- Asistencia diaria editable y única por empleado y fecha.
- Anticipos y préstamos administrativos con anulación lógica.
- Abonos reversibles, saldos pendientes y resumen por empleado.
- Roles de pago por período con sueldo base, asistencia de referencia, bonos,
  otros ingresos y descuentos.
- Deducciones congeladas de anticipos y préstamos sin cambiar sus registros o
  saldos originales.
- Vista previa, totales backend, detalle, filtros, resumen por empleado y
  anulación lógica de roles.
- Registro, consulta, busqueda y edicion de rutas de entrega.
- Zonas, sectores, dias de atencion y referencias operativas por ruta.
- Activacion e inactivacion de rutas sin borrado fisico.
- Registro, consulta, busqueda y edicion de vehiculos.
- Placa, tipo, marca, modelo, combustible y capacidad referencial por vehiculo.
- Activacion e inactivacion de vehiculos sin borrado fisico.
- Registro de ventas de contado con cliente opcional o consumidor final.
- Uno o varios productos por venta, con snapshots y calculos oficiales en backend.
- Consulta, filtros, detalle y anulacion logica de ventas con motivo.
- Registro de ventas a credito solo para clientes activos y habilitados.
- Control de limite, saldo pendiente y resumen de deuda activa por cliente.
- Registro de abonos parciales o pagos totales sobre ventas a credito.
- Historial y anulacion logica de abonos con restauracion del saldo.
- Resumen general de cuentas por cobrar y listado de clientes con saldo pendiente.
- Estado de cuenta por cliente con ventas a credito y abonos registrados.
- Ubicaciones de inventario activables e inactivables sin borrado fisico.
- Stock actual por producto y ubicacion mediante entradas, salidas y ajustes manuales.
- Historial y anulacion trazable de movimientos con reversion del stock.
- Registro de produccion y envasado con uno o varios productos activos.
- Cantidades producidas, merma, snapshots y anulacion logica con motivo.
- Aplicacion explicita de produccion a una ubicacion de inventario.
- Entradas de stock por cantidad neta y anulacion transaccional trazable.
- Formulas de produccion con vigencia, estados, snapshots de insumos y costos
  estimados calculados en backend.
- Estimacion proporcional de cantidades y costos para una cantidad de salida,
  sin consumo automatico de inventario.
- Vista previa y consumo explicito de insumos desde una ubicacion activa,
  usando la cantidad producida y la merma configurada en cada formula.
- Salidas de inventario trazables por formula e insumo, con anulacion que
  conserva el historial y revierte el stock.
- Carga explicita de productos desde una ubicacion origen hacia el inventario de un vehiculo.
- Salida y entrada vinculadas a ruta, vehiculo y carga, con anulacion reversible.
- Retorno trazable de productos desde el vehiculo hacia una ubicacion no vehicular.
- Asociacion opcional de ventas y cobros a una carga activa y consulta de sus totales comerciales.
- Cierre financiero de una carga con importes oficiales congelados, efectivo entregado y diferencia.
- Historial y anulacion trazable del cierre, con bloqueo de operaciones vinculadas mientras permanezca activo.
- Comparacion informativa, por fecha o rango, entre cierres activos de ruta y el cuadre general de caja.
- Registro trazable del efectivo de un cierre de ruta recibido en un cuadre abierto, sin alterar el conteo fisico ni los totales oficiales de caja.
- Resumen operativo diario por fecha con caja, produccion, merma, rutas, ventas, cobros y alertas, sin modificar informacion.
- Reporte mensual operativo con una fila por dia, totales consolidados y alertas, sin modificar informacion.
- Panel gerencial por rango con indicadores, alertas y gráficos simples de caja,
  ventas, cartera, gastos, compras, producción, inventario, rutas y nómina.
- Exportaciones Excel autenticadas y de solo lectura para panel gerencial,
  resumen mensual, ventas, cartera, gastos operativos, compras, inventario,
  producción, rutas y nómina base.

Quedan fuera del MVP:

- Facturacion.
- Descuento automatico de inventario por ventas.
- Conciliacion automatica de cobros con caja o bancos.
- Ingreso automatico o conciliacion contable del cierre de ruta con caja o bancos.
- Liquidacion fisica del inventario restante de una ruta.
- Mantenimiento, combustible, kilometraje y rentabilidad por vehiculo.
- WhatsApp.
- BI, rentabilidad y comparativos gerenciales avanzados.
- Multiples cajas o turnos.
- Aplicacion de compras a inventario, pagos a proveedores y cuentas por pagar
  avanzadas.
- Conciliacion o movimiento automatico de gastos operativos en caja o bancos.
- Pago real de nómina, IESS, décimos, vacaciones avanzadas, horas extras,
  comisiones y cálculos laborales legales.

La vision ERP documenta esos temas como modulos futuros. Los Bloques 24 al 52C
implementan las bases de clientes, productos, empleados, rutas, vehiculos,
ventas de contado y a credito, cobros, reportes de cartera, inventario manual,
produccion aplicada a inventario, formulas, costos estimados y consumo
controlado de insumos, carga, retorno, actividad comercial, cierre financiero
de ruta, proveedores, compras administrativas, listas de precios, gastos
operativos, control administrativo de empleados, roles de pago base,
indicadores gerenciales visuales y exportaciones Excel/PDF. Registrar una
produccion o definir una formula no mueve stock por si solo; el consumo ocurre
exclusivamente al confirmar la accion explicita de consumo de insumos. Asociar
ventas y abonos a una carga, registrar su cierre financiero, registrar una
compra, calcular un rol, consultar el panel gerencial o exportar un reporte no
modifica automaticamente caja, inventario ni bancos.

## Stack definido

Frontend:

- Next.js
- TypeScript
- Tailwind CSS

Backend:

- FastAPI
- Python
- SQLAlchemy
- Pydantic
- Alembic

Base de datos:

- PostgreSQL

Entorno:

- Docker Compose

Pruebas:

- Pytest para backend.
- Pruebas manuales en navegador para frontend.

## Arquitectura esperada

```text
Frontend Next.js -> API FastAPI -> PostgreSQL
```

## Estructura actual

```text
cuadre-caja-agua-activa/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   ├── alembic/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   └── pyproject.toml
│   └── web/
│       ├── app/
│       ├── components/
│       ├── lib/
│       ├── types/
│       ├── Dockerfile
│       ├── README.md
│       └── package.json
├── docs/
│   ├── 00-definicion-base.md
│   ├── 01-roadmap.md
│   ├── 02-modelo-datos.md
│   ├── 03-reglas-negocio.md
│   ├── 04-ejecucion-local.md
│   ├── 05-backup-restauracion.md
│   ├── 06-prueba-piloto-local.md
│   ├── 07-checklist-uso-diario.md
│   ├── 08-checklist-validacion-mvp.md
│   ├── 09-vision-erp-agua-activa.md
│   ├── 10-modulos-erp.md
│   ├── 11-roadmap-erp.md
│   ├── 12-reglas-negocio-erp.md
│   ├── 28-backups-postgresql-windows.md
│   ├── 29-restauracion-controlada-postgresql.md
│   └── 30-backup-diario-programado-windows.md
├── scripts/
│   ├── backup-db.sh
│   ├── check-health.sh
│   ├── local-migrate.sh
│   ├── local-seed.sh
│   ├── local-start.sh
│   ├── local-stop.sh
│   └── restore-db.sh
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Estado actual

- Bloque 0: base documental y estructura inicial.
- Bloque 1: backend FastAPI base con health endpoint.
- Bloque 2: PostgreSQL, SQLAlchemy, Alembic y modelos iniciales.
- Bloque 3: logica de negocio interna de cuadres.
- Bloque 4: endpoints API REST de cuadres y denominaciones.
- Bloque 5: seeds idempotentes de denominaciones y usuario administrador.
- Bloque 6: autenticacion admin con JWT Bearer.
- Bloque 7: frontend Next.js con login, dashboard inicial y consumo de `/api/v1/auth/me`.
- Bloque 8: pantalla frontend de cuadre diario con denominaciones, conteos, resumen y cierre.
- Bloque 9: registro y listado basico de gastos dentro del cuadre diario.
- Bloque 10: historial y detalle de cuadres con resumen, conteos y gastos.
- Bloque 11: correcciones backend sobre cuadres cerrados con trazabilidad en `correction_logs`.
- Bloque 12: interfaz frontend para correcciones controladas y consulta de logs en detalle de historial.
- Bloque 13: ejecucion local ordenada con Docker Compose, scripts y documentacion de backup/restauracion.
- Bloque 14: precarga de conteos guardados y mejora del flujo diario.
- Bloque 15: resumen acumulado de caja con filtros por fecha y estado.
- Bloque 16: dashboard operativo con estado del cuadre de hoy, acciones rapidas, ultimos cuadres y recordatorio de backup.
- Bloque 17: filtros de historial por fecha desde, fecha hasta y estado.
- Bloque 18: documentacion operativa, checklist de uso diario, checklist de validacion MVP y health check local.
- Bloque 20: gastos separados entre antes del conteo y despues del conteo, con total final calculado solo contra gastos posteriores al conteo.
- Bloque 23: documentacion estrategica de la vision Agua Activa ERP, modulos, roadmap y reglas generales.
- Bloque 24: modulo base de clientes con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 25: catalogo base de productos y precios con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 26: modulo base de empleados con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 27: modulo base de rutas de entrega con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 28: modulo base de vehiculos con API autenticada, migracion, pruebas y pantalla de administracion.
- Bloque 29: modulo base de ventas de contado con detalle, calculos backend, filtros y anulacion logica.
- Bloque 30: modulo base de ventas a credito con limite por cliente, saldo pendiente y anulacion logica.
- Bloque 31: modulo base de cobros y abonos con pagos parciales o totales, historial y anulacion reversible.
- Bloque 32: estado de cuenta y reporte de cuentas por cobrar con resumen, filtros y detalle por cliente.
- Bloque 33: inventario base por ubicacion con stock, movimientos manuales y anulacion reversible.
- Bloque 34: produccion y envasado base con detalle por producto, snapshots, filtros y anulacion logica.
- Bloque 35: aplicacion explicita y reversible de produccion a inventario con trazabilidad por movimiento.
- Bloque 36: carga de camion desde inventario origen hacia una ubicacion de vehiculo, asociada a ruta y reversible.
- Bloque 37: retorno de productos desde una carga activa hacia una ubicacion no vehicular, trazable y reversible.
- Bloque 38: asociacion opcional de ventas y cobros a cargas activas con consulta comercial consolidada por ruta.
- Bloque 39: cierre financiero de ruta con snapshots comerciales, efectivo entregado, diferencia, historial, anulacion y bloqueos operativos.
- Bloque 40: reporte de solo lectura que compara cierres activos de ruta con el cuadre general de caja por fecha o rango.
- Bloque 41: registro controlado y anulable del dinero de un cierre de ruta recibido en un cuadre abierto, con snapshots y sin modificar caja, inventario, ventas o cobros.
- Bloque 42: resumen operativo diario de solo lectura con caja, produccion, rutas, ventas, cobros, detalles agrupados y alertas.
- Bloque 43: reporte mensual operativo de solo lectura con caja, produccion, ventas, cobros, rutas, filas diarias y alertas consolidadas.
- Bloque 44: auditoria general del ERP, inventario de rutas y endpoints,
  checklist de uso real, guia de piloto, matriz de modulos y roadmap de
  funciones obligatorias. Este bloque no crea migraciones, seeds ni cambios
  de logica critica.
- Bloque 45: proveedores y compras base con items, snapshots, totales
  calculados en backend, filtros, detalle y anulacion, sin efecto automatico
  en caja, gastos o inventario.
- Bloque 46: listas de precios por cliente y ruta con resolución en backend.
- Bloque 47: gastos operativos generales, categorías, proveedor opcional,
  plantillas recurrentes manuales, anulación y resumen, sin movimientos
  automáticos en caja, bancos, compras o inventario.
- Bloque 48: asistencia, anticipos, préstamos, abonos y saldos por empleado,
  con anulación lógica y sin movimientos automáticos de caja, bancos o gastos.
- Bloque 49: roles de pago base por período con snapshots, asistencia de
  referencia, deducciones de anticipos y préstamos, preview, detalle y
  anulación, sin pago real ni movimientos de caja, bancos o gastos.
- Bloque 50: clasificacion productiva, formulas con items y snapshots, costos
  estimados y escalamiento por cantidad, sin consumo automatico ni
  integracion automatica con produccion existente.
- Bloque 51: consumo controlado de insumos por produccion, con vista previa,
  formulas seleccionadas, salidas de inventario, snapshots y anulacion
  transaccional reversible.
- Bloque 52A: panel gerencial visual de solo lectura por rango.
- Bloque 52B: exportaciones Excel autenticadas para diez reportes del ERP,
  generadas en memoria y sin modificar datos.
- Bloque 52C: exportaciones PDF ejecutivas autenticadas para cinco reportes,
  generadas en memoria y sin modificar datos.
- Bloque 53: auditoria tecnica completa preproduccion, riesgos priorizados,
  checklist de servidor local y plan de correcciones. Sin migraciones, seeds
  ni cambios de logica.
- Bloque 54: roles `operator` y `admin_auditor`, cuentas personales,
  administracion de usuarios, permisos backend para acciones criticas y
  navegacion frontend segun rol.
- Bloque 55A: configuracion Docker de produccion local separada, imagenes
  productivas, secretos por entorno, healthchecks y scripts operativos seguros.
  La configuracion fue probada en KERNELOS-PC.
- Bloques 55B-1, 55B-2 y 55B-2A: acceso LAN y Tailscale privado comprobados,
  con acceso dual y sin publicar PostgreSQL 5432. La reserva DHCP sigue
  pendiente.
- Bloque 55C: scripts PowerShell de inicio, apagado seguro, health, logs,
  estado, reconstruccion y migracion consciente para operar desde Windows sin
  WSL.
- Bloque 56A: backup manual PostgreSQL en formato custom, SHA256, metadata
  segura, validacion con `pg_restore --list` y scripts para preparar, consultar
  o quitar una tarea diaria de Windows. La tarea no se registra automaticamente;
  el piloto sigue pendiente.
- Bloque 56B: restauracion real demostrada en un contenedor PostgreSQL temporal,
  sin red, puertos publicados ni volumen productivo; valida Alembic, tablas,
  conteos seguros, salud de produccion y cleanup con evidencia JSON ignorada por
  Git.
- Bloque 56C: tarea diaria `AguaActivaERP-BackupDiario` registrada en Windows a
  las 23:30 y validada mediante inicio manual controlado. La prueba genero un
  nuevo `.dump`, `.sha256` y `.json`, aprobo `pg_restore --list` y no afecto la
  salud de produccion.
- Bloque 58A: matriz granular de `operator` actualizada con diez decisiones
  oficiales de George, trazabilidad obligatoria, restricciones y pendientes
  futuros. No cambia permisos efectivos ni codigo.
- Bloques 58B a 58D-2: permisos backend y frontend implementados, pruebas
  integrales aprobadas y despliegue local sincronizado. `admin_auditor`
  conserva control total y `operator` sus 22 destinos operativos.
- Bloque 59A: preparación documental del piloto interno paralelo de cinco días,
  con checklist previo, guías por rol, registro de incidencias y criterios de
  inicio, pausa y detención. El piloto todavía no se inicia.
- Bloque 59B: cierre operativo de pendientes pre-piloto. Docker, red desde el
  servidor, cuentas activas y un backup existente fueron validados; la última
  tarea desatendida terminó con resultado `1` y siguen pendientes credenciales,
  dispositivos reales, servidor y DHCP. Decisión actual: **no listo**; el
  piloto no se inicia.
- Bloque 59C: el resultado `1` se correlacionó con indisponibilidad de Docker.
  La tarea recibió directorio de inicio, reintentos y logging seguro; una prueba
  mediante el Programador terminó con resultado `0`, generó `.dump`, `.sha256`
  y `.json`, y aprobó `pg_restore --list`. Los demás bloqueadores continúan y el
  piloto no se inicia.
- Bloque 59D: las cuentas `admin`/`admin_auditor` y
  `estherdelgado31`/`operator`, la salud LAN/Tailscale, `KERNELOS-PC` y la tarea
  de backup con resultado `0` fueron reconfirmados sin exponer secretos.
  Después se cerraron la rotación segura, los accesos reales, la continuidad
  del servidor, Docker, el método paralelo, las cuentas personales, los
  responsables operativos y la decisión temporal DHCP. Decisión:
  **listo con reservas para piloto controlado**; la reserva DHCP sigue pendiente
  y el piloto no se inicia hasta el bloque siguiente.
- Bloque 60A: George autorizó e inició de forma controlada el Día 1 el
  2026-07-28. Health, IP LAN, backup y método manual paralelo aprobaron. Codex
  no ingresó datos del negocio; la operación y el cierre quedan a cargo de los
  participantes. El piloto está iniciado, no cerrado, y no equivale a
  producción definitiva.
- Bloques 60B y 60B-2: se diagnosticó la anulación de ventas durante el piloto.
  El `POST` llegaba al API, pero PostgreSQL rechazaba un `FOR UPDATE` sobre
  relaciones opcionales. El lock quedó limitado a `sales` y el frontend usa un
  único helper dinámico para LAN, Tailscale, localhost, JSON y descargas. La
  corrección está desplegada; la comprobación con una venta real autorizada
  sigue pendiente.

Todavia no se han creado recibos de cobro de clientes, cobros masivos,
anticipos de clientes, facturacion electronica, ingreso automatico por
denominaciones o conciliacion contable del cierre de ruta con caja o bancos,
descuento de inventario por ventas, liquidacion fisica del inventario de ruta,
recepcion de compras en inventario, pagos reales a proveedores, cuentas por
pagar avanzadas, conciliacion de gastos operativos con caja o bancos, pago real
de nomina, IESS, décimos, vacaciones avanzadas, horas extras, comisiones,
cálculos laborales legales, mantenimiento, combustible, kilometraje,
asignaciones formales, consumo automatico de insumos, mapas, geolocalizacion,
edicion avanzada de ventas, edicion de gastos del cuadre, eliminacion fisica
de gastos, cookies ni refresh tokens.

## Documentacion

- `docs/00-definicion-base.md`: definicion base del proyecto y alcance del MVP.
- `docs/01-roadmap.md`: roadmap por bloques pequeños.
- `docs/02-modelo-datos.md`: modelo de datos inicial documentado.
- `docs/03-reglas-negocio.md`: reglas de negocio del MVP.
- `docs/04-ejecucion-local.md`: ejecucion local con Docker Compose.
- `docs/05-backup-restauracion.md`: backup y restauracion de PostgreSQL.
- `docs/06-prueba-piloto-local.md`: guia historica del piloto del MVP de caja.
- `docs/07-checklist-uso-diario.md`: checklist historico del MVP de caja.
- `docs/08-checklist-validacion-mvp.md`: validacion historica del MVP inicial.
- `docs/09-vision-erp-agua-activa.md`: vision estrategica de Agua Activa ERP.
- `docs/10-modulos-erp.md`: modulos proyectados del ERP.
- `docs/11-roadmap-erp.md`: roadmap por fases hacia Agua Activa ERP.
- `docs/12-reglas-negocio-erp.md`: reglas generales para crecer hacia ERP.
- `docs/13-auditoria-general-erp.md`: estado auditado, arquitectura, rutas,
  endpoints, migraciones, reglas y riesgos.
- `docs/14-checklist-uso-real-agua-activa.md`: checklist diario, semanal,
  mensual y de incidentes.
- `docs/15-guia-piloto-datos-reales.md`: piloto controlado de 1 a 2 semanas.
- `docs/16-roadmap-funciones-obligatorias.md`: Bloques funcionales y
  preproduccion posteriores a la auditoria general.
- `docs/17-matriz-modulos-erp.md`: estado, faltantes, prioridad y riesgo por
  modulo.
- `docs/18-auditoria-tecnica-completa.md`: corte tecnico del Bloque 53,
  evidencias, pruebas y decision de avance.
- `docs/19-hallazgos-riesgos-produccion.md`: riesgos criticos, importantes,
  menores y deuda tecnica.
- `docs/20-checklist-preparacion-servidor-local.md`: controles previos al PC,
  red, firewall, Tailscale, backups, restore y piloto.
- `docs/21-plan-correcciones-pre-produccion.md`: prioridades, responsables y
  criterios de cierre.
- `docs/22-matriz-permisos-roles.md`: permisos efectivos de `operator` y
  `admin_auditor` por accion.
- `docs/23-docker-produccion-local.md`: preparacion, seguridad y operacion del
  Compose de produccion local del Bloque 55A.
- `docs/24-prueba-docker-produccion-pc.md`: evidencia de la prueba del Compose
  productivo en KERNELOS-PC.
- `docs/25-red-local-firewall-pc.md`: evidencia de red LAN y Windows Firewall
  del Bloque 55B-1.
- `docs/26-tailscale-acceso-remoto-privado.md`: instalación, endurecimiento,
  acceso remoto privado y evidencia de acceso dual de los Bloques 55B-2 y
  55B-2A.
- `docs/27-scripts-powershell-servidor-local.md`: operacion segura en Windows,
  accesos directos, actualizaciones y comandos prohibidos del Bloque 55C.
- `docs/28-backups-postgresql-windows.md`: backup manual seguro y preparacion
  del backup diario de PostgreSQL en Windows para el Bloque 56A.
- `docs/29-restauracion-controlada-postgresql.md`: restauracion real de un dump
  en un contenedor temporal aislado y evidencia segura del Bloque 56B.
- `docs/30-backup-diario-programado-windows.md`: registro, prueba controlada y
  evidencia operativa de la tarea diaria de Windows del Bloque 56C.
- `docs/38-matriz-permisos-operador.md`: matriz granular de
  `operator`, decisiones oficiales, diferencias frente al estado actual y base
  documental para el Bloque 58B.
- `docs/41-bloque-58d-pruebas-integrales-permisos.md`: validación integral por
  rol y sincronización del despliegue productivo local.
- `docs/42-guia-operativa-permisos-usuarios.md`: uso de cuentas y escalamiento
  de acciones restringidas.
- `docs/43-preparacion-piloto-interno.md`: estado, pendientes obligatorios,
  alcance, checklists y criterios del piloto interno.
- `docs/44-guia-piloto-secretaria-operador.md`: flujo diario sencillo para la
  persona de oficina.
- `docs/45-guia-piloto-george-admin.md`: control diario, conciliación y
  contingencia para George.
- `docs/46-registro-incidencias-piloto.md`: plantilla y reglas de seguimiento
  de incidencias.
- `docs/47-plan-piloto-5-dias.md`: Día 0 y cinco jornadas de operación en
  paralelo.
- `docs/48-cierre-pendientes-pre-piloto.md`: evidencia actual, riesgos,
  bloqueadores y decisión del Bloque 59B.
- `docs/49-checklist-dia-0-piloto.md`: checklist práctico de personas, accesos,
  respaldo, módulos, contingencia y confirmación de George.
- `docs/50-diagnostico-backup-diario-desatendido.md`: causa, corrección, logs y
  validación del backup diario del Bloque 59C.
- `docs/51-usuarios-accesos-pre-piloto.md`: evidencia técnica, usuarios,
  accesos, servidor, DHCP, backup, reservas y decisión del Bloque 59D.
- `docs/52-confirmacion-dia-0-pre-piloto.md`: checklist de confirmación y firma
  anterior al Día 1.
- `docs/53-piloto-dia-1-inicio-controlado.md`: apertura técnica, alcance,
  checklists, incidencias, método paralelo y cierre pendiente del Día 1.
- `docs/54-incidencia-60b-anulacion-ventas.md`: diagnóstico y corrección del
  flujo de anulación de ventas y de la resolución central de API para LAN,
  Tailscale y localhost.

## Antes de usar datos reales

Los Bloques 54 a 58D-2 resuelven la separación de roles, preparan Docker de
producción local y demuestran backup/restore aislado, tarea diaria y permisos
en el despliegue actual. El Bloque 59A prepara el plan y el corte 59B conserva
la decisión **no listo** por bloqueadores operativos. El Bloque 59C resuelve el
fallo técnico del backup diario, pero no los demás bloqueadores. Todavía no se
autoriza declarar producción definitiva. El Bloque 59D cierra los controles
humanos y deja el sistema listo con reserva DHCP aceptada, pero no inicia el
piloto. El Bloque 60A registra posteriormente el inicio controlado del Día 1,
y 60B/60B-2 corrige la incidencia de anulación sin declarar producción
definitiva. Leer en este orden:

1. `docs/18-auditoria-tecnica-completa.md`.
2. `docs/19-hallazgos-riesgos-produccion.md`.
3. `docs/21-plan-correcciones-pre-produccion.md`.
4. `docs/22-matriz-permisos-roles.md`.
5. `docs/23-docker-produccion-local.md`.
6. `docs/24-prueba-docker-produccion-pc.md`.
7. `docs/25-red-local-firewall-pc.md`.
8. `docs/26-tailscale-acceso-remoto-privado.md`.
9. `docs/27-scripts-powershell-servidor-local.md`.
10. `docs/28-backups-postgresql-windows.md`.
11. `docs/29-restauracion-controlada-postgresql.md`.
12. `docs/30-backup-diario-programado-windows.md`.
13. `docs/20-checklist-preparacion-servidor-local.md`.
14. `docs/41-bloque-58d-pruebas-integrales-permisos.md`.
15. `docs/42-guia-operativa-permisos-usuarios.md`.
16. `docs/43-preparacion-piloto-interno.md`.
17. `docs/44-guia-piloto-secretaria-operador.md`.
18. `docs/45-guia-piloto-george-admin.md`.
19. `docs/46-registro-incidencias-piloto.md`.
20. `docs/48-cierre-pendientes-pre-piloto.md`.
21. `docs/49-checklist-dia-0-piloto.md`.
22. `docs/50-diagnostico-backup-diario-desatendido.md`.
23. `docs/51-usuarios-accesos-pre-piloto.md`.
24. `docs/52-confirmacion-dia-0-pre-piloto.md`.
25. `docs/47-plan-piloto-5-dias.md`, solo después de cerrar los pendientes
    obligatorios y aprobar el Día 0.
26. `docs/53-piloto-dia-1-inicio-controlado.md`, registro activo del inicio,
    operación, incidencias y cierre del Día 1.
27. `docs/54-incidencia-60b-anulacion-ventas.md`, diagnóstico, corrección
    técnica y validación pendiente de una operación real autorizada.

Las separaciones actuales son deliberadas: una venta no descarga inventario,
una produccion no aumenta stock hasta aplicarse, una compra no ingresa stock ni
crea gastos, y un cierre o recibo de ruta no modifica el conteo oficial de
caja. El piloto deberá mantener el método actual, conciliación diaria y backups
comprobados durante sus cinco jornadas.

## Ejecucion local con Docker

Crear variables locales:

```bash
cp .env.example .env
```

Editar `.env` y cambiar los valores `change-me` antes de usar datos reales.

Comandos principales desde la raiz:

```bash
./scripts/local-start.sh
./scripts/local-migrate.sh
./scripts/local-seed.sh
./scripts/check-health.sh
./scripts/backup-db.sh
./scripts/restore-db.sh backups/nombre_backup.sql
./scripts/local-stop.sh
```

Abrir:

```text
http://localhost:3000/login
```

La API queda disponible en:

```text
http://localhost:8010/api/v1/health
```

Los datos de PostgreSQL se conservan en el volumen Docker `postgres_data`. Los backups locales se guardan en `backups/` y no deben subirse a Git.

No usar `docker compose down -v` con datos reales. Para apagar sin borrar datos,
usar siempre `./scripts/local-stop.sh`.

## Produccion local en Windows (Bloques 55A a 56C)

La configuracion separada usa `docker-compose.prod.yml` y
`.env.production.local`. PostgreSQL no publica 5432, la API arranca con Uvicorn
sin reload y la Web se construye con `npm run build` y arranca con
`npm run start`.

Preparar primero las variables sin secretos de desarrollo:

```bash
cp .env.production.example .env.production.local
```

Reemplazar todos los marcadores y seguir la guia completa antes de construir:

```text
docs/23-docker-produccion-local.md
```

Comandos operativos recomendados en KERNELOS-PC:

```powershell
.\scripts\prod-local-start.ps1
.\scripts\prod-local-health.ps1
.\scripts\prod-local-status.ps1
.\scripts\prod-local-logs.ps1
.\scripts\prod-local-backup-db.ps1
.\scripts\prod-local-backup-list.ps1
.\scripts\prod-local-backup-check-task.ps1
.\scripts\prod-local-restore-test.ps1
.\scripts\prod-local-restore-test-list.ps1
.\scripts\prod-local-stop.ps1
```

Para una actualizacion aprobada, crear y comprobar primero un backup y usar
`prod-local-rebuild.ps1`. Ejecutar `prod-local-migrate.ps1` solo cuando la
actualizacion incluya migraciones revisadas. Los scripts `.sh` siguen siendo
utiles en macOS/Linux, pero no son necesarios en Windows. La guia completa es
`docs/27-scripts-powershell-servidor-local.md`; el procedimiento de backup y
tarea diaria esta en `docs/28-backups-postgresql-windows.md`, y la restauracion
aislada esta en `docs/29-restauracion-controlada-postgresql.md`. La evidencia
de activacion de la tarea esta en
`docs/30-backup-diario-programado-windows.md`; el diagnóstico y la corrección
del resultado `1` están en
`docs/50-diagnostico-backup-diario-desatendido.md`.

El arranque productivo no reconstruye por defecto ni ejecuta migraciones o
seeds. Los Bloques 55B-2 y
55B-2A configuran Tailscale privado en KERNELOS-PC y documentan la prueba final
desde el iPhone de George: login, dashboard y pantalla operativa por Wi-Fi/LAN
sin Tailscale; login, dashboard, panel gerencial y exportaciones por datos
móviles con Tailscale. El acceso dual LAN + Tailscale está listo para prueba
controlada. Esto todavía no autoriza usar la PC como servidor oficial, mover
datos, abrir puertos públicos ni iniciar el piloto.

## Frontend

La app web vive en `apps/web`.

Variables principales:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8010/api/v1
```

En el navegador, todas las solicitudes y descargas pasan por el helper central
de `apps/web/lib/api.ts`, que construye la URL con el hostname desde el que se
abrió la Web y el puerto `8010`. Así LAN, Tailscale y localhost usan la API del
mismo host. `NEXT_PUBLIC_API_URL` queda como fallback para SSR o contextos sin
`window`; no debe copiarse lógica de URL a las pantallas ni añadirse `fetch`
directo fuera del helper.

Para desarrollo:

```bash
cd apps/web
npm install
npm run dev
```

## Verificacion general

Ejecutar:

```bash
git status
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest
cd ../web
npm install
npm run typecheck
npm run build
```

Para validar Docker Compose desde la raiz:

```bash
docker compose config
```

Para validar que backend y frontend responden localmente:

```bash
./scripts/check-health.sh
```
