# 55 - Bloque 60C: corrección administrativa de fecha de ventas

## Contexto del piloto

Agua Activa ERP está en el Día 1 de un piloto controlado. El método manual
permanece activo en paralelo y los movimientos reales solo los registran sus
responsables. Durante la operación, George identificó un caso legítimo: una
venta real puede quedar registrada con fecha incorrecta sin que cliente,
productos, cantidades, precio, monto o pagos estén equivocados.

El Bloque 60C implementa una corrección limitada a la fecha de la venta. No
autoriza edición libre de ventas, no crea roles nuevos y no incluye pagos,
producción, insumos, inventario ni otros maestros.

## Problema y diferencia frente a anular

Anular declara que una venta dejó de ser válida y cambia su estado operativo.
Corregir la fecha conserva la venta válida y únicamente mueve su atribución
temporal. Obligar a anular y volver a registrar habría creado riesgo de
duplicados, cambios de precio, movimientos de cartera incoherentes y pérdida de
la identidad original.

La corrección:

- conserva el mismo `id` y `sale_number`;
- conserva cliente, ruta asociada, tipo, forma de pago, vencimiento y notas;
- conserva íntegramente las partidas, cantidades, precios y subtotales;
- conserva total, pagado, saldo y estado de crédito;
- conserva pagos y sus fechas;
- conserva el estado de anulación;
- añade una fila de auditoría, sin borrar ni duplicar la venta.

## Arquitectura encontrada

Las ventas de contado y a crédito comparten la tabla `sales`, el servicio de
ventas y el campo `sale_date`. Los reportes diarios, mensuales, gerenciales,
exportaciones y cartera consultan ese campo, por lo que reflejan
automáticamente la nueva fecha después de una corrección válida.

La tabla `correction_logs` existente pertenece exclusivamente a correcciones de
conteos de caja cerrados y guarda totales monetarios. Reutilizarla habría
mezclado entidades y perdido el contrato específico de la venta. Se creó una
auditoría dedicada.

## Migración y auditoría

La migración `0027_sale_date_corrections`, con
`down_revision = 0026_user_roles`, crea `sale_date_corrections` con:

- `id`;
- `sale_id`;
- `correction_type`, limitado a `date_change`;
- `previous_sale_date`;
- `new_sale_date`;
- `reason`;
- `created_by`;
- `created_at`.

La base exige motivo no vacío y fechas distintas. Los índices por venta y
usuario facilitan la trazabilidad. La escritura de auditoría y el cambio de
`sales.sale_date` ocurren en una sola transacción.

## Endpoint

```http
PATCH /api/v1/sales/{sale_id}/date
Authorization: Bearer <sesión admin_auditor>
Content-Type: application/json

{
  "new_sale_date": "2026-07-27",
  "reason": "La fecha fue digitada un día adelante"
}
```

La respuesta incluye la venta actualizada, el ID y tipo de corrección, fecha
anterior y nueva, motivo, usuario que corrigió y fecha/hora UTC.

## Permisos y errores

Solo `admin_auditor` puede usar el endpoint. `operator` recibe `403` antes de
consultar o modificar la venta:

```text
No tienes permiso para corregir ventas. Solicita autorización a George.
```

| Caso | Estado | Mensaje o comportamiento |
| --- | ---: | --- |
| Sin sesión | `401` | Autenticación requerida |
| Venta inexistente | `404` | `La venta no existe.` |
| Fecha o payload inválido | `422` | Validación de contrato |
| Misma fecha actual | `400` | `La nueva fecha debe ser diferente de la fecha actual.` |
| Motivo vacío | `422` | `El motivo de corrección es obligatorio.` |
| Venta anulada | `409` | `La venta anulada no puede corregirse.` |
| Carga con cierre financiero activo | `409` | `La fecha no puede corregirse porque la venta está ligada a un cierre.` |
| Fecha origen o destino con caja `closed/corrected` | `409` | `La fecha no puede corregirse porque la venta está ligada a un cierre de caja.` |

## Bloqueos y concurrencia

La venta se consulta con lock sobre `sales`, usando el patrón corregido en 60B.
Cuando existe una carga de ruta, también se bloquea la carga antes de comprobar
el cierre financiero. Esto serializa la corrección frente a la creación de un
cierre de ruta. Los cuadres de las fechas afectadas se consultan con lock y se
bloquea el cambio si alguno ya está cerrado o corregido.

No existe una entidad separada de “cierre de cartera” en el modelo actual. Una
venta a crédito con pagos puede corregirse si no está alcanzada por los cierres
anteriores. Los pagos no se editan, trasladan ni recalculan.

## Frontend

Las listas de ventas de contado y crédito muestran `Corregir fecha` únicamente
cuando el rol resuelto es `admin_auditor` y la venta está activa. El modal:

- identifica la venta y muestra la fecha actual;
- exige una fecha nueva distinta y válida;
- exige un motivo;
- explica que los demás datos se conservan;
- muestra el estado de envío y el resultado;
- vuelve a consultar la lista con los filtros vigentes.

`operator` no ve la acción. Si una llamada directa o una sesión desactualizada
recibe `403`, la interfaz muestra la instrucción de solicitar autorización a
George.

## Impacto en caja, cartera y reportes

### Caja

La corrección no crea ingresos, egresos, conteos ni denominaciones. Cambia la
fecha usada como referencia por los reportes de ventas. Para proteger historia
conciliada, no se permite mover desde o hacia una fecha con cuadre cerrado o
corregido.

### Cartera

El saldo, total pagado, estado de crédito, cliente y vencimiento no cambian.
Los abonos conservan `payment_date`, monto, forma de pago y estado. Los
reportes presentan la venta en la fecha nueva y los pagos en sus fechas
originales.

### Reportes

Los reportes filtran `Sale.sale_date`; después de confirmar, la venta deja de
contar en la fecha anterior y cuenta en la nueva. No se modificaron fórmulas de
reportes ni exportaciones.

## Pruebas implementadas

Backend:

- contado y crédito corregibles por `admin_auditor`;
- `403` específico para `operator` y `401` sin sesión;
- motivo/fecha inválidos, misma fecha y venta inexistente;
- venta anulada, cierre de ruta y cierre de caja bloqueados;
- auditoría completa con usuario y timestamp;
- venta e ítems sin duplicación ni cambios;
- pagos de crédito inmutables;
- reporte diario en fecha anterior y nueva;
- anulación posterior a la corrección sin regresión;
- revisión de la cadena de la migración 0027.

Frontend:

- acción visible solo para admin sobre ventas activas;
- acción oculta para operator y ventas anuladas;
- validación de fecha y motivo;
- traducción clara del `403`;
- integración del modal en contado y crédito;
- recarga de lista y mensaje de éxito.

## Validaciones ejecutadas

| Validación | Resultado |
| --- | --- |
| Pruebas dirigidas de corrección y permisos | 58 aprobadas |
| Suite backend completa | 989 aprobadas |
| Pruebas frontend | 13 aprobadas |
| `npm run typecheck` | Aprobado |
| `npm run build` | Aprobado; 38 rutas |
| Compose productivo `config --quiet` | Aprobado |
| Alembic PostgreSQL 16 temporal | Upgrade 0026→0027, downgrade 0027→0026 y segundo upgrade aprobados |
| Health productivo previo | OK; `db`, `api` y `web` saludables; Alembic productivo sigue en 0026 |
| `git diff --check` | Aprobado |
| Staging | Vacío |

Permanece únicamente el warning conocido de deprecación
`TestClient/httpx` y los avisos informativos de Node sobre módulos TypeScript
sin `"type": "module"`; no causaron fallos. El PostgreSQL temporal se eliminó
al terminar y no contenía datos reales.

## Despliegue productivo controlado 60C-2

George autorizó el backup y el despliegue técnico el 2026-07-29. Antes de
migrar se generó el juego
`agua-activa-postgres-20260729-042822` (`.dump`, `.sha256` y `.dump.json`);
aprobaron checksum y `pg_restore --list`, y `backups/` continuó ignorado por
Git.

Se construyeron las imágenes de `api` y `web`, se aplicó explícitamente la
migración `0026_user_roles` → `0027_sale_date_corrections` y se recrearon solo
esos dos servicios con `--no-deps`. No se reinició `db`: el identificador del
contenedor y su hora de inicio permanecieron iguales antes y después. Tampoco
se usaron restore, seeds, `down -v`, eliminación de volúmenes ni cambios en
`.env.production.local`.

El primer health posterior detectó que el propio control todavía esperaba
`0026_user_roles`; no era un fallo del despliegue. Se actualizó
`scripts/prod-local-health.ps1` para exigir `0027_sale_date_corrections` y la
repetición terminó sin fallos ni advertencias.

| Comprobación productiva posterior | Resultado |
| --- | --- |
| Contenedores `db`, `api` y `web` | Saludables |
| API localhost, LAN y Tailscale | OK |
| Web LAN y Tailscale | OK |
| Alembic | `0027_sale_date_corrections` |
| PostgreSQL en host | Puerto `5432` no publicado |
| Conteos previos/posteriores | Sin cambios: 2 usuarios, 285 ventas, 293 partidas, 14 abonos y 1 sesión de caja |
| Tabla de auditoría | Existe con el esquema esperado; 0 registros antes de una corrección autorizada |
| Git | Backup ignorado; staging vacío |

La interfaz de login cargó en localhost, LAN
(`192.168.100.220`) y Tailscale (`100.121.163.126`). Un intento deliberadamente
inválido mostró el error controlado y volvió a habilitar el botón; una ruta del
panel sin sesión redirigió al login. No había una sesión autenticada disponible
en el navegador de validación, por lo que no se usaron ni inspeccionaron
credenciales.

Las pruebas automatizadas siguen cubriendo la visibilidad y autorización por
rol, incluido el `403` de `operator`. La comprobación visual productiva con
`admin_auditor` y `operator`, la corrección de una venta real autorizada y su
conciliación en reportes permanecen como pasos operativos pendientes. Este
bloque no modificó ninguna venta ni creó registros de auditoría.

## Estado final del Bloque 60C

La capacidad está implementada y desplegada; producción quedó saludable en
`0027_sale_date_corrections`. Permanece pendiente exclusivamente la validación
operativa con sesiones reales por rol y una venta expresamente autorizada,
incluida su auditoría y conciliación en reportes. Hasta completarla, el método
manual paralelo permanece activo.
