# 49 - Checklist Día 0 del piloto

## Uso

Completar este checklist antes de autorizar el Día 1. El Día 0 prepara personas,
equipos, accesos, respaldo y contingencia; **no inicia el piloto**, no registra
operación real y no declara producción definitiva.

No escribir contraseñas, tokens, contenido de `.env.production.local`, hashes,
dumps ni secretos. Para una contraseña solo se permite registrar
`rotada correctamente`.

El Bloque 59D creó una versión de confirmación previa con el corte técnico
actual en
[`52-confirmacion-dia-0-pre-piloto.md`](52-confirmacion-dia-0-pre-piloto.md).
Ambos checklists deben coincidir antes de autorizar el Día 1.

| Dato | Registro |
| --- | --- |
| Fecha del Día 0 | |
| Hora de inicio | |
| Hora de cierre | |
| Responsable técnico | |
| Operadora presente | |
| George presente | |
| URL LAN usada | `http://192.168.100.220:3000/login` |
| URL Tailscale usada | `http://100.121.163.126:3000/login` |

## 1. Decisión previa sobre bloqueadores

- [x] Se revisó
  [`48-cierre-pendientes-pre-piloto.md`](48-cierre-pendientes-pre-piloto.md).
- [x] No queda un bloqueador abierto.
- [x] La última ejecución mediante la tarea terminó con resultado `0`.
- [ ] La reserva DHCP está configurada y la IP LAN fue reconfirmada.
- [x] Si no existe reserva DHCP, George escribió
  `riesgo aceptado temporal`, la fecha, el control diario de IP y el criterio de
  detención.
- [x] George comprende que una reserva o un riesgo aceptado no convierte el ERP
  en producción definitiva.

Si alguna casilla aplicable queda vacía, no se autoriza el Día 1.

El Bloque 59C cerró el resultado técnico `1` y validó una ejecución mediante
`Start-ScheduledTask`. La ejecución por el disparador natural, sin intervención,
se conserva como control separado en la sección 6.

## 2. PC servidor y Docker

- [x] El equipo se identifica como `KERNELOS-PC`.
- [x] George confirma la continuidad de KERNELOS-PC durante el horario.
- [x] KERNELOS-PC permanecerá encendida durante todo el horario operativo.
- [x] George es responsable de encendido y revisión.
- [x] Windows no entrará en suspensión ni hibernación durante el uso.
- [x] Docker Desktop está abierto y disponible en el corte técnico.
- [x] La sesión necesaria para Docker y la tarea de backup estará activa.
- [x] `db`, `api` y `web` aparecen `healthy`.
- [x] El health termina con cero fallos críticos.
- [x] Alembic muestra `0026_user_roles`.
- [x] PostgreSQL `5432` no está publicado.
- [x] La fecha y hora local son correctas.
- [x] Hay espacio libre suficiente para operación y backups (84,26 GB en el corte).

La configuración técnica observada usa `Sleep after = Nunca` con corriente
alterna. La casilla de continuidad permanece abierta hasta que George confirme
energía, horario y prohibición de suspensión manual.

Comando autorizado de comprobación:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-health.ps1
```

Resultado:

| Campo | Registro |
| --- | --- |
| Fecha/hora del health | 2026-07-28, corte 59D |
| Resultado general | OK; cero fallos críticos y cero advertencias |
| Observaciones sin secretos | LAN/Tailscale OK; Alembic 0026; 5432 no publicado |

## 3. Usuarios, roles y contraseñas

Estado técnico conocido al crear esta plantilla:

| Cuenta | Rol esperado | Activa | Titular confirmado | No se comparte |
| --- | --- | --- | --- | --- |
| `admin` | `admin_auditor` | Sí | [x] | [x] |
| `estherdelgado31` | `operator` | Sí | [x] | [x] |

- [x] George confirma que `admin` es la cuenta administrativa.
- [x] George confirma que `estherdelgado31` es la cuenta operativa.
- [x] La operadora usará únicamente su cuenta de rol `operator`.
- [x] La operadora no conoce ni usará la contraseña administrativa.
- [x] George no prestará la cuenta administrativa para resolver bloqueos.
- [x] Nadie usará una cuenta compartida.
- [x] contraseña admin rotada correctamente.
- [x] contraseña estherdelgado31 rotada correctamente.
- [x] Cada titular conoce únicamente su propia contraseña.
- [x] Las contraseñas no fueron copiadas en chat, papel visible, captura o
  documentación.
- [x] Los roles visibles después del login coinciden con lo esperado.
- [ ] Los permisos vigentes de los Bloques 58B a 58D-2 fueron recordados.

## 4. Acceso LAN de la operadora

Realizar desde el dispositivo que se usará en la oficina:

- [x] Abrir `http://192.168.100.220:3000/login`.
- [x] La pantalla de login carga.
- [x] Iniciar sesión con la cuenta de rol `operator`.
- [x] El dashboard carga.
- [x] El rol mostrado es el esperado.
- [x] Se muestran los 22 destinos operativos esperados.
- [x] Abrir una pantalla operativa permitida.
- [x] Confirmar que no aparecen Reportes/Gerencia/Exportaciones/Usuarios/Precios/Nómina.
- [x] Cerrar sesión correctamente.
- [x] Guardar solo evidencia sin contraseña ni token.

| Campo | Registro |
| --- | --- |
| Dispositivo probado | |
| Pantalla operativa abierta | |
| Resultado | OK; confirmado por George el 2026-07-28 |
| Evidencia segura | |
| Responsable | |

## 5. Acceso Tailscale de George

Realizar desde el dispositivo que George usará fuera de la LAN:

- [x] Tailscale está conectado a la red privada aprobada.
- [x] Abrir `http://100.121.163.126:3000/login`.
- [x] La pantalla de login carga.
- [x] Iniciar sesión con la cuenta de rol `admin_auditor`.
- [x] El dashboard carga.
- [x] El rol mostrado es el esperado.
- [x] Se muestran los 33 destinos esperados.
- [x] Abrir el panel gerencial o un reporte autorizado.
- [x] Comprobar una exportación de solo lectura, si aplica.
- [x] Cerrar sesión correctamente.
- [x] Guardar solo evidencia sin contraseña, token ni contenido sensible.

| Campo | Registro |
| --- | --- |
| Dispositivo probado | |
| Reporte o exportación comprobada | |
| Resultado | OK; confirmado por George el 2026-07-28 |
| Evidencia segura | |
| Responsable | George |

## 6. Backup reciente y tarea diaria

Consultar sin borrar ni restaurar:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-check-task.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-list.ps1
```

- [x] La tarea `AguaActivaERP-BackupDiario` existe.
- [x] La próxima ejecución es coherente con las 23:30.
- [ ] La última ejecución ocurrió por el disparador, sin intervención.
- [x] El último resultado es `0`.
- [x] La ejecución creó un nuevo `.dump`.
- [x] Existe su `.sha256`.
- [x] Existe su `.json`.
- [x] El checksum coincide.
- [x] La metadata JSON es válida y no contiene secretos.
- [x] `pg_restore --list` termina correctamente.
- [x] El backup no está en staging ni se subirá a Git.
- [x] Se definió quién revisará la tarea cada mañana.
- [x] Se entiende que esta validación no autoriza ejecutar un restore.

| Campo | Registro |
| --- | --- |
| Última ejecución | 2026-07-28 06:41:41, inicio manual de la tarea |
| Último resultado | `0` |
| Fecha del backup validado | 2026-07-28 06:41 |
| Dump + SHA256 + JSON | OK |
| `pg_restore --list` | OK |
| Responsable de revisión diaria | George, cada mañana antes de operar |

La siguiente ejecución natural de las 23:30 es un control rutinario posterior a
la corrección 59C. Si vuelve a fallar, se convierte en bloqueador.

## 7. Método paralelo e incidencias

- [x] El método actual está disponible para toda la jornada.
- [x] Se acordó conciliar el mismo período en ambos registros.
- [x] Se acordó la hora de conciliación diaria.
- [x] La plantilla
  [`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md)
  está lista.
- [x] Se definió el canal para avisar incidencias.
- [x] Se definió quién recibe y clasifica incidencias.
- [x] Todos saben registrar hora, usuario, módulo y resultado sin secretos.
- [ ] Todos saben que una diferencia no se corrige a ciegas.
- [x] Se confirmó que el ERP todavía no reemplaza oficialmente el método actual.

| Campo | Registro |
| --- | --- |
| Método paralelo preparado | Confirmado por George |
| Responsable de conciliación | George |
| Canal de incidencias | WhatsApp directo a George; registrar las importantes en la plantilla |
| Responsable de incidencias | George |
| Hora de revisión diaria | Al cierre del día, después del cuadre de caja |

## 8. Módulos que se usarán

Marcar únicamente el alcance aprobado para los cinco días:

- [ ] Login y roles.
- [ ] Dashboard.
- [ ] Cuadre de caja.
- [ ] Gastos de caja.
- [ ] Clientes.
- [ ] Ventas de contado.
- [ ] Cobros.
- [ ] Producción diaria.
- [ ] Inventario con movimientos `entry`/`exit`, sin costos ni ajustes.
- [ ] Historial básico.
- [ ] Reportes y exportaciones de solo lectura, solo George.
- [ ] Ventas a crédito, únicamente con aprobación específica de George.

Decisión sobre ventas a crédito:

- [ ] Incluidas.
- [ ] Excluidas.

Alcance u observaciones:

| Campo | Registro |
| --- | --- |
| Módulos aprobados | |
| Restricciones adicionales | |
| Responsable de recordar el alcance | |

## 9. Módulos y acciones que no se usarán

- [ ] Nómina.
- [ ] Anticipos y préstamos.
- [ ] Cambios de precios.
- [ ] Fórmulas y costos.
- [ ] Correcciones de cuadres cerrados por la operadora.
- [ ] Anulaciones.
- [ ] Ajustes delicados de inventario.
- [ ] Aplicación de producción o consumo de insumos.
- [ ] Cambios masivos de datos.
- [ ] Eliminación o desactivación de registros importantes.
- [ ] Administración de usuarios y roles durante la operación.
- [ ] Restore, migraciones, seeds, rebuild o `docker compose down -v`.

Una acción excepcional de George requiere motivo, evidencia y registro de
incidencia; no amplía automáticamente el alcance del piloto.

## 10. Criterios para pausar o detener

Pausar el módulo afectado y continuar con el método actual si:

- [ ] una pantalla no carga o repite errores;
- [ ] existe riesgo de duplicar una operación;
- [ ] hay una diferencia todavía no explicada;
- [ ] una acción aprobada muestra un bloqueo de permisos;
- [ ] LAN o Tailscale falla de forma parcial;
- [ ] falta información para registrar con seguridad.

Detener nuevas entradas en todo el ERP si:

- [ ] se sospecha pérdida, corrupción o mezcla de datos;
- [ ] una persona accede fuera de su rol;
- [ ] se comparte o compromete una credencial;
- [ ] caja, ventas o cobros no pueden conciliarse de forma material;
- [ ] servidor o base de datos presentan fallos repetidos;
- [ ] el backup esperado falla y no existe respaldo reciente validado;
- [ ] el sistema queda indisponible durante una parte relevante de la jornada;
- [ ] existe una incidencia crítica;
- [ ] George determina que continuar aumenta el riesgo.

Ante una pausa o detención:

1. No crear ni modificar más registros en el alcance afectado.
2. Anotar hora, usuario, módulo y última operación conocida.
3. Continuar con el método actual desde un punto de corte claro.
4. Avisar a George y registrar la incidencia.
5. No borrar datos ni improvisar restores, migraciones o reinicios destructivos.

## 11. Confirmación final de George

Marcar una sola decisión:

- [ ] **Listo para piloto:** todos los controles obligatorios están cerrados.
- [x] **Listo con reservas:** solo existen riesgos expresamente aceptados, con
  controles, responsable y criterio de detención.
- [ ] **No listo:** queda al menos un bloqueador; se mueve el Día 1.

| Campo | Confirmación |
| --- | --- |
| Decisión | Listo para piloto controlado, con reserva DHCP |
| Riesgos aceptados | Riesgo DHCP aceptado temporalmente |
| Controles de cada riesgo | Verificar IP; detener y actualizar si cambia |
| Bloqueadores restantes | Ninguno para preparar el inicio |
| Fecha autorizada para el Día 1 | Se ejecutará en el bloque siguiente |
| Nombre de George | George |
| Firma o confirmación escrita | Confirmación escrita recibida |
| Fecha y hora de confirmación | 2026-07-28 |

La firma de este checklist autoriza únicamente el inicio controlado del Día 1
en paralelo con el método actual. No autoriza producción definitiva. La fecha,
el horario y el alcance exacto de módulos deben registrarse en el bloque de
inicio antes de crear la primera operación del piloto.
