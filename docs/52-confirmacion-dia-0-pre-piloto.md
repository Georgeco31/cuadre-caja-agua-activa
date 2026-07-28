# 52 - Confirmación Día 0 pre-piloto

## Uso

Checklist de firma y confirmación anterior al Día 1. Completarlo únicamente con
evidencia real. Una casilla obligatoria sin cierre o sin riesgo aceptado
mantiene el estado **NO LISTO**. Los controles rutinarios posteriores y la
reserva DHCP expresamente aceptada no impiden la clasificación con reservas.

El Día 0 no inicia el piloto, no registra operación real y no autoriza
producción definitiva.

No escribir contraseñas, hashes, tokens, secretos, contenido de
`.env.production.local`, backups o logs. Para una rotación solo se permiten las
frases indicadas en la sección 2.

| Dato | Confirmación |
| --- | --- |
| Fecha | 2026-07-28 |
| Hora | |
| George presente | Sí; confirmación escrita |
| Operadora presente | |
| Responsable técnico | |
| Dispositivo de oficina | |
| Dispositivo de George | |

## 1. Estado técnico comprobado

- [x] `KERNELOS-PC` es el equipo comprobado.
- [x] `db`, `api` y `web` están activos y `healthy`.
- [x] API y Web responden por LAN desde el servidor.
- [x] API y Web responden por Tailscale desde el servidor.
- [x] Alembic está en `0026_user_roles`.
- [x] PostgreSQL `5432` no está publicado.
- [x] `.env.production.local` está ignorado y no versionado.
- [x] La unidad del servidor tiene 84,26 GB disponibles en el corte.
- [x] `admin` existe, está activo y tiene rol `admin_auditor`.
- [x] `estherdelgado31` existe, está activa y tiene rol `operator`.
- [x] La tarea de backup existe y su `LastTaskResult` actual es `0`.
- [x] El último backup de la tarea tiene `.dump`, `.sha256` y `.json` y fue
  validado sin ejecutar restore.
- [x] El piloto todavía no se ha iniciado.

Referencia técnica:
[`51-usuarios-accesos-pre-piloto.md`](51-usuarios-accesos-pre-piloto.md).

## 2. Contraseñas definitivas

- [x] George autorizó expresamente la rotación.
- [x] contraseña admin rotada correctamente.
- [x] contraseña estherdelgado31 rotada correctamente.
- [x] Cada titular conoce únicamente su propia contraseña.
- [x] Ninguna contraseña fue pegada en chat, consola visible, documento,
  script, log o archivo.
- [x] No quedó un script, variable temporal o archivo con contraseñas.
- [x] Ambos titulares volvieron a iniciar sesión después de la rotación.

## 3. Cuentas personales y reglas de uso

- [x] George confirma que `admin` es su cuenta personal.
- [x] La operadora confirma que `estherdelgado31` es su cuenta personal.
- [x] No se usan cuentas compartidas.
- [x] La cuenta `admin` no se usa para operación diaria.
- [x] La operadora no usa ni conoce la credencial administrativa.
- [x] George no presta su cuenta para evitar restricciones.
- [x] Cada persona cierra su sesión al terminar.

| Persona | Cuenta | Rol | Confirmación |
| --- | --- | --- | --- |
| George | `admin` | `admin_auditor` | Confirmado |
| Operadora | `estherdelgado31` | `operator` | Confirmado |

## 4. Acceso real de la operadora por LAN

URL: `http://192.168.100.220:3000/login`

- [x] La prueba se hizo desde el dispositivo real de oficina.
- [x] Cargó la pantalla de login.
- [x] El login con `estherdelgado31` funcionó.
- [x] Cargó el dashboard `operator`.
- [x] Se observaron 22 destinos operativos.
- [x] No aparecieron Reportes, Gerencia, Exportaciones, Usuarios, Precios ni
  Nómina.
- [x] Se abrió al menos una pantalla permitida.
- [x] Se cerró sesión correctamente.

| Campo | Confirmación |
| --- | --- |
| Dispositivo | |
| Pantalla permitida probada | |
| Resultado | OK después de la rotación; confirmado por George |
| Responsable | Operadora / George |
| Observación sin secretos | Recorrido real aprobado |

## 5. Acceso real de George por Tailscale

URL: `http://100.121.163.126:3000/login`

- [x] La prueba se hizo desde el dispositivo real de George.
- [x] Tailscale estaba activo.
- [x] Cargó la pantalla de login.
- [x] El login con `admin` funcionó.
- [x] Cargó el dashboard `admin_auditor`.
- [x] Se observaron 33 destinos.
- [x] Se abrió Reportes o Gerencia.
- [x] Una exportación Excel/PDF respondió, si formó parte de la prueba.
- [x] Se cerró sesión correctamente.

| Campo | Confirmación |
| --- | --- |
| Dispositivo | |
| Reporte o exportación | |
| Resultado | OK después de la rotación; confirmado por George |
| Responsable | George |
| Observación sin secretos | Recorrido real aprobado |

## 6. PC servidor y Docker

- [x] George confirma `KERNELOS-PC` como servidor del piloto.
- [x] El PC permanecerá encendido durante todo el horario operativo.
- [x] George confirma la continuidad del PC durante el horario de operación.
- [x] Se definió responsable de encendido y revisión.
- [x] Windows no se suspenderá ni hibernará durante la operación.
- [x] Docker Desktop estará abierto o disponible.
- [x] La sesión de Windows requerida por Docker y por la tarea estará
  disponible.
- [ ] Se ejecutará el health después de reiniciar.
- [x] Nadie usará `docker compose down -v`.
- [x] Nadie borrará volúmenes.

| Campo | Confirmación |
| --- | --- |
| Horario operativo | |
| Responsable del servidor | George |
| Control de continuidad | Mantener `KERNELOS-PC` encendido durante la operación |
| Resultado del health del Día 0 | OK después de la rotación; cero fallos y advertencias |

## 7. Red y DHCP

- [x] IP LAN actual comprobada: `192.168.100.220`.
- [x] IP Tailscale actual comprobada: `100.121.163.126`.
- [ ] La reserva DHCP fue configurada y la LAN se volvió a probar.
- [x] Si no hay reserva, George acepta temporalmente el riesgo con control
  diario de IP y criterio de detención.

Marcar y firmar una sola decisión:

- [ ] `DHCP bloquea piloto`.
- [x] `Riesgo DHCP aceptado temporalmente por George para piloto controlado`.

| Campo | Confirmación |
| --- | --- |
| Decisión | Riesgo aceptado temporalmente; reserva DHCP pendiente |
| Responsable del control diario de IP | George |
| Criterio de detención | Cambio de IP o pérdida de acceso LAN |
| Firma/confirmación de George | Confirmación escrita del 2026-07-28 |

No resetear el router, abrir puertos ni configurar port forwarding como parte
de este checklist.

## 8. Backup automático

- [x] La tarea `AguaActivaERP-BackupDiario` existe.
- [x] Estado actual: `Ready`.
- [x] Última ejecución: 2026-07-28 06:41:41.
- [x] `LastTaskResult`: `0`.
- [x] Próxima ejecución: 2026-07-28 23:30:30.
- [x] Último juego validado: `.dump`, `.sha256` y `.json`, OK.
- [x] `pg_restore --list` fue aprobado sin ejecutar restore.
- [x] Se definió quién revisará el resultado cada mañana.
- [ ] La ejecución natural de las 23:30 fue revisada como control rutinario.

Si el resultado vuelve a ser distinto de `0`, detener la autorización hasta
diagnosticarlo.

## 9. Método manual paralelo e incidencias

- [x] El método actual estará disponible durante toda la jornada.
- [x] Se acordó conciliar el mismo período en ambos métodos.
- [x] Se definió hora y responsable de conciliación diaria.
- [x] Existe la plantilla
  [`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md).
- [x] Se definió canal de incidencias.
- [x] Se definió responsable de recibir y clasificar incidencias.
- [x] Toda incidencia importante se registra también en la plantilla.
- [x] El ERP todavía no reemplaza oficialmente el método actual.

| Campo | Confirmación |
| --- | --- |
| Método paralelo | Confirmado por George; no reemplaza todavía el método actual |
| Responsable de conciliación | George |
| Hora de conciliación | Al cierre del día, después del cuadre de caja |
| Alcance de conciliación | Caja, ventas, cobros, gastos, producción/inventario si aplica e incidencias |
| Canal de incidencias | WhatsApp directo a George |
| Responsable de incidencias | George |

## 10. Resultado previo a la firma

| Control | Estado actual |
| --- | --- |
| Usuarios y roles técnicos | Confirmado |
| Contraseñas definitivas | Confirmado |
| Cuentas personales y no compartidas | Confirmado |
| Acceso real `operator` por LAN | Confirmado |
| Acceso real `admin_auditor` por Tailscale | Confirmado |
| Backup válido y tarea corregida | Confirmado |
| PC servidor y continuidad | Confirmado; responsable George |
| Docker actual | Confirmado |
| Tailscale del servidor | Confirmado |
| DHCP | Riesgo aceptado temporalmente; reserva pendiente |
| Método paralelo | Confirmado; conciliación e incidencias asignadas |
| Plantilla de incidencias | Disponible |
| Piloto iniciado | No |

Decisión final 59D: **LISTO CON RESERVAS PARA PILOTO CONTROLADO**. La reserva
DHCP continúa pendiente con riesgo aceptado temporalmente. El piloto no inicia
hasta ejecutar el bloque siguiente.

## 11. Decisión final de George

Marcar una sola opción después de completar las secciones anteriores:

- [ ] **Listo para piloto:** no quedan bloqueadores.
- [x] **Listo con reservas:** solo quedan riesgos aceptados expresamente, con
  responsable, control y criterio de detención.
- [ ] **No listo:** queda al menos un bloqueador y el Día 1 se aplaza.

| Campo | Confirmación |
| --- | --- |
| Decisión | Listo para piloto controlado, con reserva DHCP |
| Riesgos aceptados | Riesgo DHCP aceptado temporalmente |
| Bloqueadores restantes | Ninguno para preparar el inicio; reserva DHCP pendiente |
| Fecha autorizada para el Día 1 | Se definirá/ejecutará en el bloque siguiente |
| Nombre de George | George |
| Firma o confirmación escrita | Confirmación escrita recibida |
| Fecha y hora | 2026-07-28 |

La firma autoriza únicamente el inicio controlado y paralelo del Día 1. No
autoriza producción definitiva.
