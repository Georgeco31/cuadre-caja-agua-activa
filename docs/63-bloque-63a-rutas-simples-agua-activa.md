# 63 - Bloque 63A: Rutas Simples para Agua Activa

## Problema real

George comprobó que el flujo tradicional de carga, inventario, retorno y
cierre no representa el trabajo diario de Agua Activa. La operación usa una
hoja física llamada **Registro de venta - Agua purificada envasada**, con varios
viajes, clientes informales, ventas, fiados, abonos, gastos y dinero entregado.

63A incorpora **Rutas Simples** como módulo nuevo y recomendado. El módulo
tradicional permanece disponible como `legacy`; no fue eliminado ni
refactorizado.

## Decisión de separación

Las tablas `simple_route_*` forman un dominio operativo independiente:

- no crean registros en `sales` ni `sale_items`;
- no crean registros en `credit_payments` ni cartera formal;
- no crean `expenses` oficiales;
- no crean `inventory_movements` ni consultan stock disponible;
- el cliente formal, producto de catálogo, empleado y vehículo son referencias
  opcionales; siempre se conserva un snapshot o etiqueta operacional;
- un bidón lleno, vacío, prestado, devuelto, para rellenar o relleno mantiene
  categorías distintas.

Esta separación evita inventar clientes formales, inflar ventas oficiales,
crear cartera impropia o descontar inventario que todavía no tiene un flujo
físico confiable para rutas.

## Modelo

La migración preparada es `0029_simple_routes`, archivo
`0029_simple_route_sheets.py`, con nueve tablas:

1. `simple_route_sheets`: encabezado, estado, liquidación y vínculo opcional a caja.
2. `simple_route_trips`: viajes numerados de una hoja.
3. `simple_route_trip_items`: salidas y retornos por producto o etiqueta.
4. `simple_route_sales`: venta operativa contado, fiada o parcial.
5. `simple_route_sale_items`: detalle, cantidad, precio y subtotal calculado.
6. `simple_route_collections`: abonos libres o vinculados a un fiado de ruta.
7. `simple_route_expenses`: combustible, almuerzo, cola, retiro de tapas u otro.
8. `simple_route_audit_logs`: creador, acción, motivo y metadata de trazabilidad.
9. `simple_route_cash_receipts`: recepción única de efectivo en un cuadre abierto.

`unique(route_sheet_id)` en `simple_route_cash_receipts` y el bloqueo transaccional
de hoja/caja impiden recibir dos veces la misma ruta.

## Estados y permisos

La hoja recorre `draft -> in_progress -> settled`; también puede quedar
`cancelled` con motivo. Una hoja liquidada o cancelada no acepta edición
operativa libre.

| Acción | operator | admin_auditor |
| --- | --- | --- |
| Crear y consultar hojas | Sí | Sí |
| Agregar viajes, ventas, abonos y gastos | Sí, mientras sea editable | Sí |
| Ver cuadre operativo | Sí | Sí |
| Liquidar | No | Sí |
| Cancelar con motivo | No | Sí |
| Recibir efectivo en caja | No | Sí |
| Analytics global y dry-run 1 de agosto | No | Sí |

## Reglas de venta y fiado

- contado: `cobrado = total`, `saldo = 0`;
- fiado: `cobrado = 0`, `saldo = total`;
- parcial: `0 < cobrado < total`, `saldo = total - cobrado`;
- el total se calcula en backend con los subtotales de ítems;
- un abono enlazado no puede superar el saldo restante del fiado;
- el saldo restante se calcula dentro de Rutas Simples y nunca llega a
  `receivables` ni `credit_payments`.

## Fórmulas del cuadre

Por producto o etiqueta y categoría:

```text
vendido_físico = total_salido - total_regresado
diferencia_física = vendido_físico - vendido_registrado_en_ruta
```

El retorno acumulado nunca puede superar la salida acumulada. Varios viajes se
suman antes de validar y calcular.

Por dinero:

```text
efectivo_esperado = ventas_contado_cobradas
                  + cobros_parciales
                  + abonos_de_ruta
                  - gastos_de_ruta
diferencia_efectivo = dinero_entregado - efectivo_esperado
```

El cuadre es `pending` antes de liquidar, `balanced` sin diferencias,
`with_difference` si difiere producto o dinero, y `cancelled` si la hoja fue
cancelada.

## Integración controlada con caja

La integración no crea ventas, cobros ni gastos oficiales. Al liquidar, la hoja
muestra **Efectivo a ingresar a caja**. Un `admin_auditor` puede vincular ese
importe a un `cash_session` abierto de la misma fecha.

La recepción aparece en la pantalla del cuadre y en su historial como
**Rutas simples / referencia**. No se suma a `total_counted`: el dinero ya está
incluido físicamente en billetes y monedas, por lo que sumarlo otra vez
duplicaría caja. La tabla conserva hoja, sesión, monto, receptor y fecha.

Una hoja recibida en caja no puede cancelarse automáticamente. Requiere una
conciliación futura explícita; 63A no implementa anulaciones destructivas de
recepciones.

## API

Endpoints principales:

```text
GET/POST /api/v1/simple-routes
GET/PATCH /api/v1/simple-routes/{id}
POST /api/v1/simple-routes/{id}/trips
PATCH /api/v1/simple-routes/{id}/trips/{trip_id}
POST /api/v1/simple-routes/{id}/trips/{trip_id}/items
POST /api/v1/simple-routes/{id}/sales
POST /api/v1/simple-routes/{id}/collections
POST /api/v1/simple-routes/{id}/expenses
GET /api/v1/simple-routes/{id}/settlement
POST /api/v1/simple-routes/{id}/settle
POST /api/v1/simple-routes/{id}/cancel
POST /api/v1/simple-routes/{id}/cash-receipt
GET /api/v1/simple-routes/analytics
GET /api/v1/simple-routes/cleanup/august-1-route-sales-dry-run
GET /api/v1/cash-sessions/{id}/simple-route-cash-receipts
```

No existe endpoint de 63A que cree ventas o cobros oficiales.

## Pantallas

- `/dashboard/simple-routes`: lista rápida y métricas operativas separadas para admin;
- `/dashboard/simple-routes/new`: encabezado mínimo;
- `/dashboard/simple-routes/[id]`: viajes, ventas, abonos, gastos, cuadre,
  liquidación y caja;
- caja e historial muestran las recepciones como referencia separada.

El dashboard marca **Rutas simples (recomendado)** y conserva **Rutas
tradicionales (legacy)**.

## Estadísticas propias

El endpoint administrativo calcula por periodo: venta de ruta, contado/parcial
cobrado, fiado, abonos, gastos, efectivo esperado, entregado, diferencia,
ranking de zonas y vendedores, mejor día, tendencia diaria y hojas con
diferencias. No alimenta el dashboard de ventas oficiales.

## Brechas deliberadas

- No se anulan todavía ventas del 2026-08-01; solo existe dry-run.
- No hay sincronización con inventario, cartera, gastos ni ventas oficiales.
- La pantalla agrega una línea de producto por venta para minimizar pasos; el
  backend admite varias líneas para futuras interfaces.
- No se implementó edición/anulación granular de ventas, abonos o gastos de una
  hoja; después de liquidar todo queda bloqueado y auditado.
- La cancelación de una recepción ya vinculada a caja queda para un bloque de
  conciliación posterior.

## Resultado 63A-2: despliegue productivo controlado

El despliegue fue autorizado y ejecutado el 2026-08-06. Antes de migrar se
confirmó health completo en `0028_payroll_base` y se creó el backup manual
`agua-activa-postgres-20260806-003708.dump`, acompañado por `.sha256` y JSON.
El checksum coincidió, `pg_restore --list` aprobó y todos los artefactos quedaron
bajo `backups/`, ignorados por Git.

La imagen API nueva reportó una sola cabeza y se aplicó
`0028_payroll_base -> 0029_simple_routes` mediante
`prod-local-migrate.ps1`, sin seeds. Las nueve tablas `simple_route_*` fueron
confirmadas por catálogo. Después se construyó Web y se recrearon únicamente
`api` y `web` con `--no-deps`; el contenedor `db` conservó ID, hora de inicio y
`RestartCount=0`.

El validador productivo de PowerShell y su equivalente de shell se actualizaron
para esperar `0029_simple_routes`. El health final aprobó con cero fallos y cero
advertencias:

- `db`, `api` y `web`: `healthy`;
- API localhost, LAN `192.168.100.225` y Tailscale: OK;
- Web LAN y Tailscale: OK;
- Alembic: `0029_simple_routes`;
- PostgreSQL `5432`: no publicado.

### Huella de datos antes y después

| Tabla o dominio | Antes | Después |
| --- | ---: | ---: |
| `sales` | 321 | 321 |
| `credit_payments` | 15 | 15 |
| `customers` | 17 | 17 |
| `cash_sessions` | 2 | 2 |
| `cash_count_items` | 0 | 0 |
| `inventory_stocks` | 9 | 9 |
| `inventory_movements` | 21 | 21 |
| `payroll_runs` | 0 | 0 |
| `payroll_items` | 0 | 0 |
| `delivery_routes` | 3 | 3 |
| `route_loads` | 2 | 2 |
| `route_returns` | 1 | 1 |
| `route_closures` | 1 | 1 |
| `route_cash_receipts` | 1 | 1 |
| `simple_route_sheets` | ausente | 0 |
| `simple_route_sales` | ausente | 0 |
| `simple_route_collections` | ausente | 0 |
| `simple_route_expenses` | ausente | 0 |

No se crearon hojas, ventas, abonos, gastos o recibos de efectivo de Rutas
Simples. No se modificaron ventas oficiales, cobros, clientes, caja, inventario,
nómina ni rutas legacy.

### Humo, permisos y brechas

El login incorrecto mostró un mensaje claro y el formulario no quedó en
`Iniciando...`. Los endpoints productivos se comprobaron con tokens efímeros
generados dentro de API y no persistidos: ambos roles listan Rutas Simples;
`operator` recibe `403` en analytics, dry-run, nómina, panel gerencial y
exportación restringida. Los módulos existentes y sus rutas frontend principales
respondieron correctamente.

El dry-run fijo del 2026-08-01 identificó 14 candidatas, devolvió
`modified_records = 0` y no cambió conteos. No se anuló ninguna venta.

La sesión visual real quedó completada con las cuentas existentes, sin exponer
ni cambiar contraseñas:

- `admin_auditor` y `operator` ingresaron correctamente por localhost;
- `admin_auditor` ingresó por LAN `192.168.100.225`;
- `operator` ingresó por Tailscale `100.121.163.126`;
- admin vio el acceso recomendado, la lista vacía, analytics separada y el
  formulario de nueva hoja;
- operator vio el flujo operativo y no vio analytics ni acciones de liquidar,
  cancelar o recibir efectivo;
- los accesos directos de operator a nómina, panel gerencial y exportaciones
  mostraron el bloqueo frontend esperado;
- la lista de Rutas Simples no presentó desbordamiento horizontal en viewport
  móvil y las comprobaciones de consola terminaron con cero errores.

Queda pendiente únicamente cualquier ruta de prueba real, porque George no la
autorizó expresamente. No se creó ninguna hoja durante el humo visual.

Un downgrade productivo solo debe considerarse antes de registrar hojas reales;
después de crear datos, se requiere un plan de conservación y autorización.
