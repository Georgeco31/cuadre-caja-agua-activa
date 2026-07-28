# 43 - Preparación del piloto interno

## Objetivo

Preparar un piloto interno controlado de Agua Activa ERP durante cinco días de
operación, en paralelo con el método actual. Este documento define las
condiciones previas, el alcance, los responsables y las reglas de contingencia.

El Bloque 59A es únicamente documental. **No inicia el piloto ni declara el ERP
en producción definitiva.**

## Estado actual del sistema

Al cierre de los Bloques 55A a 58D-2:

- el entorno local productivo funciona con Docker en KERNELOS-PC;
- Web y API fueron comprobadas por LAN y por Tailscale;
- PostgreSQL 5432 no está publicado en el host;
- Alembic está en `0026_user_roles`;
- la versión desplegada está sincronizada con las protecciones actuales;
- `admin_auditor` conserva control total y 33 destinos;
- `operator` conserva 22 destinos operativos;
- las acciones sensibles del operador reciben `403` real en backend y se
  ocultan o bloquean en frontend;
- el backup manual seguro y la restauración aislada fueron demostrados;
- la tarea diaria `AguaActivaERP-BackupDiario` está registrada a las 23:30 y
  aprobó un inicio manual controlado;
- `backups/` y `.env.production.local` están ignorados por Git.

Estas evidencias demuestran preparación técnica, pero no reemplazan las
confirmaciones del Día 0 ni autorizan todavía el uso piloto.

## Corte operativo del Bloque 59B

El 2026-07-28 se ejecutó el cierre de pendientes previo al piloto. El resultado
detallado está en
[`48-cierre-pendientes-pre-piloto.md`](48-cierre-pendientes-pre-piloto.md) y el
checklist práctico del Día 0 en
[`49-checklist-dia-0-piloto.md`](49-checklist-dia-0-piloto.md).

| Control | Resultado del corte |
| --- | --- |
| Cuentas | `admin`/`admin_auditor` y `estherdelgado31`/`operator`, activas |
| Contraseñas definitivas | Sin rotación ni confirmación segura; bloqueador |
| Docker | `db`, `api` y `web` saludables |
| Red desde el servidor | API y Web por LAN y Tailscale, OK |
| Dispositivos reales | Pruebas actuales de secretaria y George pendientes |
| Alembic | `0026_user_roles` |
| PostgreSQL | `5432` no publicado |
| Backup existente | Dump, checksum, JSON y `pg_restore --list`, OK |
| Tarea diaria | Existe y está `Ready`, pero la última ejecución desatendida terminó con resultado `1` |
| DHCP | Pendiente y sin aceptación temporal de George |
| Decisión | **No listo; no iniciar el piloto** |

La disponibilidad técnica actual no cierra la titularidad de cuentas, el uso sin
compartir, las contraseñas, los accesos desde dispositivos reales ni los
compromisos de disponibilidad del servidor.

## Qué ya está listo

| Área | Estado listo para preparación |
| --- | --- |
| Login y roles | Dos roles validados; backend y frontend aplican la política |
| Operación de `operator` | Caja, gastos, clientes, ventas, cobros, producción, inventario operativo e historial básico |
| Control de `admin_auditor` | Revisión total, reportes, exportaciones y acciones administrativas |
| Despliegue local | Contenedores saludables y acceso LAN/Tailscale comprobado |
| Base de datos | PostgreSQL persistente, sin publicar 5432; Alembic en `0026_user_roles` |
| Respaldo | Backup manual validado y tarea diaria registrada |
| Recuperación | Restore demostrado únicamente en ambiente aislado |
| Documentación | Guías de permisos, servidor, red, backup y restore disponibles |

## Pendientes obligatorios antes de iniciar

Todos los puntos de esta tabla deben quedar confirmados con fecha, responsable
y evidencia. El piloto no puede empezar con una casilla vacía.

| Confirmación obligatoria | Responsable | Evidencia mínima | Estado |
| --- | --- | --- | --- |
| Primera ejecución desatendida real del backup diario terminada con resultado `0` | George | Fecha/hora de la tarea y nuevo juego `.dump`, `.sha256`, `.json` válido | [ ] |
| Contraseñas definitivas de `admin_auditor` y `operator` rotadas por canal seguro | George | Confirmación sin escribir ni adjuntar la contraseña | [ ] |
| Usuarios reales activos, individuales y asociados a cada persona | George | Lista de nombres de usuario y rol, sin contraseñas | [ ] |
| Reserva DHCP o dirección estable del servidor configurada | George / técnico de red | Dirección reservada y acceso LAN posterior aprobado | [ ] |
| PC servidor disponible y encendida durante todo el horario de uso | George | Horario y responsable de encendido definidos | [ ] |
| Docker Desktop inicia correctamente en la PC servidor | George | Reinicio controlado y estado saludable confirmado | [ ] |
| Acceso desde la computadora o dispositivo real de la secretaria | Secretaria + George | Login `operator` y carga de un módulo permitido | [ ] |
| Acceso de George por Tailscale | George | Login `admin_auditor` y carga de un módulo administrativo | [ ] |
| Prohibición de cuentas compartidas comprendida y aceptada | Todos los participantes | Cada persona confirma su cuenta individual | [ ] |

También deben definirse antes de comenzar:

- [ ] fecha y horario de cada jornada;
- [ ] persona que cubre a la secretaria si se ausenta;
- [ ] formularios o archivos del método actual disponibles para toda la jornada;
- [ ] responsable de recibir incidencias y medio de contacto;
- [ ] decisión explícita sobre incluir o no ventas a crédito;
- [ ] breve práctica de la secretaria con la
  [guía de operador](44-guia-piloto-secretaria-operador.md);
- [ ] autorización de inicio del Día 1 registrada por George.

## Riesgos antes y durante el piloto

| Riesgo | Efecto posible | Control del piloto |
| --- | --- | --- |
| Backup desatendido no comprobado | Jornada sin respaldo esperado | No iniciar hasta comprobarlo; revisar el resultado cada mañana |
| Cambio de IP del servidor | Pérdida de acceso de la secretaria | Configurar reserva DHCP antes del Día 1 |
| PC apagada, suspendida o Docker detenido | ERP no disponible | Definir horario y responsable; mantener el método actual |
| Cuenta compartida | Pérdida de trazabilidad | Usar cuentas personales; detener la sesión compartida |
| Registro duplicado u omitido | Diferencia entre ERP y método actual | Registrar ambos en el momento y conciliar al cierre |
| Venta a crédito sin proceso preparado | Saldo o cobro incorrecto | Excluirla hasta que George apruebe su uso |
| Acción administrativa accidental | Cambios difíciles de revertir | Usar `operator` para operación; reservar `admin_auditor` para control |
| Corrección apresurada de una diferencia | Pérdida de evidencia | No modificar históricos; registrar incidencia y motivo antes de actuar |
| Falla de acceso remoto o LAN | Interrupción parcial | Continuar manualmente, registrar hora y avisar a George |

## Checklist técnica

- [x] Compose productivo separado y sin modo de desarrollo.
- [x] API y Web con healthchecks.
- [x] Servicios con reinicio y rotación básica de logs.
- [x] PostgreSQL 5432 sin publicación en el host.
- [x] Alembic en `0026_user_roles`.
- [x] Backend y frontend sincronizados tras 58D-2.
- [x] Permisos integrales por rol validados.
- [ ] Estado saludable confirmado el Día 0.
- [ ] Espacio libre suficiente en servidor y destino de backups.
- [ ] Fecha y hora de Ecuador correctas.
- [ ] Reinicio controlado confirma arranque correcto de Docker Desktop.
- [ ] Navegador del puesto de la secretaria actualizado.
- [ ] URL o acceso directo aprobado disponible en el puesto real.
- [ ] Ningún cambio técnico pendiente se mezcla con las jornadas del piloto.

## Checklist operativa

- [ ] Alcance de los módulos explicado a secretaria y George.
- [ ] Método actual preparado y disponible en paralelo.
- [ ] Regla para identificar el mismo movimiento en ambos registros acordada.
- [ ] Hora de apertura, conciliación y cierre diario acordada.
- [ ] Responsable de caja y responsable de revisión identificados.
- [ ] Productos, clientes y saldos iniciales necesarios revisados sin cambios
  masivos.
- [ ] Ventas a crédito incluidas solo si el proceso operativo fue aprobado.
- [ ] Plantilla de incidencias disponible.
- [ ] Canal para avisar incidentes definido.
- [ ] Criterios de pausa y detención comprendidos.
- [ ] No se declara producción definitiva al terminar el Día 5.

## Checklist de usuarios

- [ ] Existe una cuenta personal activa para cada participante.
- [ ] Cada cuenta tiene el rol correcto.
- [ ] Contraseñas definitivas rotadas y conocidas solo por su titular.
- [ ] Login real de `operator` aprobado desde el puesto de la secretaria.
- [ ] Login real de `admin_auditor` aprobado por Tailscale para George.
- [ ] La secretaria reconoce el nombre o rol de su sesión.
- [ ] La secretaria sabe cerrar sesión al terminar o alejarse.
- [ ] Nadie utilizará la cuenta de otra persona.
- [ ] Nadie guardará contraseñas en la plantilla de incidencias.
- [ ] George sabe revisar un bloqueo sin prestar su cuenta.

## Checklist de backups

- [x] Backup manual crea dump, checksum y metadata.
- [x] Formato validado mediante `pg_restore --list`.
- [x] Restore real demostrado en ambiente aislado.
- [x] Tarea diaria registrada a las 23:30.
- [x] Inicio manual controlado de la tarea aprobado.
- [ ] Primera ejecución por su disparador, sin intervención, aprobada.
- [ ] Hora de las 23:30 confirmada como compatible con la operación.
- [ ] Backup más reciente y resultado de tarea revisados antes del Día 1.
- [ ] Responsable de revisión diaria definido.
- [ ] Espacio disponible revisado.
- [ ] Copia externa periódica acordada o riesgo aceptado expresamente por
  George.
- [ ] Se entiende que un fallo de backup no autoriza un restore.

La comprobación debe seguir
[`30-backup-diario-programado-windows.md`](30-backup-diario-programado-windows.md).
No se deben adjuntar dumps, checksums con rutas sensibles, variables ni
credenciales a este documento.

En el corte 59B, la tarea existía y su próxima ejecución estaba programada, pero
la ejecución desatendida del 2026-07-27 23:30:30 terminó con resultado `1`. Un
backup existente posterior aprobó checksum, metadata y `pg_restore --list`, pero
no sustituye una ejecución por disparador con resultado `0`.

## Checklist de red y acceso

- [x] Web y API accesibles por LAN en la prueba previa.
- [x] Web y API accesibles por Tailscale en la prueba previa.
- [x] CORS validado para los orígenes aprobados.
- [x] Tailscale sin Funnel ni exposición pública.
- [x] PostgreSQL no publicado por LAN ni Tailscale.
- [ ] Reserva DHCP o dirección estable configurada.
- [ ] Acceso LAN reconfirmado después de la reserva.
- [ ] Puesto real de la secretaria probado con su cuenta.
- [ ] Dispositivo real de George probado por Tailscale.
- [ ] PC servidor no entrará en suspensión durante el horario acordado.
- [ ] Persona de contacto definida si falla LAN, Wi-Fi o Tailscale.

## Módulos incluidos en el piloto

| Módulo | Uso durante el piloto | Responsable principal |
| --- | --- | --- |
| Login y roles | Ingreso con cuenta individual y validación del rol | Ambos |
| Dashboard | Consulta inicial y accesos permitidos | Ambos |
| Cuadre de caja | Apertura, conteo, consulta y cierre del día | Secretaria |
| Gastos de caja | Registro asociado al cuadre | Secretaria |
| Clientes | Alta y consulta necesarias para la jornada | Secretaria |
| Ventas de contado | Registro paralelo de ventas reales | Secretaria |
| Ventas a crédito | Solo si George aprueba que el proceso está listo | Secretaria |
| Cobros | Registro de abonos o pagos aplicables | Secretaria |
| Producción diaria | Registro de la producción informada | Secretaria |
| Inventario `entry`/`exit` | Entradas y salidas operativas, sin costos ni ajustes | Secretaria |
| Historial básico | Consulta para verificar registros del día | Secretaria / George |
| Reportes y exportaciones | Revisión y descarga de solo lectura | Solo George |

El piloto no cambia las separaciones del sistema: registrar una venta no
descarga inventario automáticamente; registrar producción no aumenta stock por
sí solo; y los datos deben conciliarse con el método actual.

## Módulos excluidos o restringidos

No son prioridad durante los primeros días y solo pueden revisarse por George
si existe una necesidad concreta:

- nómina;
- anticipos y préstamos;
- cambios de precios;
- fórmulas y costos;
- correcciones de cuadres cerrados por el operador;
- anulaciones;
- ajustes delicados de inventario;
- aplicación de producción y consumo de insumos;
- cambios masivos de datos;
- eliminación o desactivación de registros importantes;
- administración de usuarios y roles.

Que George tenga permiso técnico no convierte estas tareas en parte normal del
piloto. Toda intervención excepcional debe tener motivo, evidencia y resultado
en el registro de incidencias.

## Reglas del trabajo en paralelo

1. Cada operación incluida se registra en el ERP y en el método actual.
2. El método actual se mantiene disponible como continuidad operativa durante
   los cinco días.
3. La misma persona registra ambos lados en el momento o deja una referencia
   inequívoca para completar la conciliación.
4. Al cierre se comparan totales y movimientos; una diferencia no se corrige a
   ciegas.
5. Si el ERP falla, se continúa con el método actual y se anota la hora exacta
   desde la que quedó pendiente registrar.
6. El reingreso posterior de datos requiere autorización de George y control
   para evitar duplicados.
7. Ninguna jornada convierte al ERP en el único registro oficial.

## Criterios para iniciar el piloto

El Día 1 solo puede comenzar cuando:

- todas las casillas de pendientes obligatorios están cerradas;
- el Día 0 del [plan de cinco días](47-plan-piloto-5-dias.md) fue aprobado;
- la secretaria puede entrar con `operator` desde su equipo;
- George puede entrar con `admin_auditor` por Tailscale;
- el backup desatendido real fue comprobado;
- servidor, Docker, LAN y Tailscale están disponibles;
- el método actual y la plantilla de incidencias están preparados;
- se decidió si las ventas a crédito entran o quedan excluidas;
- George dejó registrada la autorización de inicio.

## Criterios de éxito

El piloto será exitoso si:

- completa los cinco días previstos sin incidentes críticos abiertos;
- el 100 % de las jornadas tiene conciliación entre ERP y método actual;
- caja, gastos y módulos usados coinciden o toda diferencia queda explicada;
- cada usuario opera únicamente con su cuenta y rol;
- no hay accesos administrativos de la secretaria;
- el backup diario esperado se confirma durante el período;
- las incidencias tienen gravedad, responsable, estado y resolución;
- la secretaria completa el flujo diario sin depender de una cuenta
  administrativa;
- George puede revisar cierres, reportes y evidencias;
- no se pierden datos ni se ejecutan restores o borrados.

## Criterios de pausa o detención

### Pausar una operación o un módulo

Pausar el módulo afectado y continuar con el método actual cuando:

- una pantalla no carga o repite errores;
- hay una diferencia que todavía no puede explicarse;
- una acción permitida muestra “No tienes permiso”;
- existe riesgo de duplicar una venta, cobro, gasto o movimiento;
- el acceso LAN o Tailscale falla de forma parcial;
- falta información para completar correctamente el registro.

### Detener todo el piloto

Detener nuevas entradas en el ERP cuando:

- se sospecha pérdida, corrupción o mezcla de datos;
- una persona accede a información o acciones fuera de su rol;
- se comparte o compromete una credencial;
- caja, ventas o cobros no pueden conciliarse y la diferencia es material;
- el servidor o la base presentan fallos repetidos;
- falla el backup y no se obtiene un respaldo verificado antes de continuar;
- el sistema queda indisponible durante una parte relevante de la jornada;
- aparece un incidente crítico o varios incidentes altos relacionados;
- George considera que continuar aumenta el riesgo operativo.

## Plan de contingencia

1. Dejar de crear o modificar registros en el módulo afectado.
2. Anotar hora, usuario, módulo y última operación conocida.
3. Continuar la operación únicamente con el método actual.
4. Informar a George y abrir una fila en
   [`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md).
5. Conservar capturas y documentos sin incluir contraseñas, tokens ni secretos.
6. No borrar datos, no repetir operaciones dudosas y no modificar históricos.
7. No ejecutar restore, rebuild, migraciones, seeds ni `docker compose down -v`
   como respuesta improvisada.
8. George decide si se reanuda el módulo, se extiende el piloto o se detiene.
9. Antes de volver al ERP, definir el punto de corte y cómo evitar registros
   duplicados.

## Registro y documentos de trabajo

- Operador: [`44-guia-piloto-secretaria-operador.md`](44-guia-piloto-secretaria-operador.md).
- George: [`45-guia-piloto-george-admin.md`](45-guia-piloto-george-admin.md).
- Incidencias: [`46-registro-incidencias-piloto.md`](46-registro-incidencias-piloto.md).
- Cronograma: [`47-plan-piloto-5-dias.md`](47-plan-piloto-5-dias.md).
- Cierre de pendientes:
  [`48-cierre-pendientes-pre-piloto.md`](48-cierre-pendientes-pre-piloto.md).
- Checklist ejecutable del Día 0:
  [`49-checklist-dia-0-piloto.md`](49-checklist-dia-0-piloto.md).
- Permisos vigentes:
  [`42-guia-operativa-permisos-usuarios.md`](42-guia-operativa-permisos-usuarios.md).

## Conclusión

Agua Activa ERP está técnicamente preparado para continuar el Día 0, pero el
corte 59B lo clasifica como **no listo** y **todavía no está autorizado el
inicio del piloto**. La autorización depende de corregir y comprobar el backup
diario desatendido, cerrar las credenciales definitivas y reglas de cuentas,
resolver o aceptar expresamente el riesgo DHCP, confirmar el servidor y probar
los accesos desde los dispositivos reales.

El eventual piloto será limitado, reversible en lo operativo mediante el
método actual y evaluado al final de cinco días. Su cierre no equivale
automáticamente a producción definitiva.
