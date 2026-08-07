# Bloque 63B: métricas de Rutas Simples en el dashboard

Fecha de implementación: 2026-08-07.

## Problema detectado por George

Después de desplegar Rutas Simples, George preguntó si las ventas registradas
en ese módulo aparecerían dentro del **Total vendido** del dashboard. El nombre
anterior era ambiguo porque representaba únicamente las ventas oficiales, pero
las rutas también registran ventas reales de la operación diaria.

Mezclar ambos orígenes dentro de la misma métrica habría contaminado ventas
oficiales, cartera, cobros, inventario y caja. Ocultar las rutas, en cambio,
habría dejado incompleta la lectura operativa del administrador.

## Decisión final

El dashboard de `admin_auditor` muestra tres conceptos explícitos:

1. **Ventas oficiales**: ventas contado oficiales más ventas crédito oficiales.
2. **Ventas de ruta**: ventas activas registradas en Rutas Simples.
3. **Total vendido con rutas**: Ventas oficiales más Ventas de ruta.

El dashboard presenta de forma visible la aclaración aprobada:

> Las rutas simples son control operativo separado. No afectan cartera formal,
> inventario ni ventas oficiales.

El campo histórico `total_sales_amount` se conserva por compatibilidad y sigue
significando únicamente ventas oficiales. La interfaz dejó de mostrar el nombre
ambiguo **Total vendido** para esa cifra.

## Reglas de cálculo

Todas las cantidades monetarias se redondean a dos decimales.

```text
ventas_oficiales = contado_oficial + crédito_oficial
ventas_de_ruta = suma(total_amount de ventas de ruta activas)
total_vendido_con_rutas = ventas_oficiales + ventas_de_ruta

efectivo_esperado_rutas = cobrado_al_registrar_ventas_de_ruta
                         + abonos_de_ruta
                         - gastos_de_ruta

diferencia_rutas = efectivo_entregado_rutas - efectivo_esperado_rutas
```

El desglose de Rutas Simples usa estas reglas adicionales:

- contado de ruta: total de ventas con `sale_type = cash`;
- venta fiada registrada: total de ventas con `sale_type = credit`;
- venta parcial: total de ventas con `sale_type = partial`;
- cobrado al vender: suma de `paid_amount` de las ventas activas;
- fiado de rutas visible: saldo pendiente actual de ventas fiadas y parciales,
  descontando abonos enlazados que pertenezcan a hojas no canceladas;
- abonos de ruta: movimientos de `simple_route_collections` de las hojas del
  período;
- gastos de ruta: movimientos de `simple_route_expenses` de las hojas del
  período;
- efectivo entregado: suma de `cash_delivered` cuando fue registrado;
- una diferencia sin dinero entregado aún se representa como cero en el total,
  porque todavía no existe base para compararla.

Crédito formal pendiente nunca incluye fiados de ruta. Cobros oficiales nunca
incluyen abonos de ruta. Gastos oficiales nunca incluyen gastos de ruta.

## Período, estados y cancelaciones

El rango se resuelve con los parámetros `start_date` y `end_date`. Sin
parámetros, conserva la regla 62A: desde el primer día del mes actual hasta hoy.

Para mantener coherencia con analytics de Rutas Simples, la pertenencia al
período se decide con `simple_route_sheets.route_date`. Entran hojas `draft`,
`in_progress` y `settled`, porque las dos primeras representan operación real
en curso y la última una liquidación concluida. Se excluyen por completo:

- hojas `cancelled`;
- ventas de ruta con estado `voided`;
- ventas oficiales y cobros oficiales anulados.

El saldo pendiente de una venta de ruta incluida refleja su saldo actual y por
ello considera todos sus abonos enlazados válidos, aunque el abono se haya
registrado después del período consultado. La métrica **Abonos de ruta** sí
representa únicamente las hojas incluidas en el período.

## Endpoint usado

Se extendió de forma compatible el endpoint de solo lectura ya consumido por
`/dashboard`:

```text
GET /api/v1/reports/admin-dashboard-analytics
```

No se agregó una segunda llamada. El endpoint continúa protegido por
`require_admin_auditor`; `operator` recibe `403` y no ve la sección gerencial en
el frontend.

Los campos 62A se conservan sin cambio semántico:

- `total_sales_amount`;
- `cash_sales_amount`;
- `credit_sales_amount`;
- `collections_amount`;
- `pending_credit_amount`.

Todos ellos siguen siendo exclusivamente oficiales.

## Métricas agregadas

- `official_sales_amount`;
- `official_cash_sales_amount`;
- `official_credit_sales_amount`;
- `official_credit_collections_amount`;
- `official_credit_pending_amount`;
- `simple_route_sales_amount`;
- `simple_route_cash_sales_amount`;
- `simple_route_credit_sales_amount`;
- `simple_route_partial_sales_amount`;
- `simple_route_paid_amount`;
- `simple_route_pending_amount`;
- `simple_route_collections_amount`;
- `simple_route_expenses_amount`;
- `simple_route_expected_cash_amount`;
- `simple_route_cash_delivered_amount`;
- `simple_route_cash_difference_amount`;
- `total_sales_with_routes_amount`;
- mejor día y tendencia diaria de ventas de ruta;
- top de rutas/zonas y vendedores;
- cantidad de hojas operativas y hojas con diferencia.

Cuando no existen rutas, el endpoint devuelve importes en `0.00`, listas vacías,
mejor día `null` y contadores en cero.

## Separaciones preservadas

### Ventas oficiales y ventas de ruta

La consulta lee ambos orígenes y solo los suma en
`total_sales_with_routes_amount`. No crea ni modifica registros de venta. Una
venta de ruta no entra en contado oficial ni en crédito oficial.

### Crédito formal y fiado de rutas

El saldo formal continúa saliendo de `sales.balance_amount`. El fiado de ruta
sale de `simple_route_sales.pending_amount` menos abonos válidos enlazados. No
se crean cuentas por cobrar ni registros de cartera formal.

### Cobros oficiales y abonos de ruta

Los cobros oficiales se leen de `credit_payments`. Los abonos de ruta se leen
de `simple_route_collections`. Ninguno alimenta al otro.

### Caja y efectivo de ruta

Efectivo esperado, entregado y diferencia son indicadores propios de la hoja de
ruta. Consultarlos no altera denominaciones, conteo físico, sesión de caja ni
resumen oficial. La referencia opcional de efectivo recibido sigue evitando el
doble conteo definido en 63A.

## Frontend

El componente gerencial del dashboard quedó organizado en tres secciones
responsive:

1. **Ventas oficiales**, con contado, crédito, cobros, saldo formal, gastos,
   tendencia, mezcla y top clientes oficiales.
2. **Rutas simples / operativo**, con ventas, contado, parciales, cobrado al
   vender, fiado, abonos, gastos, efectivo, diferencia, tendencia y rankings.
3. **Total vendido con rutas**, con comparación visual mediante barras CSS,
   sin agregar librerías de gráficos.

Se conservan los presets **Hoy**, **Últimos 7 días** y **Mes actual**, los
filtros por fecha y los estados loading, error y vacío. El layout usa grids
fluidos, `min-w-0` y texto adaptable para evitar desbordamiento en móvil.

## Permisos

| Capacidad | `operator` | `admin_auditor` |
| --- | --- | --- |
| Ver métricas gerenciales oficiales | No | Sí |
| Ver métricas gerenciales de Rutas Simples | No | Sí |
| Consultar endpoint administrativo | `403` | `200` |
| Usar el módulo operativo permitido de Rutas Simples | Sí | Sí |

## Pruebas realizadas

Validaciones ejecutadas durante la implementación:

- backend 63B + 62A + Rutas Simples: **35 aprobadas**;
- suite backend completa: **1.037 aprobadas**, con un warning conocido de
  deprecación `TestClient/httpx`;
- frontend: **33 aprobadas**;
- TypeScript `npm run typecheck`: aprobado;
- build Next.js de producción: aprobado, 40 rutas generadas;
- `docker compose -f docker-compose.prod.yml --env-file
  .env.production.local config --quiet`: aprobado;
- `scripts/prod-local-health.ps1`: **0 fallos y 0 advertencias**; `db`, `api` y
  `web` healthy; API localhost/LAN/Tailscale y Web LAN/Tailscale OK; PostgreSQL
  no publicado;
- Alembic productivo: `0029_simple_routes`;
- `git diff --check`: aprobado.

Las pruebas 63B cubren explícitamente:

- período sin rutas y respuesta en cero;
- ruta contado, fiada y parcial;
- separación de cobrado y pendiente;
- abonos, gastos, efectivo esperado, entregado y diferencia;
- ventas oficiales y total combinado;
- cartera/cobros oficiales sin datos de ruta;
- mejor día, tendencia, top rutas y top vendedores;
- exclusión de rutas canceladas y de fechas fuera del rango;
- restricción de `operator`;
- consulta sin modificación de datos.

## Migración y despliegue 63B-2

63B no cambia tablas, columnas, constraints ni índices. No se ejecutó
`upgrade`, `downgrade` ni restauración: Alembic permaneció en
`0029_simple_routes`.

El 2026-08-07 se construyeron las imágenes de `api` y `web` y se recrearon
exclusivamente esos dos servicios con `--no-deps --force-recreate`. No se usó
`down`, no se eliminaron volúmenes y el servicio `db` no formó parte del
comando. Su contenedor conservó el mismo ID, fecha de inicio, cero reinicios y
estado healthy antes y después del despliegue.

## Evidencia productiva de 63B-2

- El health previo y el posterior terminaron con **0 fallos y 0 advertencias**:
  `db`, `api` y `web` healthy; API por localhost, LAN
  `192.168.100.225` y Tailscale; Web por LAN y Tailscale; PostgreSQL 5432 no
  publicado.
- El login de `admin_auditor` respondió correctamente por API en localhost,
  LAN y Tailscale. Un login incorrecto devolvió `401` y la interfaz mostró
  `Usuario o contraseña incorrectos.` sin quedar detenida en `Iniciando...`.
- El dashboard autenticado de administrador se revisó visualmente en
  localhost, LAN y Tailscale. Mostró **Ventas oficiales**, **Ventas de ruta** y
  **Total vendido con rutas**, además de la nota de separación operativa. Las
  tres sesiones terminaron sin errores de consola.
- En producción no existen hojas de Rutas Simples. Las métricas operativas
  devolvieron ceros y listas vacías sin romper el dashboard; por ello el total
  combinado coincidió con el oficial, sin alterar sus componentes.
- El viewport móvil de `390 × 844` no presentó desbordamiento horizontal.
- El endpoint administrativo respondió a `admin_auditor`, conservó iguales los
  campos oficiales compatibles con 62A y cumplió la suma oficial + rutas. Un
  token efímero de la cuenta `operator`, sin persistir credenciales, obtuvo
  `200` en su panel operativo y en Rutas Simples, y `403` en analytics,
  nómina, reportes gerenciales y exportaciones restringidas.
- No se repitió el login visual de `operator` porque el entorno sólo dispone de
  credenciales administrativas configuradas y no había otra sesión iniciada.
  No se cambió ni restableció ninguna contraseña para forzar la prueba. La
  ausencia de métricas gerenciales para ese rol quedó cubierta por el humo API
  anterior y por la suite automatizada de permisos/frontend.
- Dashboard, clientes, ventas contado/crédito, cobros, caja, Rutas Simples,
  rutas anteriores, reportes, exportaciones y nómina administrativa
  respondieron `200` en el humo HTTP.

Conteos protegidos antes y después del despliegue y del humo visual:

| Entidad | Antes | Después |
| --- | ---: | ---: |
| `sales` | 321 | 321 |
| `credit_payments` | 15 | 15 |
| `customers` | 17 | 17 |
| `cash_sessions` | 2 | 2 |
| `cash_count_items` | 0 | 0 |
| `inventory_movements` | 21 | 21 |
| `inventory_stocks` | 9 | 9 |
| `payroll_runs` | 0 | 0 |
| `payroll_items` | 0 | 0 |
| `simple_route_sheets` | 0 | 0 |
| `simple_route_sales` | 0 | 0 |
| `simple_route_collections` | 0 | 0 |
| `simple_route_expenses` | 0 | 0 |

No se crearon rutas, ventas ni cobros; tampoco se modificaron caja, inventario,
nómina, credenciales ni archivos de entorno.

## Brechas pendientes

- Rutas Simples todavía no reemplaza reportes oficiales.
- Fiados de ruta no forman parte de cartera formal.
- Abonos de ruta no son cobros oficiales.
- Gastos de ruta no son gastos oficiales de caja.
- La integración definitiva con caja debe seguir controlada para evitar doble
  conteo.
- La impresión o formato final de hoja de ruta queda para un bloque futuro.

## Resultado

El administrador puede leer el negocio con una cifra oficial, una cifra
operativa de rutas y un total combinado inequívoco. La implementación es de
solo lectura y mantiene separados ventas, cartera, cobros, inventario y caja.

## Continuidad en el Bloque 63C

La brecha de Excel específico quedó atendida con siete exportaciones basadas en
Rutas Simples: resumen, detalle, ventas, fiados, abonos, gastos y cuadres. La
pantalla explica que no incluye ventas oficiales, cartera formal ni inventario,
y dejó de ofrecer la exportación legacy de rutas en el selector general.

63C es de solo lectura, conserva la protección exclusiva de
`admin_auditor`, no cambia cálculos del dashboard y no requiere migración.
63C-2 se desplegó el 2026-08-07 recreando solo `api` y `web`; `db`, Alembic y
los conteos quedaron intactos. Health, login administrativo, UI móvil y las
descargas vacías aprobaron sin crear rutas ni modificar datos. Ver
[`66-bloque-63c-exportaciones-rutas-simples.md`](66-bloque-63c-exportaciones-rutas-simples.md).
