# Bloque 63C: exportaciones Excel de Rutas Simples

Fecha de implementación: 2026-08-07.

## Problema detectado

El centro de exportaciones todavía ofrecía **Rutas** usando el flujo histórico
de cargas, retornos y cierres. Después de 63A y 63B, esa opción podía llevar a
George a descargar un reporte que no representa la hoja diaria nueva.

Rutas Simples ya conserva en tablas propias los viajes, ventas, fiados, abonos,
gastos y liquidaciones. Faltaba una salida gerencial y auditable que usara ese
dominio sin mezclar ventas oficiales, cartera formal, caja ni inventario.

## Decisión

Toda exportación nueva de rutas usa únicamente hojas y movimientos
`simple_route_*`. El backend legacy se mantiene por compatibilidad, pero la
opción **Rutas** anterior se retiró del selector visible de Excel. El nuevo
bloque **Rutas Simples** identifica expresamente su origen y muestra esta nota:

> Estas exportaciones usan únicamente Rutas Simples. No incluyen ventas
> oficiales, cartera formal ni inventario.

No se cambian cálculos ni registros de ventas oficiales, cobros oficiales,
cartera, caja, inventario o nómina. 63C es de solo lectura y no requiere
migración.

## Exportaciones agregadas

| Exportación | Endpoint | Contenido principal |
| --- | --- | --- |
| Resumen de Rutas Simples | `GET /api/v1/reports/exports/simple-routes-summary.xlsx` | Indicadores, rutas y ranking de vendedores/zonas |
| Detalle de Ruta Simple | `GET /api/v1/reports/exports/simple-routes/{route_sheet_id}.xlsx` | Encabezado, viajes, ventas, abonos, gastos y cuadre |
| Ventas de Ruta | `GET /api/v1/reports/exports/simple-route-sales.xlsx` | Resumen por tipo y detalle por producto |
| Fiados de Ruta | `GET /api/v1/reports/exports/simple-route-pending.xlsx` | Ventas activas con saldo actual pendiente |
| Abonos de Ruta | `GET /api/v1/reports/exports/simple-route-collections.xlsx` | Abonos propios de Rutas Simples |
| Gastos de Ruta | `GET /api/v1/reports/exports/simple-route-expenses.xlsx` | Gastos propios de Rutas Simples |
| Cuadres de Ruta | `GET /api/v1/reports/exports/simple-route-settlements.xlsx` | Efectivo y diferencias físicas por ruta/producto |

Todos los endpoints generan `.xlsx` reales en memoria, agregan
`Cache-Control: no-store` y usan la misma sanitización de celdas del módulo de
Excel. Los textos que empiezan por `=`, `+`, `-`, `@`, tabulación o retorno se
escapan para evitar fórmulas maliciosas.

## Filtros

Los reportes por período aceptan `start_date` y `end_date`, ambos opcionales e
inclusivos. Un rango invertido devuelve `400`.

- `seller`: coincidencia parcial sin distinguir mayúsculas;
- `route_label`: coincidencia parcial de ruta o zona;
- `status`: `draft`, `in_progress`, `settled` o `cancelled`, disponible en
  resumen y cuadres;
- `sale_type`: `cash`, `credit`, `partial` o `all`, disponible en ventas;
- `route_sheet_id`: entero positivo obligatorio para el detalle.

El detalle de una hoja inexistente devuelve `404`. Los valores de filtro no
válidos devuelven `400`.

## Reglas de datos y cálculos

- Solo se procesan `simple_route_sheets`, viajes, partidas de viaje, ventas,
  partidas de venta, abonos y gastos de Rutas Simples, más las referencias de
  vendedor/vehículo ya asociadas a la hoja.
- No se consultan `route_loads` ni `route_closures` para estos reportes.
- No se agregan `sales`, `credit_payments`, cartera formal ni movimientos o
  saldos de inventario.
- Las ventas anuladas no participan en cálculos.
- Las hojas canceladas aparecen identificadas en resumen, cuadres o detalle,
  pero no inflan totales principales ni exportaciones de actividad.
- Los montos se calculan con `Decimal`; no se convierten a `float`.
- El saldo pendiente es `pending_amount` menos abonos enlazados, con mínimo
  cero.
- El efectivo esperado conserva la regla de 63A:

```text
efectivo esperado = contado cobrado
                  + parcial cobrado
                  + abonos de ruta
                  - gastos de ruta

diferencia efectivo = efectivo entregado - efectivo esperado
```

Si no hay información, el libro sigue siendo válido y contiene un mensaje
claro como **Sin Rutas Simples en el período**.

## Estructura de los libros

### Resumen

- `Resumen`: período, conteos por estado, ventas, fiado, abonos, gastos,
  efectivo esperado/entregado, diferencia y fecha de generación.
- `Rutas`: una fila por hoja con vendedor, vehículo, zona, estado y cifras de
  liquidación.
- `Top vendedores y rutas`: cantidad de rutas, ventas, efectivo entregado y
  diferencia.

### Detalle individual

- `Encabezado`: identidad y estado de la hoja, observaciones y efectivo.
- `Viajes`: salidas y regresos por producto/etiqueta.
- `Ventas`: cliente, tipo, producto, cantidad, precio, cobrado y saldo.
- `Abonos` y `Gastos`: movimientos propios de la hoja.
- `Cuadre`: salido, regresado, vendido físico/registrado y diferencias de
  producto y efectivo.

### Reportes especializados

- Ventas: `Resumen ventas ruta` y `Detalle ventas`.
- Fiados: `Fiados pendientes`.
- Abonos: `Abonos de ruta`.
- Gastos: `Gastos de ruta`.
- Cuadres: `Cuadres por ruta` y `Diferencias de producto`.

Las hojas usan encabezados congelados, autofiltros, ancho automático y formatos
de fecha, dinero y cantidad compatibles con `openpyxl`.

## Frontend y rutas anteriores

`/dashboard/exports` incorpora una sección independiente con filtros de fecha,
vendedor, zona, estado y tipo de venta. El detalle usa un selector de hojas
existentes; si no hay rutas, se explica que los reportes por período pueden
descargarse vacíos y que el detalle requiere una hoja.

El selector Excel general ya no muestra la exportación de rutas anteriores.
Su endpoint `/reports/exports/routes.xlsx` continúa disponible para
compatibilidad técnica, pero no es el flujo recomendado ni la base de 63C.

## Permisos

El router completo `/reports/exports` conserva la dependencia
`require_admin_auditor`:

| Rol | Ver la pantalla | Descargar cualquier XLSX 63C |
| --- | --- | --- |
| `admin_auditor` | Sí | Sí |
| `operator` | No | `403` |

El backend sigue siendo la autoridad aunque alguien intente una URL directa.

## Pruebas

Las pruebas automatizadas de 63C cubren:

- libros vacíos válidos y cargables con `openpyxl`;
- permisos de administrador y `403` de operador en los siete destinos;
- resumen con contado, fiado, parcial, abono, gasto y diferencia;
- exclusión de una ruta cancelada de totales principales;
- las seis hojas del detalle, `404` y sanitización contra fórmulas;
- ventas, saldos pendientes, abonos, gastos y diferencias físicas/efectivo;
- filtros de fecha, vendedor, zona, estado y tipo de venta;
- rangos y tipos inválidos;
- invariancia de tablas de Rutas Simples y módulos oficiales al exportar;
- catálogo, texto aclaratorio, endpoints, selección obligatoria y bloqueo
  frontend del operador.

Resultados de implementación:

- pruebas dirigidas backend 63C: **19 aprobadas**;
- suite backend completa: **1.056 aprobadas**, con un warning conocido de
  deprecación `TestClient/httpx`;
- frontend: **37 aprobadas**;
- `npm run typecheck`: aprobado;
- build Next.js de producción: aprobado, **40 rutas** generadas;
- Compose productivo `config --quiet`: aprobado;
- `scripts/prod-local-health.ps1`: **0 fallos y 0 advertencias**; `db`, `api` y
  `web` healthy; API localhost/LAN/Tailscale y Web LAN/Tailscale OK; PostgreSQL
  no publicado;
- Alembic productivo: `0029_simple_routes`;
- `git diff --check`: aprobado;
- staging vacío: no se ejecutó `git add`.

## Resultado 63C-2: despliegue productivo controlado

El despliegue fue autorizado y ejecutado el 2026-08-07. Los chequeos de health
anteriores y posteriores aprobaron con **0 fallos y 0 advertencias**. Se
construyeron y recrearon únicamente `api` y `web` con `--no-deps`; no se usó
`down`, no se ejecutó una migración y no se restauró ni sembró información.

PostgreSQL conservó exactamente el mismo contenedor
`fce8124dc998ce3df81197eed99b7af84b1b21ee230ff578599753039943953a`, iniciado
el `2026-08-05T13:47:07.5708977Z`, con `RestartCount=0`. Alembic permaneció en
`0029_simple_routes` y el puerto `5432` siguió sin publicarse.

Los conteos protegidos coincidieron antes, después y al terminar el humo:

| Tabla | Antes | Después/final |
| --- | ---: | ---: |
| `cash_count_items` | 0 | 0 |
| `cash_sessions` | 2 | 2 |
| `credit_payments` | 15 | 15 |
| `customers` | 17 | 17 |
| `inventory_movements` | 21 | 21 |
| `inventory_stocks` | 9 | 9 |
| `payroll_items` | 0 | 0 |
| `payroll_runs` | 0 | 0 |
| `sales` | 321 | 321 |
| `simple_route_collections` | 0 | 0 |
| `simple_route_expenses` | 0 | 0 |
| `simple_route_sales` | 0 | 0 |
| `simple_route_sheets` | 0 | 0 |

Validación autenticada de producción local:

- el login administrativo aprobó por localhost, LAN y Tailscale;
- credenciales inválidas mostraron un error claro y liberaron el botón de
  acceso;
- las seis exportaciones por período respondieron `200`, entregaron XLSX
  válidos y cargables con `openpyxl`, con hojas, cabeceras y estados vacíos
  esperados;
- el detalle de una hoja inexistente respondió `404` controlado; producción no
  contiene una ruta simple real y no se creó una para forzar el caso `200`;
- los libros no incluyeron etiquetas de ventas oficiales, cobros oficiales,
  inventario ni cartera formal;
- `management-dashboard.xlsx` y el endpoint legacy `routes.xlsx` continuaron
  entregando libros válidos;
- la sección mostró los siete destinos y el aviso de separación, ocultó la
  opción legacy del selector general, deshabilitó correctamente el detalle sin
  rutas y no presentó desbordamiento horizontal en móvil;
- el humo administrativo de dashboard, clientes, ventas de contado/crédito,
  cobros, caja, Rutas Simples, reportes, exportaciones y nómina aprobó por
  Tailscale; la consola del navegador terminó sin errores ni advertencias.

No se cambió ninguna credencial ni archivo de entorno y no se crearon rutas,
ventas, abonos, gastos, cuadres, roles de pago ni otros datos. La denegación
`403` y el ocultamiento para `operator` permanecen cubiertos por las pruebas
automatizadas; no había una credencial operativa disponible para repetir el
login visual sin alterar secretos.

## Brechas pendientes

- PDF específico de Rutas Simples.
- Formato imprimible equivalente a la hoja física.
- Exportación combinada de ventas oficiales + Rutas Simples, solo si George la
  solicita y aprueba su semántica.
- Publicación o conciliación definitiva con caja.
- Las rutas legacy siguen presentes por compatibilidad y quedan no
  recomendadas.
- Validar el XLSX de detalle `200` cuando exista una ruta simple real
  autorizada; en 63C-2 solo correspondía comprobar el `404` controlado.
- Repetir el humo visual manual con `operator` cuando se disponga de su
  credencial, sin rotarla ni exponerla.

## Procedimiento de despliegue ejecutado

63C no agrega tablas, columnas, constraints ni índices. Alembic debe permanecer
en `0029_simple_routes`; no se debe ejecutar `upgrade`, restore ni seed.

Con las validaciones y la autorización aprobadas, 63C-2 siguió este orden:

1. Comprobar health y confirmar `0029_simple_routes`.
2. Validar Compose con
   `docker compose -f docker-compose.prod.yml --env-file .env.production.local config --quiet`.
3. Construir las imágenes `api` y `web`.
4. Recrear únicamente `api` y `web` con `--no-deps`; no reiniciar `db` y no
   usar `down -v`.
5. Ejecutar `scripts/prod-local-health.ps1`, el humo administrativo de la
   sección y las descargas vacías; conservar la cobertura automatizada del
   `403` de operador si no hay credencial disponible.
6. Confirmar nuevamente Alembic, conteos protegidos y que no se crearon rutas.

El procedimiento quedó completado sin reiniciar `db`, modificar datos ni dejar
archivos temporales de las descargas.
