# 62 - Bloque 62A: métricas de clientes y dashboard

## Contexto

Agua Activa ERP está en piloto controlado. George necesita consultar cómo va el
negocio y cuánto se ha vendido a cada cliente sin alterar ventas, cobros, caja,
inventario, rutas o nómina. El método manual continúa activo en paralelo.

El Bloque 62A agrega únicamente lecturas, cálculos de backend, una exportación
Excel y componentes visuales. No crea tablas, no cambia datos y no requiere
migración. La revisión productiva debe conservar Alembic en
`0028_payroll_base`.

## Necesidades de George

- Ver contado, crédito, total vendido, cobrado sobre crédito y saldo pendiente
  de un cliente.
- Filtrar el historial del cliente por fecha.
- Exportar las ventas a crédito detalladas de un cliente.
- Ver en el dashboard principal del administrador total vendido, mezcla
  contado/crédito, cobros, cartera, gastos, mejor día, promedio diario,
  clientes atendidos, top clientes y tendencia diaria.
- Mantener separados los conceptos de ventas registradas, cobros recibidos,
  efectivo contado en caja y gastos.

## Alcance implementado

### Resumen por cliente

`GET /api/v1/customers/{customer_id}/sales-summary`

Filtros opcionales:

- `start_date`;
- `end_date`;
- `sale_type=cash|credit|all`;
- `status=active|voided`.

La respuesta incluye:

- cliente y período;
- cantidad y total de ventas de contado activas;
- cantidad y total de ventas a crédito activas;
- cantidad y total general de ventas activas;
- monto cobrado sobre las ventas a crédito seleccionadas;
- saldo pendiente actual de esas ventas a crédito;
- fecha de última venta activa;
- cantidad y total de anuladas como referencia separada.

Las anuladas nunca inflan los totales principales. Si el cliente no tiene
ventas, los montos regresan en cero, la última fecha es `null` y el detalle es
vacío.

### Detalle de ventas

`GET /api/v1/customers/{customer_id}/sales`

Acepta los mismos filtros. Reutiliza el contrato real de ventas y devuelve por
venta:

- ID, número y fecha;
- tipo, cliente y estado;
- productos con cantidad, precio unitario y subtotal;
- total, pagado y saldo;
- estado de crédito;
- carga y ruta cuando existen;
- notas y referencia de anulación.

Las pantallas de ventas de contado y crédito consultan el resumen cuando se
selecciona un cliente y se aplica el filtro. El bloque visual muestra contado,
crédito, total general, saldo pendiente, cobrado sobre crédito, cantidad de
ventas, última venta y anuladas separadas.

## Exportación de crédito por cliente

`GET /api/v1/reports/exports/customer-credit-sales.xlsx`

Parámetros:

- `customer_id`: obligatorio;
- `start_date`: opcional;
- `end_date`: opcional.

Permisos:

- `admin_auditor`: permitido;
- `operator`: `403`.

La pantalla `/dashboard/exports` incorpora la sección **Ventas a crédito por
cliente**, selector obligatorio, fechas opcionales y el botón **Exportar
crédito del cliente**.

El libro contiene:

1. **Resumen**: cliente, rango, total de crédito, total cobrado, saldo
   pendiente, número de ventas y fecha de generación.
2. **Detalle ventas crédito**: fecha, ID y número de venta, cliente, producto,
   cantidad, precio, subtotal, total de venta, cobrado, saldo, estado y
   observación.

La exportación incluye ventas a crédito activas. Las anuladas no se suman ni se
exportan como operaciones vigentes. Si no existen datos, el libro sigue siendo
válido y muestra `Sin ventas a crédito en el periodo`. Las celdas de texto pasan
por la sanitización existente contra fórmulas y caracteres ilegales.

## Métricas administrativas

`GET /api/v1/reports/admin-dashboard-analytics`

Filtros opcionales:

- `start_date`;
- `end_date`.

Sin filtros usa desde el primer día del mes actual hasta hoy. El endpoint está
protegido para `admin_auditor`; `operator` recibe `403`.

Datos incluidos:

- total de ventas activas registradas;
- ventas activas de contado;
- ventas activas a crédito;
- cobros de crédito activos cuya fecha de pago cae en el período;
- saldo pendiente actual de las ventas a crédito activas registradas en el
  período;
- gastos operativos activos registrados en el período;
- mejor día por total vendido;
- promedio vendido por día calendario del rango, incluyendo días sin ventas;
- cantidad de clientes identificados atendidos;
- top 5 clientes identificados por total vendido;
- serie de días con ventas, separada en contado y crédito;
- mezcla contado/crédito con monto y porcentaje.

La ruta `/dashboard` muestra estas métricas sólo a `admin_auditor`, con presets
de hoy, últimos 7 días, mes actual y rango personalizado. Se usan cards y barras
CSS/Tailwind responsivas, sin una dependencia de gráficos. El panel operativo
de `operator` conserva sus componentes actuales y no solicita ni renderiza las
métricas administrativas.

## Semántica de los datos

- **Venta registrada**: importe de una venta activa según `sale_date`.
- **Cobrado del cliente**: `paid_amount` actual de las ventas a crédito
  seleccionadas. Puede incluir abonos hechos fuera del rango si la venta está
  dentro del rango.
- **Cobros del dashboard**: abonos activos según `payment_date` dentro del
  rango.
- **Saldo pendiente**: `balance_amount` actual de las ventas a crédito activas
  seleccionadas.
- **Gastos**: gastos operativos activos según `expense_date`; no son gastos del
  cuadre ni efectivo contado.
- **Clientes atendidos/top clientes**: sólo ventas asociadas a un
  `customer_id`; “Consumidor final” sin cliente no se atribuye a un cliente.

`net_amount` se devuelve como `null` con una explicación. No se resta
automáticamente gasto a venta porque ventas registradas, cobros y efectivo no
son la misma base contable.

## Datos que no se inventan

- No se estima rentabilidad.
- No se infieren cobros desde caja.
- No se presenta el conteo físico como ventas.
- No se atribuye “Consumidor final” a un cliente ficticio.
- No se rellenan días sin registros con ventas simuladas.
- No se mezclan anuladas con operaciones activas.
- No se calcula neto contable ni flujo de efectivo.

## Pruebas realizadas

Resultado final local:

- 1.017 pruebas backend aprobadas; incluye 15 pruebas específicas de 62A;
- 27 pruebas frontend aprobadas;
- `npm run typecheck` aprobado;
- `npm run build` aprobado con 38 rutas generadas;
- Compose productivo válido;
- health productivo actual aprobado en DB/API/Web, localhost, LAN y Tailscale;
- Alembic confirmado en `0028_payroll_base`;
- PostgreSQL 5432 confirmado sin publicar;
- `git diff --check` aprobado.

La batería backend cubre cero ventas, contado, crédito, anuladas, fechas,
detalle con ítems, lectura por operador, Excel válido, libro sin datos, cliente
obligatorio, permisos de exportación, analytics, mezcla, mejor día, promedio,
top clientes, filtros, `403` y ausencia de mutaciones.

La batería frontend cubre las métricas del resumen, construcción de endpoints,
cliente obligatorio, rango inválido, presets, visibilidad por rol y estados de
carga, error, vacío y listo.

La única advertencia de pruebas es la deprecación preexistente de
TestClient/httpx, registrada como mantenimiento y no causada por 62A.

## Despliegue productivo 62A-2

62A-2 fue desplegado de forma controlada el 29 de julio de 2026. El comando de
actualización reconstruyó y recreó exclusivamente `api` y `web` con
`--no-deps`; no incluyó `db`, no ejecutó Alembic, no cambió variables de
entorno y no tocó volúmenes.

La evidencia antes y después fue:

- health productivo con `0` fallos críticos y `0` advertencias informativas;
- DB, API y Web saludables en ambos controles;
- API aprobada en localhost, LAN y Tailscale;
- Web aprobada en LAN y Tailscale;
- Alembic conservado en `0028_payroll_base`;
- PostgreSQL 5432 sin publicar;
- el contenedor DB conservó el mismo ID, la misma hora de inicio y
  `RestartCount=0`;
- API y Web recibieron IDs nuevos, como correspondía al alcance autorizado.

Huella de integridad productiva:

| Entidad | Antes | Después |
| --- | ---: | ---: |
| Ventas | 285 | 285 |
| Abonos de crédito | 14 | 14 |
| Clientes | 15 | 15 |
| Sesiones de caja | 1 | 1 |
| Rutas | 3 | 3 |
| Cargas de ruta | 0 | 0 |
| Devoluciones de ruta | 0 | 0 |
| Cierres de ruta | 0 | 0 |
| Recibos de efectivo de ruta | 0 | 0 |
| Roles de nómina | 0 | 0 |

La API desplegada expone las cuatro rutas de 62A en OpenAPI y las protege:
sin sesión, resumen, exportación y analytics respondieron `401`. Una prueba
productiva interna, encerrada en una sesión PostgreSQL `READ ONLY` y cerrada
con rollback, seleccionó un cliente real existente sin imprimir su identidad y
comprobó:

- 23 ventas en el detalle y en el resumen, con desglose de contado y crédito;
- analytics con ventas, contado, crédito, cobros, cartera, gastos, mejor día,
  top 5 y 23 puntos diarios;
- `net_amount=null`;
- libro Excel válido con las hojas **Resumen** y **Detalle ventas crédito**,
  detalle y fila de totales.

El navegador cargó el login en localhost, LAN y Tailscale. Un intento inválido
mostró el mensaje claro esperado y liberó el estado de carga; la consola no
registró errores. No había sesiones autenticadas abiertas para
`admin_auditor` u `operator`, por lo que no se buscaron credenciales ni se
extrajo o fabricó un token. La frontera por rol permanece comprobada por la
suite automatizada completa: 1.017/1.017 backend, 27/27 frontend, typecheck y
build productivo.

## Brechas pendientes

- Revisión visual autenticada del dashboard, resumen de cliente y descarga
  Excel con sesiones reales de `admin_auditor` y `operator`, incluyendo
  escritorio y móvil. Requiere ingreso manual sin compartir credenciales.
- Comprobación manual del `403` productivo específico con una sesión real de
  `operator`; la suite automatizada ya cubre esta frontera.
- Una contabilidad de rentabilidad o flujo de efectivo requiere reglas
  contables futuras; no forma parte de 62A.
- Las pruebas frontend actuales validan lógica y permisos con el arnés existente;
  el repositorio no incluye una librería de renderizado DOM/E2E.

## Procedimiento de despliegue

62A no contiene migraciones.

1. Confirmar autorización de George y método manual paralelo.
2. Ejecutar backup productivo y validar SHA256/listado según la guía vigente.
3. Ejecutar `git status --short` y `git diff --check`.
4. Validar Compose:

   ```powershell
   docker compose -f docker-compose.prod.yml --env-file .env.production.local config --quiet
   ```

5. Confirmar que Alembic sigue en `0028_payroll_base`. No ejecutar migración para
   62A.
6. Reconstruir y recrear sólo API y Web:

   ```powershell
   docker compose -f docker-compose.prod.yml --env-file .env.production.local up -d --build --no-deps api web
   ```

7. Ejecutar:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-health.ps1
   ```

8. Hacer humo por rol: resumen de cliente para ambos roles; exportación y
   analytics permitidos a admin; ambos `403` para operator; panel operativo del
   operador sin métricas gerenciales.
9. Confirmar que no cambiaron conteos ni saldos y que Alembic continúa en 0028.

No ejecutar `docker compose down -v`, restore, seed, carga inicial, cambio de
credenciales ni modificación de `.env.production.local`.
