# 49 - Checklist Día 0 del piloto

## Uso

Completar este checklist antes de autorizar el Día 1. El Día 0 prepara personas,
equipos, accesos, respaldo y contingencia; **no inicia el piloto**, no registra
operación real y no declara producción definitiva.

No escribir contraseñas, tokens, contenido de `.env.production.local`, hashes,
dumps ni secretos. Para una contraseña solo se permite registrar
`rotada correctamente`.

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

- [ ] Se revisó
  [`48-cierre-pendientes-pre-piloto.md`](48-cierre-pendientes-pre-piloto.md).
- [ ] No queda un bloqueador abierto.
- [ ] La última ejecución desatendida del backup terminó con resultado `0`.
- [ ] La reserva DHCP está configurada y la IP LAN fue reconfirmada.
- [ ] Si no existe reserva DHCP, George escribió
  `riesgo aceptado temporal`, la fecha, el control diario de IP y el criterio de
  detención.
- [ ] George comprende que una reserva o un riesgo aceptado no convierte el ERP
  en producción definitiva.

Si alguna casilla aplicable queda vacía, no se autoriza el Día 1.

## 2. PC servidor y Docker

- [ ] El equipo se identifica como `KERNELOS-PC`.
- [ ] KERNELOS-PC está conectada a corriente.
- [ ] KERNELOS-PC permanecerá encendida durante todo el horario operativo.
- [ ] Hay una persona responsable de encendido y revisión.
- [ ] Windows no entrará en suspensión ni hibernación durante el uso.
- [ ] Docker Desktop está abierto y disponible.
- [ ] La sesión necesaria para Docker y la tarea de backup estará activa.
- [ ] `db`, `api` y `web` aparecen `healthy`.
- [ ] El health termina con cero fallos críticos.
- [ ] Alembic muestra `0026_user_roles`.
- [ ] PostgreSQL `5432` no está publicado.
- [ ] La fecha y hora local son correctas.
- [ ] Hay espacio libre suficiente para operación y backups.

Comando autorizado de comprobación:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-health.ps1
```

Resultado:

| Campo | Registro |
| --- | --- |
| Fecha/hora del health | |
| Resultado general | |
| Observaciones sin secretos | |

## 3. Usuarios, roles y contraseñas

Estado técnico conocido al crear esta plantilla:

| Cuenta | Rol esperado | Activa | Titular confirmado | No se comparte |
| --- | --- | --- | --- | --- |
| `admin` | `admin_auditor` | Sí | [ ] | [ ] |
| `estherdelgado31` | `operator` | Sí | [ ] | [ ] |

- [ ] George confirma que `admin` es la cuenta administrativa.
- [ ] George confirma que `estherdelgado31` es la cuenta operativa.
- [ ] La operadora usará únicamente su cuenta de rol `operator`.
- [ ] La operadora no conoce ni usará la contraseña administrativa.
- [ ] George no prestará la cuenta administrativa para resolver bloqueos.
- [ ] Nadie usará una cuenta compartida.
- [ ] Contraseña de `admin_auditor`: `rotada correctamente`.
- [ ] Contraseña de `operator`: `rotada correctamente`.
- [ ] Cada titular conoce únicamente su propia contraseña.
- [ ] Las contraseñas no fueron copiadas en chat, papel visible, captura o
  documentación.
- [ ] Los roles visibles después del login coinciden con lo esperado.
- [ ] Los permisos vigentes de los Bloques 58B a 58D-2 fueron recordados.

## 4. Acceso LAN de la operadora

Realizar desde el dispositivo que se usará en la oficina:

- [ ] Abrir `http://192.168.100.220:3000/login`.
- [ ] La pantalla de login carga.
- [ ] Iniciar sesión con la cuenta personal de rol `operator`.
- [ ] El dashboard carga.
- [ ] El rol mostrado es el esperado.
- [ ] Abrir una pantalla operativa permitida.
- [ ] Confirmar que no aparecen accesos administrativos.
- [ ] Cerrar sesión y volver a entrar correctamente.
- [ ] Guardar solo evidencia sin contraseña ni token.

| Campo | Registro |
| --- | --- |
| Dispositivo probado | |
| Pantalla operativa abierta | |
| Resultado | OK / No OK |
| Evidencia segura | |
| Responsable | |

## 5. Acceso Tailscale de George

Realizar desde el dispositivo que George usará fuera de la LAN:

- [ ] Tailscale está conectado a la red privada aprobada.
- [ ] Abrir `http://100.121.163.126:3000/login`.
- [ ] La pantalla de login carga.
- [ ] Iniciar sesión con la cuenta personal de rol `admin_auditor`.
- [ ] El dashboard carga.
- [ ] El rol mostrado es el esperado.
- [ ] Abrir el panel gerencial o un reporte autorizado.
- [ ] Comprobar una exportación de solo lectura, si aplica.
- [ ] Cerrar sesión correctamente.
- [ ] Guardar solo evidencia sin contraseña, token ni contenido sensible.

| Campo | Registro |
| --- | --- |
| Dispositivo probado | |
| Reporte o exportación comprobada | |
| Resultado | OK / No OK |
| Evidencia segura | |
| Responsable | George |

## 6. Backup reciente y tarea diaria

Consultar sin borrar ni restaurar:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-check-task.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-backup-list.ps1
```

- [ ] La tarea `AguaActivaERP-BackupDiario` existe.
- [ ] La próxima ejecución es coherente con las 23:30.
- [ ] La última ejecución ocurrió por el disparador, sin intervención.
- [ ] El último resultado es `0`.
- [ ] La ejecución creó un nuevo `.dump`.
- [ ] Existe su `.sha256`.
- [ ] Existe su `.json`.
- [ ] El checksum coincide.
- [ ] La metadata JSON es válida y no contiene secretos.
- [ ] `pg_restore --list` termina correctamente.
- [ ] El backup no está en staging ni se subirá a Git.
- [ ] Se definió quién revisará la tarea cada mañana.
- [ ] Se entiende que esta validación no autoriza ejecutar un restore.

| Campo | Registro |
| --- | --- |
| Última ejecución | |
| Último resultado | |
| Fecha del backup validado | |
| Dump + SHA256 + JSON | OK / No OK |
| `pg_restore --list` | OK / No OK |
| Responsable de revisión diaria | |

## 7. Método paralelo e incidencias

- [ ] El método actual está disponible para toda la jornada.
- [ ] Se acordó cómo relacionar el mismo movimiento en ambos registros.
- [ ] Se acordó la hora de conciliación diaria.
- [ ] La plantilla
  [`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md)
  está lista.
- [ ] Se definió el canal para avisar incidencias.
- [ ] Se definió quién recibe y clasifica incidencias.
- [ ] Todos saben registrar hora, usuario, módulo y resultado sin secretos.
- [ ] Todos saben que una diferencia no se corrige a ciegas.
- [ ] Todos conocen el punto de corte para continuar solo con el método actual.

| Campo | Registro |
| --- | --- |
| Método paralelo preparado | |
| Responsable de conciliación | |
| Canal de incidencias | |
| Responsable de incidencias | |
| Hora de revisión diaria | |

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
- [ ] **Listo con reservas:** solo existen riesgos expresamente aceptados, con
  controles, responsable y criterio de detención.
- [ ] **No listo:** queda al menos un bloqueador; se mueve el Día 1.

| Campo | Confirmación |
| --- | --- |
| Decisión | |
| Riesgos aceptados | |
| Controles de cada riesgo | |
| Bloqueadores restantes | |
| Fecha autorizada para el Día 1 | |
| Nombre de George | |
| Firma o confirmación escrita | |
| Fecha y hora de confirmación | |

La firma de este checklist autoriza únicamente el inicio controlado del Día 1
en paralelo con el método actual. No autoriza producción definitiva.

