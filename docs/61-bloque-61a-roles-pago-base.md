# Bloque 61A: roles de pago base

## Contexto y objetivo

Agua Activa ERP ya contaba con empleados, asistencia, anticipos, préstamos,
abonos y un primer rol de pago congelado en el momento de creación. Ese flujo
solo distinguía `active/voided`: no permitía preparar un borrador, revisar,
aprobar, registrar el estado pagado ni aplicar de forma trazable los descuentos
al saldo correspondiente.

61A permite a `admin_auditor` crear un período, agregar o corregir empleados en
borrador, revisar sueldo, ingresos y descuentos, aprobar, marcar pagado y
cancelar con motivo. `operator` no ve ni puede usar nómina.

Este es un módulo interno base. No convierte el sistema en una nómina legal
ecuatoriana, no mueve caja o bancos y no ejecuta un pago real. Producción local
quedó migrada a `0028_payroll_base` durante el despliegue controlado 61A-2 del
29 de julio de 2026.

## Alcance y cálculo

Por empleado, el backend calcula:

```text
ingresos_totales = sueldo_base + bonos + otros_ingresos
descuentos_totales = anticipos + préstamos + otros_descuentos
neto_a_pagar = ingresos_totales - descuentos_totales
```

Todos los importes deben ser mayores o iguales a cero. El cliente no envía ni
sobrescribe el neto. Un neto negativo se rechaza.

El sueldo registrado en el empleado es el valor inicial y se conserva como
snapshot. `admin_auditor` puede ajustar `base_salary_amount` en el borrador sin
modificar el maestro del empleado; corregir un ítem exige motivo y genera
auditoría. El sistema no carga ni inventa sueldos.

La asistencia continúa como referencia congelada. No prorratea el sueldo ni
calcula consecuencias laborales.

### No incluido

- IESS.
- Décimos.
- Vacaciones.
- Fondos de reserva.
- Horas extra.
- Liquidaciones.
- Comisiones o fórmulas laborales legales.
- Firma del empleado.
- Comprobante individual.

Las exportaciones administrativas generales de nómina que ya existían se
mantienen. 61A no agrega un rol individual PDF/Excel ni un comprobante firmable.

## Modelo y migración

La nueva revisión es:

```text
0028_payroll_base
down_revision = 0027_sale_date_corrections
```

No duplica `payroll_runs`, `payroll_items` ni las tablas de vínculos.

### Roles

`payroll_runs` agrega:

- `label`;
- `approved_by`, `approved_at`;
- `paid_by`, `paid_at`;
- `cancelled_by`, `cancelled_at`;
- `cancellation_reason`.

`void_reason/voided_at` se renombran a
`cancellation_reason/cancelled_at`. La migración convierte:

| Estado anterior | Estado 0028 | Razón |
| --- | --- | --- |
| `active` | `approved` | El rol anterior era congelado, pero no demostraba pago |
| `voided` | `cancelled` | Conserva motivo y fecha |

No se asume que un rol histórico esté pagado. Para filas migradas se usa el
creador como actor disponible de aprobación o cancelación y se agrega un evento
que identifica la migración.

### Descuentos y auditoría

Se reutilizan `payroll_item_advance_deductions` y
`payroll_item_loan_deductions`. Ambos reciben `applied_at`; el vínculo de
préstamo recibe `loan_payment_id`.

`employee_advances` admite `active/deducted/voided` y agrega `deducted_at`,
`deducted_by` y `deducted_payroll_run_id`.

`employee_loan_payments` agrega `payroll_run_id`. Un abono generado por un rol
pagado no puede anularse por el endpoint normal porque rompería la inmutabilidad
del rol.

`payroll_audit_logs` registra creación, empleado agregado, ítem corregido con
valores antes/después, aprobación, pago y cancelación. Cada evento conserva
actor, fecha, motivo y detalle.

## Estados y reglas

| Estado | Editable | Aprobar | Pagar | Cancelar |
| --- | --- | --- | --- | --- |
| `draft` | Sí | Sí, con empleados | No | Sí, con motivo |
| `approved` | No | No | Sí | Sí, con motivo |
| `paid` | No | No | No | No |
| `cancelled` | No | No | No | No |

Un aprobado que necesita corrección se cancela con motivo y se reemplaza por
un nuevo borrador. No existe reapertura silenciosa de aprobados o pagados. No
hay endpoint para borrar roles o descuentos aplicados.

## Anticipos

1. Seleccionar un anticipo en `draft` solo lo reserva.
2. `draft` y `approved` impiden reservarlo en otro rol.
3. Cancelar libera la reserva sin cambiar el anticipo.
4. Aprobar no cambia su estado.
5. Marcar pagado lo cambia a `deducted` y registra actor, fecha y rol.
6. Un anticipo `deducted` no puede reutilizarse ni anularse.

El descuento es por el monto completo, de acuerdo con el modelo existente.

## Préstamos

1. Seleccionar una cuota en `draft` solo la reserva.
2. `draft` y `approved` impiden reservar simultáneamente el mismo préstamo en
   otro rol.
3. La cuota no puede exceder el saldo actual.
4. Cancelar libera la reserva sin cambiar el préstamo.
5. Aprobar no cambia el saldo.
6. Marcar pagado crea un `EmployeeLoanPayment`, reduce `balance_amount`,
   aumenta `paid_amount` y enlaza el abono al descuento.
7. Si el saldo llega a cero, el préstamo pasa a `paid`.
8. Con saldo restante puede participar en un rol futuro; cada cuota queda en
   un abono distinto y no puede aplicarse dos veces.

La acción de pago vuelve a comprobar el saldo bajo lock. Si un abono externo
dejó saldo insuficiente entre aprobación y pago, se rechaza toda la transacción.

## Cuándo se afectan saldos

| Acción | Anticipo | Préstamo |
| --- | --- | --- |
| Vista previa | Sin cambio | Sin cambio |
| Crear/editar borrador | Reserva | Reserva |
| Aprobar | Conserva reserva | Conserva reserva |
| Cancelar | Libera reserva | Libera reserva |
| Marcar pagado | Estado `deducted` | Crea abono y reduce saldo |

El rol y sus descuentos se confirman en una sola transacción. No se registra un
gasto, salida de caja, movimiento bancario ni pago real.

## Permisos

Solo `admin_auditor` puede listar, ver, previsualizar, crear, agregar/corregir
ítems, aprobar, marcar pagado, cancelar y consultar el resumen sensible por
empleado.

`operator` recibe:

```text
403 No tienes permiso para gestionar roles de pago.
```

Sin token se devuelve `401`. El backend sigue siendo la autoridad aunque el
frontend también oculte y bloquee la ruta.

## Endpoints

| Método | Ruta | Uso |
| --- | --- | --- |
| `POST` | `/api/v1/payroll/runs/preview` | Cálculo sin persistir |
| `GET` | `/api/v1/payroll/runs` | Lista y filtros |
| `POST` | `/api/v1/payroll/runs` | Crea borrador vacío o con ítems |
| `GET` | `/api/v1/payroll/runs/{id}` | Detalle, ítems y auditoría |
| `POST` | `/api/v1/payroll/runs/{id}/items` | Agrega empleado |
| `PATCH` | `/api/v1/payroll/items/{id}` | Corrige ítem con motivo |
| `POST` | `/api/v1/payroll/runs/{id}/approve` | Aprueba |
| `POST` | `/api/v1/payroll/runs/{id}/mark-paid` | Aplica descuentos |
| `POST` | `/api/v1/payroll/runs/{id}/cancel` | Cancela con motivo |
| `GET` | `/api/v1/payroll/employees/{id}/summary` | Sueldo, saldos y reservas |

`POST /api/v1/payroll/runs/{id}/void` queda como alias obsoleto de cancelación
para compatibilidad.

## Pantalla

`/dashboard/payroll` contiene:

- período, etiqueta y notas;
- selección y alta posterior de empleados;
- sueldo base editable en borrador;
- bonos, otros ingresos, anticipos, cuotas y otros descuentos;
- vista previa oficial;
- lista con estado, empleados, descuentos y neto;
- detalle responsive;
- edición auditada del ítem en borrador;
- acciones según estado;
- campos y eventos de auditoría.

Antes de marcar pagado se pide confirmación explícita y se recuerda que George
debe autorizar la acción.

## Pruebas

La cobertura incluye:

- borrador por administrador;
- `403` de `operator` y `401`;
- alta y corrección auditada de empleado;
- neto calculado en backend;
- negativos y neto negativo;
- bloqueo de aprobado/pagado;
- cancelación con motivo;
- auditoría de transiciones;
- reserva, liberación y no duplicación;
- saldo máximo de préstamos;
- abono enlazado al pagar;
- inmutabilidad de anticipos y abonos aplicados;
- resumen por empleado antes y después del pago;
- controles existentes de empleados, permisos y reportes;
- matriz de acciones frontend y bloqueo de URL;
- test, typecheck y build.

La migración fue probada el 29 de julio de 2026 en PostgreSQL 16 desechable:

```text
0027 -> 0028 -> 0027 -> 0028
```

Dos roles sintéticos comprobaron `active -> approved` y
`voided -> cancelled`, preservando el motivo. El primer intento detectó y
corrigió un literal SQL de auditoría; su transacción se revirtió antes de
repetir exitosamente todo el ciclo.

## Riesgos y brechas

- Un rol histórico `active` se interpreta como aprobado, nunca como pagado.
- Marcar pagado modifica saldos internos y requiere autorización operativa.
- Un abono manual entre aprobación y pago puede invalidar el saldo reservado.
- La revisión humana del período y sueldo sigue siendo obligatoria.
- Un rol pagado no tiene reversión automática en 61A.
- IESS, décimos, vacaciones, fondos de reserva, horas extra y liquidaciones no
  están implementados.
- Rol individual PDF/Excel, firma y comprobante individual no están
  implementados.
- Pago real o movimiento de caja/banco no está implementado.

## Evidencia del despliegue 61A-2

El 29 de julio de 2026 se ejecutó el despliegue productivo local autorizado:

- estado inicial y `git diff --check` aprobados, con staging vacío;
- health inicial con `db`, `api` y `web` saludables, localhost, LAN y
  Tailscale disponibles, PostgreSQL sin publicar y Alembic en
  `0027_sale_date_corrections`;
- backup `agua-activa-postgres-20260729-103636.dump` de 303.908 bytes;
- SHA256
  `a6d7f4ddefb5f154b3ebf347b5c71266ca300fe11d04d1e2347710b15c78801a`
  coincidente;
- metadata segura y `pg_restore --list` aprobados;
- imágenes `api` y `web` construidas antes de migrar;
- migración aplicada con el script seguro del proyecto, sin seeds ni restore;
- solo `api` y `web` fueron recreados;
- PostgreSQL conservó el mismo contenedor, hora de inicio
  `2026-07-28T04:43:27.981193771Z` y `RestartCount=0`;
- una sola cabeza y revisión actual `0028_payroll_base`;
- tabla de auditoría, campos de ciclo, vínculos y constraints de 0028
  verificados directamente;
- health final con cero fallos y cero advertencias en localhost, LAN y
  Tailscale.

La línea base y la comprobación posterior coincidieron:

| Control agregado | Antes | Después |
| --- | ---: | ---: |
| Empleados | 7 | 7 |
| Anticipos | 9 | 9 |
| Total de anticipos | 1460,00 | 1460,00 |
| Préstamos | 0 | 0 |
| Abonos de préstamo | 0 | 0 |
| Roles de pago | 0 | 0 |
| Ítems de rol | 0 | 0 |
| Eventos de auditoría de rol | No existía la tabla | 0 |

No se creó ningún rol real, no se marcó `paid`, no se aplicó descuento y no
se alteró ningún saldo.

El formulario de login cargó en localhost, LAN y Tailscale sin errores de
consola. En móvil no tuvo desbordamiento horizontal. Un login incorrecto mostró
`Usuario o contraseña incorrectos.` y salió de `Iniciando...`.

La contraseña `ADMIN_PASSWORD` del archivo de entorno no coincide con la cuenta
existente, comportamiento ya documentado porque el seed no rota contraseñas.
No se modificaron credenciales. George ingresó manualmente las credenciales
vigentes, sin compartirlas ni registrarlas, y el humo autenticado aprobó con
`admin_auditor` y `operator` en localhost, LAN/WiFi y Tailscale.

Con `admin_auditor`, el dashboard mostró 33 destinos y acceso a nómina. La
pantalla principal cargó los 7 empleados, los campos del borrador y el historial
vacío, sin errores de consola; también aprobó la revisión responsive en
escritorio y móvil. Clientes, ventas de contado y crédito, cobros, rutas, carga,
retorno, liquidación simple, caja, reportes y exportaciones administrativas
abrieron correctamente y sin escrituras.

Con `operator`, el dashboard mostró 22 destinos y no incluyó nómina. El intento
por URL directa en localhost, LAN/WiFi y Tailscale mostró `Acceso restringido`
y `No tienes permiso para gestionar roles de pago.`, sin errores de consola.
No se extrajo ni fabricó un token de sesión para forzar una petición productiva
directa al backend; por tanto, el `403` productivo específico de nómina queda
como brecha de evidencia manual. La frontera backend sí está cubierta por la
suite automatizada completa aprobada después del despliegue.

## Procedimiento de referencia para 61A-2

El procedimiento siguiente se ejecutó con autorización para 61A-2 y se
conserva como referencia operativa.

### Antes de la ventana

1. Confirmar que no hay cambios operativos en curso.
2. Confirmar el commit autorizado y staging vacío.
3. Confirmar `alembic heads` = `0028_payroll_base`.
4. Confirmar producción en `0027_sale_date_corrections`.
5. Crear backup manual custom con los scripts existentes.
6. Validar SHA256, metadata y `pg_restore --list`.
7. Guardar conteos seguros de roles, ítems, vínculos, anticipos, préstamos y
   abonos.
8. Validar:

   ```powershell
   docker compose -f docker-compose.prod.yml `
     --env-file .env.production.local config --quiet
   ```

### Despliegue

1. Reconstruir solo `api` y `web`, sin borrar volúmenes.
2. Ejecutar `alembic current` dentro de la API.
3. Aplicar `alembic upgrade 0028_payroll_base`.
4. Confirmar `alembic current`.
5. Recrear solo `api` y `web`.
6. No marcar ningún rol real como pagado durante el despliegue.

### Humo

1. Health de localhost, LAN y Tailscale.
2. Login `admin_auditor`.
3. Lista y detalle de un rol histórico migrado.
4. Confirmar que figura `approved`, no `paid`.
5. Crear/cancelar un borrador solo si George autoriza datos identificables de
   prueba.
6. Login `operator`: menú oculto, URL denegada y API `403`.
7. Verificar empleados, anticipos, préstamos y abonos.
8. Confirmar que caja, ventas, rutas, inventario y producción no cambiaron.

### Rollback

Antes de existir cualquier rol `paid` o rol vacío en 0028:

1. detener escrituras administrativas;
2. ejecutar `alembic downgrade 0027_sale_date_corrections`;
3. volver a la imagen anterior;
4. ejecutar health y humo por rol.

Después de existir un rol `paid`, 0028 bloquea deliberadamente el downgrade
para proteger los descuentos aplicados. También lo bloquea si existe un rol
vacío, porque `0027` exigía al menos un empleado. No debe forzarse ni borrarse
información. La salida segura es fix-forward o restore completo del backup de
la ventana, con autorización explícita y conciliación de todos los movimientos
posteriores.
