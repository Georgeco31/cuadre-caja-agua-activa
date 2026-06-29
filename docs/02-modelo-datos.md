# 02 - Modelo de Datos Inicial

Este documento describe el modelo de datos inicial del MVP. Todavia no representa modelos SQLAlchemy reales ni migraciones Alembic.

## users

Usuarios que podran crear o corregir cuadres en una etapa futura.

Campos:

| Campo | Descripcion |
| --- | --- |
| `id` | Identificador unico del usuario. |
| `username` | Nombre de usuario. |
| `password_hash` | Hash de la contrasena. |
| `is_active` | Indica si el usuario esta activo. |
| `created_at` | Fecha y hora de creacion. |

Notas:

- La autenticacion no se implementa en el Bloque 0.
- El modelo se documenta para preparar trazabilidad futura.

## cash_sessions

Representa un cuadre diario de caja.

Campos:

| Campo | Descripcion |
| --- | --- |
| `id` | Identificador unico del cuadre. |
| `session_date` | Fecha del cuadre. |
| `status` | Estado del cuadre. |
| `notes` | Notas generales del cuadre. |
| `created_by` | Usuario que creo el cuadre. |
| `created_at` | Fecha y hora de creacion. |
| `updated_at` | Fecha y hora de ultima actualizacion. |
| `closed_at` | Fecha y hora de cierre. |

Notas:

- Debe existir un solo cuadre principal por fecha.
- El estado permitira diferenciar cuadres abiertos y cerrados.

## denominations

Catalogo de denominaciones de monedas y billetes.

Campos:

| Campo | Descripcion |
| --- | --- |
| `id` | Identificador unico de la denominacion. |
| `type` | Tipo de denominacion: moneda o billete. |
| `value` | Valor monetario de la denominacion. |
| `label` | Texto visible para identificar la denominacion. |
| `is_active` | Indica si la denominacion esta activa. |

Notas:

- No se documentan valores especificos para evitar inventar datos del negocio.
- Las denominaciones se usaran para calcular subtotales.

## cash_count_items

Detalle del conteo de monedas y billetes dentro de un cuadre.

Campos:

| Campo | Descripcion |
| --- | --- |
| `id` | Identificador unico del item. |
| `cash_session_id` | Cuadre al que pertenece el item. |
| `denomination_id` | Denominacion contada. |
| `quantity` | Cantidad contada. |
| `subtotal` | Resultado de `quantity * denomination.value`. |

Notas:

- La cantidad debe ser mayor o igual a cero.
- El subtotal debe ser calculado por el sistema.

## expenses

Gastos realizados con dinero de caja y asociados a un cuadre.

Campos:

| Campo | Descripcion |
| --- | --- |
| `id` | Identificador unico del gasto. |
| `cash_session_id` | Cuadre al que pertenece el gasto. |
| `description` | Descripcion del gasto. |
| `amount` | Monto del gasto. |
| `category` | Categoria del gasto. |
| `expense_date` | Fecha del gasto. |
| `notes` | Notas adicionales. |
| `created_at` | Fecha y hora de creacion. |

Notas:

- El monto debe ser mayor a cero.
- Los gastos se restan del total contado para obtener el total final.

## correction_logs

Registro de correcciones realizadas sobre un cuadre.

Campos:

| Campo | Descripcion |
| --- | --- |
| `id` | Identificador unico del registro de correccion. |
| `cash_session_id` | Cuadre corregido. |
| `reason` | Motivo de la correccion. |
| `previous_total` | Total anterior antes de la correccion. |
| `new_total` | Total nuevo despues de la correccion. |
| `created_by` | Usuario que realizo la correccion. |
| `created_at` | Fecha y hora de creacion. |

Notas:

- Debe usarse cuando un cuadre cerrado requiera cambios.
- No debe reemplazar ni borrar la informacion historica importante.

## Relaciones iniciales

- Un `cash_session` puede tener muchos `cash_count_items`.
- Un `cash_session` puede tener muchos `expenses`.
- Un `cash_session` puede tener muchos `correction_logs`.
- Un `cash_count_item` pertenece a una `denomination`.
- Un `cash_session` puede estar asociado a un `user` mediante `created_by`.
- Un `correction_log` puede estar asociado a un `user` mediante `created_by`.

## Totales calculados

Los totales no deben escribirse manualmente.

- Total monedas = suma de subtotales donde la denominacion es moneda.
- Total billetes = suma de subtotales donde la denominacion es billete.
- Total contado = total monedas + total billetes.
- Total gastos = suma de gastos.
- Total final = total contado - total gastos.
