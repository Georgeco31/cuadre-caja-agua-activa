# 13 - Auditoría general de Agua Activa ERP

## Ficha de la auditoría

- Fecha de corte: 2026-07-23.
- Bloque revisado: 44.
- Rama revisada: `main`.
- Último commit al iniciar la auditoría: `797b82b` (`Reportes Mensuales`).
- Alcance: estructura, stack, arquitectura, migraciones, rutas web, endpoints,
  módulos, reglas críticas, operación local, pruebas y riesgos.
- Fuentes: código versionado, OpenAPI generado por FastAPI, páginas de Next.js,
  scripts operativos, migraciones Alembic, pruebas automatizadas y
  documentación existente.

Este bloque es documental. No crea tablas, migraciones, seeds ni datos, y no
modifica la lógica de negocio.

## Conclusión ejecutiva

Agua Activa ERP tiene una base operativa amplia y coherente para ejecutar un
piloto supervisado con datos reales. Caja, catálogos, ventas, crédito, cobros,
inventario, producción y el ciclo básico de rutas están conectados mediante
flujos explícitos y trazables. El backend conserva los cálculos oficiales y
usa anulaciones lógicas en las operaciones sensibles.

El sistema todavía no debe considerarse un ERP completo ni una plataforma
lista para operación desatendida. Existen separaciones deliberadas entre
ventas, inventario, rutas y caja; no hay bancos, compras, proveedores, gastos
operativos generales, nómina, costos de producción completos, roles de acceso,
facturación ni reportes exportables. El uso inicial debe hacerse en paralelo
con los controles actuales y con backups verificados.

Estado recomendado: **apto para piloto controlado de 1 a 2 semanas, no apto
todavía para reemplazar todos los controles manuales ni para exposición
pública en Internet**.

## Estado general

### Implementado

- Autenticación JWT de un usuario administrador.
- Cuadre diario, denominaciones, conteos, gastos de caja, cierre, historial y
  correcciones trazables.
- Clientes, productos, empleados, rutas y vehículos como datos maestros.
- Ventas de contado y a crédito con detalle y anulación lógica.
- Abonos, cartera, resumen de cuentas por cobrar y estado de cuenta.
- Ubicaciones, stock y movimientos manuales de inventario.
- Producción, merma y aplicación reversible a inventario.
- Carga de camión y retorno con movimientos de inventario vinculados.
- Actividad comercial, cierre financiero y efectivo de ruta recibido en caja.
- Comparación de rutas contra caja.
- Resúmenes operativos diario y mensual de solo lectura.
- Scripts de arranque, apagado, health check, migración, seed, backup y
  restauración.
- Pruebas backend y validaciones de compilación frontend.

### Parcialmente implementado

- Caja: no hay bancos, conciliación automática, múltiples cajas o turnos.
- Productos y precios: existe precio base, pero no listas por cliente o ruta.
- Gastos: existen gastos dentro de un cuadre, pero no un módulo general fuera
  de caja con categorías, proveedores y recurrencias.
- Empleados: existe ficha base, pero no anticipos, asistencia, préstamos,
  pagos ni roles.
- Vehículos: existe catálogo y uso en rutas, pero no mantenimiento,
  combustible, kilometraje ni rentabilidad.
- Inventario: los movimientos de producción, carga y retorno son explícitos;
  las ventas no descargan stock automáticamente.
- Producción: no existen insumos, fórmulas, consumo de materia prima ni costos
  reales de producción.
- Reportes: existen reportes operativos, pero no gráficos, indicadores
  avanzados ni exportación Excel/PDF.
- Auditoría: varias anulaciones y correcciones conservan motivo y usuario, pero
  los cambios de todos los datos maestros no tienen un historial general.

### Pendiente o no implementado

- Compras y proveedores.
- Listas de precios por cliente y ruta, promociones y precios especiales.
- Gastos operativos generales fuera del cuadre de caja.
- Nómina, anticipos, asistencia, préstamos y roles de pago.
- Insumos, materia prima, fórmulas y costeo completo.
- Mantenimiento y control operativo de vehículos.
- Facturación y documentos tributarios.
- Bancos y conciliación.
- Descuento automático de inventario por ventas.
- Liquidación física completa del inventario de ruta.
- Recibos formales de cobro, cobros masivos y anticipos de clientes.
- Roles y permisos por usuario.
- Exportaciones, gráficos e indicadores gerenciales avanzados.
- Automatización de backups, monitoreo y despliegue productivo con HTTPS.

La matriz detallada está en
[`docs/17-matriz-modulos-erp.md`](17-matriz-modulos-erp.md).

## Stack usado

| Capa | Tecnología auditada |
| --- | --- |
| Frontend | Next.js 16.2.9, React 19.2.7, TypeScript 6.0.3 y Tailwind CSS 3.4.19 |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy 2.0 y Uvicorn |
| Migraciones | Alembic |
| Base de datos | PostgreSQL 16 Alpine en Docker Compose |
| Autenticación | JWT Bearer firmado con algoritmo configurable |
| Pruebas | Pytest y TestClient con SQLite en memoria |
| Contenedores | Python 3.12 Slim para API y Node.js 22 Alpine para web |
| Operación local | Docker Compose y scripts Bash |

Los rangos oficiales de dependencias backend viven en
`apps/api/pyproject.toml`; las versiones frontend están fijadas en
`apps/web/package-lock.json`. La auditoría no actualiza dependencias.

## Arquitectura general

```text
Navegador
  |
  | HTTP + JWT Bearer
  v
Next.js / React (apps/web)
  |
  | JSON bajo /api/v1
  v
FastAPI (apps/api/app/api)
  |
  +--> services: reglas y transacciones
  +--> repositories: consultas y persistencia
  +--> schemas: contratos de entrada y salida
  +--> models: modelo SQLAlchemy
  |
  v
PostgreSQL 16 (volumen Docker postgres_data)
```

La configuración local levanta tres servicios:

- `db`: PostgreSQL persistente.
- `api`: FastAPI, publicado por defecto en `http://localhost:8010`.
- `web`: Next.js, publicado por defecto en `http://localhost:3000`.

Los totales monetarios y de inventario oficiales se calculan en backend. El
frontend presenta estimaciones durante algunos formularios, pero vuelve a
consultar los valores persistidos.

## Guía de arranque y apagado local

Desde la raíz del proyecto:

```bash
./scripts/local-start.sh
./scripts/check-health.sh
```

Comprobar:

```text
http://localhost:8010/api/v1/health
http://localhost:3000/login
```

Si el código trae una migración nueva aprobada, hacer backup antes y aplicar
`./scripts/local-migrate.sh`. En el corte del Bloque 44 no hay migraciones
nuevas y no se debe crear ninguna.

Para apagar conservando PostgreSQL:

```bash
./scripts/local-stop.sh
```

El script ejecuta `docker compose down` sin `-v`; el volumen
`postgres_data` se conserva.

## Guía de backup y restauración

### Crear y comprobar un backup

```bash
./scripts/backup-db.sh
ls -lh backups/
```

El script usa `pg_dump --clean --if-exists` y genera
`backups/cuadre_caja_YYYYMMDD_HHMMSS.sql`. Confirmar fecha y tamaño mayor que
cero, copiar el archivo a un segundo medio seguro y no subirlo a Git.

### Restaurar

La restauración puede reemplazar objetos y datos. Antes de ejecutarla:

1. Detener la digitación.
2. Crear un backup del estado actual.
3. Verificar que el archivo corresponde a este proyecto y fecha.
4. Preferir un entorno aislado para la prueba.
5. Ejecutar, solo con autorización:

   ```bash
   ./scripts/restore-db.sh backups/nombre_backup.sql
   ```

6. Comprobar health, login, revisión Alembic y una muestra de cuadres,
   inventario, ventas y rutas.

No se realizó una restauración sobre la base local durante esta auditoría
porque habría sido una modificación destructiva fuera del alcance.

## Guía de pruebas manuales principales

Ejecutar con datos de prueba en una base separada antes del piloto real:

| Flujo | Prueba | Resultado esperado |
| --- | --- | --- |
| Acceso | Login válido, inválido y logout | Acceso solo con credenciales válidas; logout elimina la sesión |
| Caja | Crear cuadre, contar, registrar ambos tipos de gasto y cerrar | Un cuadre por fecha; solo `after_count` reduce el total final |
| Corrección | Corregir conteo cerrado con motivo | Cuadre sigue cerrado y aparece el log con total anterior/nuevo |
| Clientes/productos | Alta, edición, inactivación y reactivación | No hay borrado físico y los filtros reflejan el estado |
| Venta de contado | Registrar varios ítems y anular | Backend calcula total; la anulación conserva el registro |
| Crédito | Vender, abonar parcial/total y anular abono | Saldos se actualizan y la anulación restaura el saldo |
| Inventario | Entrada, salida, ajuste y anulación | No hay stock negativo; la reversión actualiza el stock |
| Producción | Crear lote, aplicar y revertir aplicación | Crear no mueve stock; aplicar y revertir sí lo hacen |
| Ruta | Cargar, vender/cobrar, retornar y cerrar | Movimientos, actividad y efectivo esperado son trazables |
| Ruta a caja | Registrar y anular dinero recibido | Se conserva trazabilidad sin cambiar el conteo oficial |
| Reportes | Revisar caja, cartera, diario, mensual y rutas vs caja | Los reportes son de solo lectura y coinciden con el detalle |
| Respaldo | Crear backup y restaurarlo en entorno aislado | El archivo es legible y los datos seleccionados reaparecen |

En cada prueba comprobar también:

- rechazo de datos inválidos;
- mensajes de error;
- recarga de la página;
- filtros y estados vacíos;
- bloqueo de operaciones con vínculos activos;
- conservación de motivos y registros anulados.

La secuencia diaria completa está en
[`14-checklist-uso-real-agua-activa.md`](14-checklist-uso-real-agua-activa.md).

## Migraciones actuales

La cadena es lineal y termina en `0018_route_receipts`.

| Archivo | Revisión | Revisión anterior | Propósito |
| --- | --- | --- | --- |
| `0001_create_initial_tables.py` | `0001_create_initial_tables` | ninguna | Usuarios, denominaciones, cuadres, conteos, gastos y correcciones |
| `0002_expense_timing.py` | `0002_expense_timing` | `0001_create_initial_tables` | Momento del gasto respecto al conteo |
| `0003_create_customers.py` | `0003_customers` | `0002_expense_timing` | Clientes |
| `0004_create_products.py` | `0004_products` | `0003_customers` | Productos y precio base |
| `0005_create_employees.py` | `0005_employees` | `0004_products` | Empleados |
| `0006_create_delivery_routes.py` | `0006_routes` | `0005_employees` | Rutas de entrega |
| `0007_create_vehicles.py` | `0007_vehicles` | `0006_routes` | Vehículos |
| `0008_create_cash_sales.py` | `0008_cash_sales` | `0007_vehicles` | Ventas de contado |
| `0009_add_credit_fields_to_sales.py` | `0009_credit_sales` | `0008_cash_sales` | Crédito y saldos de venta |
| `0010_create_credit_payments.py` | `0010_payments` | `0009_credit_sales` | Abonos |
| `0011_create_inventory.py` | `0011_inventory` | `0010_payments` | Ubicaciones, stock y movimientos |
| `0012_create_production.py` | `0012_production` | `0011_inventory` | Producción y merma |
| `0013_production_inventory.py` | `0013_prod_inventory` | `0012_production` | Aplicación de producción a inventario |
| `0014_create_route_loads.py` | `0014_route_loads` | `0013_prod_inventory` | Cargas de camión |
| `0015_create_route_returns.py` | `0015_route_returns` | `0014_route_loads` | Retornos de ruta |
| `0016_route_commercial_links.py` | `0016_route_links` | `0015_route_returns` | Vínculos comerciales con cargas |
| `0017_create_route_closures.py` | `0017_route_closures` | `0016_route_links` | Cierres financieros de ruta |
| `0018_create_route_cash_receipts.py` | `0018_route_receipts` | `0017_route_closures` | Dinero de ruta recibido en caja |

Verificación de la base local durante la auditoría:

```text
SELECT version_num FROM alembic_version;
0018_route_receipts
```

No se creó ni modificó ninguna migración en el Bloque 44.

## Rutas frontend

Se auditaron 26 archivos `page.tsx`, incluida la redirección raíz. Las páginas
bajo `/dashboard` verifican el token en el cliente y redirigen a `/login`
cuando falta o la API responde `401`/`403`.

| Ruta | Uso principal |
| --- | --- |
| `/` | Redirección a `/login` |
| `/login` | Inicio de sesión |
| `/dashboard` | Panel operativo y accesos rápidos |
| `/dashboard/monthly-summary` | Resumen operativo mensual |
| `/dashboard/daily-summary` | Resumen operativo diario |
| `/dashboard/cash-session` | Crear, consultar y cerrar cuadre |
| `/dashboard/history` | Historial de cuadres |
| `/dashboard/history/[cashSessionId]` | Detalle y correcciones de un cuadre |
| `/dashboard/reports` | Resumen acumulado de caja |
| `/dashboard/route-cash-comparison` | Comparación rutas contra caja |
| `/dashboard/route-cash-receipts` | Dinero de ruta recibido en caja |
| `/dashboard/customers` | Clientes |
| `/dashboard/products` | Productos y precio base |
| `/dashboard/employees` | Fichas base de empleados |
| `/dashboard/delivery-routes` | Rutas de entrega |
| `/dashboard/vehicles` | Vehículos |
| `/dashboard/inventory` | Ubicaciones, stock y movimientos |
| `/dashboard/production` | Producción y aplicación a inventario |
| `/dashboard/route-loads` | Cargas de camión |
| `/dashboard/route-returns` | Retornos de ruta |
| `/dashboard/route-activity` | Actividad comercial por carga |
| `/dashboard/route-closures` | Cierres financieros de ruta |
| `/dashboard/sales/cash` | Ventas de contado |
| `/dashboard/sales/credit` | Ventas a crédito |
| `/dashboard/receivables` | Cobros y abonos |
| `/dashboard/receivables/reports` | Resumen de cuentas por cobrar |
| `/dashboard/receivables/reports/[customerId]` | Estado de cuenta de cliente |

## Endpoints backend

El esquema OpenAPI auditado expone 81 plantillas de ruta y 103 operaciones
HTTP. De esas operaciones, 101 requieren JWT. Solo el login y el health check
son públicos.

La documentación interactiva de desarrollo está disponible en
`http://localhost:8010/docs` cuando la API está levantada.

### Autenticación y salud

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/health`

### Caja

- `GET, POST /api/v1/cash-sessions`
- `GET /api/v1/cash-sessions/by-date/{session_date}`
- `GET /api/v1/cash-sessions/{cash_session_id}`
- `GET, POST /api/v1/cash-sessions/{cash_session_id}/count-items`
- `GET, POST /api/v1/cash-sessions/{cash_session_id}/expenses`
- `POST /api/v1/cash-sessions/{cash_session_id}/corrections/count-items`
- `POST /api/v1/cash-sessions/{cash_session_id}/corrections/expenses`
- `GET /api/v1/cash-sessions/{cash_session_id}/corrections`
- `GET /api/v1/cash-sessions/{cash_session_id}/summary`
- `GET /api/v1/cash-sessions/{cash_session_id}/route-cash-receipts`
- `POST /api/v1/cash-sessions/{cash_session_id}/close`
- `GET /api/v1/denominations`

### Clientes, productos, empleados, rutas y vehículos

- `GET, POST /api/v1/customers`
- `GET, PATCH /api/v1/customers/{customer_id}`
- `PATCH /api/v1/customers/{customer_id}/deactivate`
- `PATCH /api/v1/customers/{customer_id}/activate`
- `GET, POST /api/v1/products`
- `GET, PATCH /api/v1/products/{product_id}`
- `PATCH /api/v1/products/{product_id}/deactivate`
- `PATCH /api/v1/products/{product_id}/activate`
- `GET, POST /api/v1/employees`
- `GET, PATCH /api/v1/employees/{employee_id}`
- `PATCH /api/v1/employees/{employee_id}/deactivate`
- `PATCH /api/v1/employees/{employee_id}/activate`
- `GET, POST /api/v1/delivery-routes`
- `GET, PATCH /api/v1/delivery-routes/{route_id}`
- `PATCH /api/v1/delivery-routes/{route_id}/deactivate`
- `PATCH /api/v1/delivery-routes/{route_id}/activate`
- `GET, POST /api/v1/vehicles`
- `GET, PATCH /api/v1/vehicles/{vehicle_id}`
- `PATCH /api/v1/vehicles/{vehicle_id}/deactivate`
- `PATCH /api/v1/vehicles/{vehicle_id}/activate`

### Ventas, cobros y cartera

- `POST /api/v1/sales/cash`
- `POST /api/v1/sales/credit`
- `GET /api/v1/sales`
- `GET /api/v1/sales/credit/customer/{customer_id}/balance`
- `GET /api/v1/sales/{sale_id}`
- `POST /api/v1/sales/{sale_id}/void`
- `GET, POST /api/v1/sales/{sale_id}/payments`
- `GET /api/v1/credit-payments`
- `POST /api/v1/credit-payments/{payment_id}/void`
- `GET /api/v1/receivables/summary`
- `GET /api/v1/receivables/customers`
- `GET /api/v1/receivables/overdue`
- `GET /api/v1/receivables/customers/{customer_id}/statement`

### Inventario y producción

- `GET, POST /api/v1/inventory/locations`
- `GET, PATCH /api/v1/inventory/locations/{location_id}`
- `PATCH /api/v1/inventory/locations/{location_id}/deactivate`
- `PATCH /api/v1/inventory/locations/{location_id}/activate`
- `GET /api/v1/inventory/stocks`
- `GET, POST /api/v1/inventory/movements`
- `GET /api/v1/inventory/movements/{movement_id}`
- `POST /api/v1/inventory/movements/{movement_id}/void`
- `GET, POST /api/v1/production/batches`
- `GET /api/v1/production/batches/{batch_id}`
- `POST /api/v1/production/batches/{batch_id}/void`
- `POST /api/v1/production/batches/{batch_id}/apply-inventory`
- `GET /api/v1/production/batches/{batch_id}/inventory-application`
- `POST /api/v1/production/inventory-applications/{application_id}/void`

### Ciclo de rutas

- `GET, POST /api/v1/route-loads`
- `GET /api/v1/route-loads/{load_id}`
- `GET /api/v1/route-loads/{load_id}/commercial-activity`
- `GET /api/v1/route-loads/{load_id}/financial-closure`
- `POST /api/v1/route-loads/{load_id}/void`
- `GET, POST /api/v1/route-returns`
- `GET /api/v1/route-returns/{return_id}`
- `POST /api/v1/route-returns/{return_id}/void`
- `GET, POST /api/v1/route-closures`
- `GET /api/v1/route-closures/{closure_id}`
- `GET /api/v1/route-closures/{closure_id}/cash-receipt`
- `POST /api/v1/route-closures/{closure_id}/void`
- `GET, POST /api/v1/route-cash-receipts`
- `GET /api/v1/route-cash-receipts/{receipt_id}`
- `POST /api/v1/route-cash-receipts/{receipt_id}/void`

### Reportes

- `GET /api/v1/reports/cash-summary`
- `GET /api/v1/reports/route-cash-comparison`
- `GET /api/v1/reports/daily-operational-summary`
- `GET /api/v1/reports/monthly-operational-summary`

## Reglas críticas de negocio

### Dinero y caja

- Usar precisión decimal; los totales oficiales se calculan en backend.
- Solo puede existir un cuadre por fecha.
- Un cuadre cerrado bloquea cambios normales.
- Las correcciones de cuadres cerrados requieren motivo y conservan los
  totales anterior y nuevo.
- Los gastos `before_count` se informan, pero no se restan del total contado.
- Los gastos `after_count` sí se restan del total contado.
- Registrar dinero de ruta recibido en caja no cambia denominaciones, conteos,
  gastos ni el total oficial del cuadre.

### Ventas, crédito y cobros

- Una venta de contado puede usar consumidor final; una venta a crédito exige
  cliente activo y habilitado para crédito.
- El backend calcula subtotales, total, monto pagado y saldo.
- Un abono no puede superar el saldo vigente.
- Anular un abono restaura el saldo de la venta.
- Las anulaciones conservan el registro y exigen motivo.
- Las ventas no descargan inventario automáticamente en el alcance actual.

### Inventario y producción

- No se permite stock negativo en salidas, ajustes negativos o reversiones.
- Crear producción no mueve inventario.
- Aplicar producción crea entradas por la cantidad producida menos la merma.
- Solo puede existir una aplicación activa por lote.
- Una aplicación debe revertirse antes de anular el lote.
- Las operaciones vinculadas se anulan desde su módulo de origen, no desde el
  movimiento de inventario aislado.

### Rutas

- Una carga exige ruta, vehículo y ubicaciones activas.
- La carga traslada stock del origen a una ubicación de vehículo.
- El retorno traslada stock del vehículo a una ubicación no vehicular.
- Solo puede existir un retorno activo por carga.
- El efectivo esperado de una ruta es ventas de contado más cobros; las ventas
  a crédito no se suman.
- Solo puede existir un cierre financiero activo por carga.
- Un cierre activo bloquea nuevas operaciones o anulaciones comerciales
  vinculadas a esa carga.
- El cierre de ruta no crea un cuadre ni mueve caja o inventario.
- Un recibo activo de dinero de ruta debe anularse antes de anular su cierre.
- La comparación rutas contra caja es informativa, no una conciliación
  contable definitiva.

### Trazabilidad

- No borrar movimientos sensibles para corregirlos.
- Usar inactivación para datos maestros y anulación con motivo para
  operaciones.
- No cambiar datos directamente en PostgreSQL durante la operación normal.
- Registrar el motivo real de cada corrección o anulación.

## Riesgos técnicos y operativos

| Nivel | Riesgo observado | Consecuencia | Mitigación inmediata |
| --- | --- | --- | --- |
| Alto | Ventas, inventario, rutas y caja no están conciliados automáticamente | Registrar una operación en un módulo no garantiza que los demás cambien | Seguir el orden del checklist y conciliar manualmente cada día |
| Alto | JWT en `localStorage`, un administrador y sin roles | Una sesión del navegador tiene acceso amplio; no es adecuado para exposición pública | Usar solo en equipos controlados y red confiable; planificar cookies seguras, roles y HTTPS |
| Alto | Backup manual, local y sin cifrado ni copia externa automática | Fallo del equipo o pérdida del disco puede afectar base y backups | Copiar backups de forma segura a un segundo medio y probar restauración aislada |
| Alto | No hay pruebas integradas automatizadas contra PostgreSQL | SQLite puede no detectar diferencias de dialecto, bloqueo o concurrencia | Añadir suite de integración PostgreSQL antes de operación multiusuario |
| Medio | No hay pruebas E2E automatizadas del frontend | Un build correcto no cubre todos los flujos de navegador | Ejecutar la guía manual completa en cada versión piloto |
| Medio | Los guardas de autenticación están repetidos en páginas cliente | Puede haber comportamiento inconsistente al crecer el frontend | Centralizar protección en una fase posterior |
| Medio | Los cambios de datos maestros no tienen auditoría general | Es difícil reconstruir quién cambió algunos catálogos | Limitar usuarios y llevar bitácora externa durante el piloto |
| Medio | No hay monitoreo, alertas, rotación de logs ni recuperación automática | Un fallo puede descubrirse tarde | Revisar health, logs y backups a diario |
| Medio | `POSTGRES_PASSWORD` y `DATABASE_URL` deben mantenerse coherentes | Cambiar solo una variable puede impedir que la API conecte | Validar ambas variables sin publicarlas y ejecutar health |
| Medio | `docker compose config` muestra valores resueltos | Copiar su salida puede divulgar secretos | No publicar ni adjuntar la salida completa |
| Medio | Gastos de caja no equivalen a gastos operativos generales | Reportes pueden subestimar costos del negocio | Mantener control externo hasta implementar el Bloque 47 |
| Medio | Documentos 00–08 reflejan etapas históricas del MVP | Sus exclusiones o flujos pueden estar desactualizados para el ERP actual | Usar los documentos 13–17 como guía vigente y conservar avisos en los históricos |
| Bajo | Pytest emite una advertencia de deprecación de TestClient | Puede requerir ajuste futuro de dependencias de prueba | Registrar y resolver en mantenimiento de dependencias |

## Recomendaciones antes de usar datos reales

1. Cambiar todos los valores de ejemplo y confirmar que
   `POSTGRES_PASSWORD`, `DATABASE_URL`, `ADMIN_PASSWORD` y `AUTH_SECRET_KEY`
   son coherentes, sin compartirlos.
2. Confirmar `0018_route_receipts` en la base que se usará.
3. Ejecutar pytest, typecheck, build y `docker compose config`.
4. Probar login, health y navegación principal.
5. Crear un backup de línea base.
6. Probar una restauración en un entorno aislado con datos de prueba.
7. Definir un solo responsable de datos maestros durante la primera semana.
8. Ingresar catálogos reales de forma gradual y revisarlos antes de crear
   movimientos.
9. Levantar inventario inicial desde un conteo físico; no estimarlo.
10. Usar el sistema en paralelo con los controles actuales durante 1 a 2
    semanas.
11. Empezar con un subconjunto controlado de productos, clientes y una ruta.
12. Conciliar al final de cada día caja, rutas, ventas, cobros e inventario.
13. Guardar backups al inicio de hitos importantes y al cierre diario.
14. Registrar incidentes con fecha, pantalla, operación e identificadores,
    evitando incluir contraseñas o tokens.

## Qué no se debe hacer

- No ejecutar `docker compose down -v` con información que deba conservarse.
- No borrar el volumen `postgres_data` como forma de apagar o limpiar.
- No restaurar un backup sobre la base operativa sin crear antes un backup del
  estado actual y confirmar el archivo.
- No editar `.env` durante la operación diaria ni compartir su contenido.
- No publicar la salida completa de `docker compose config`.
- No subir `.env`, backups o datos reales al repositorio.
- No ejecutar SQL manual para corregir operaciones normales.
- No crear seeds con datos reales ni volver a ejecutar seeds como mecanismo de
  actualización de credenciales.
- No registrar una producción y asumir que el stock ya aumentó; debe aplicarse.
- No registrar una venta y asumir que el inventario ya disminuyó.
- No registrar un cierre o recibo de ruta y asumir que el total de caja cambió.
- No anular operaciones sin entender primero sus vínculos activos.
- No abandonar los controles manuales durante el piloto.

## Resultado técnico del corte

| Validación | Resultado |
| --- | --- |
| Estado Git inicial | Limpio |
| Backend | 627 pruebas aprobadas; 1 advertencia de deprecación |
| Frontend typecheck | Aprobado |
| Frontend build | Aprobado con Next.js 16.2.9 |
| Docker Compose | Configuración válida |
| Health backend/frontend | Ambos servicios responden |
| Alembic en base local | `0018_route_receipts` |
| Migraciones nuevas | Ninguna |
| Seeds nuevos o modificados | Ninguno |
| Lógica de negocio modificada | No |

Las verificaciones finales de diff se ejecutan después de completar todos los
documentos del bloque.

## Documentos operativos relacionados

- [`14-checklist-uso-real-agua-activa.md`](14-checklist-uso-real-agua-activa.md)
- [`15-guia-piloto-datos-reales.md`](15-guia-piloto-datos-reales.md)
- [`16-roadmap-funciones-obligatorias.md`](16-roadmap-funciones-obligatorias.md)
- [`17-matriz-modulos-erp.md`](17-matriz-modulos-erp.md)
- [`04-ejecucion-local.md`](04-ejecucion-local.md)
- [`05-backup-restauracion.md`](05-backup-restauracion.md)
