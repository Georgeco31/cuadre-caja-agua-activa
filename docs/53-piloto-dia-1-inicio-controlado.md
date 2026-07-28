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
