# 18 - Auditoría técnica completa antes de producción local

## Resumen ejecutivo

- Fecha de auditoría: **2026-07-25**.
- Bloque auditado: **53**.
- Rama inicial: `main`.
- Commit inicial: `060e303fa396e2a518dac2227b2b136246d1ce39`
  (`Exportacion PDF`).
- Estado Git inicial: limpio, sin archivos preparados para commit.
- Decisión: **continuar con reservas al Bloque 54**.
- Estado para producción local o piloto: **no autorizado todavía**.

El ERP tiene una base funcional sólida: la suite backend aprobó 917 pruebas,
el frontend pasó typecheck y build, Docker Compose es válido, la API responde,
la base está en `0025_materials`, las rutas funcionales requieren JWT y las
exportaciones generan archivos válidos sin modificar conteos de negocio.

La reserva no se debe a un fallo funcional general, sino a cuatro condiciones
previas a cualquier uso productivo:

1. PostgreSQL conserva la contraseña de desarrollo y el puerto `5432` se
   publica en todas las interfaces del host.
2. Solo existe el usuario administrador, sin roles ni separación
   `operator`/`admin-auditor`.
3. La configuración actual usa `localhost` para API y CORS, por lo que no es
   una configuración válida para clientes de la red local.
4. Los backups son manuales y no hay evidencia actual de restauración
   aislada, automatización, retención ni copia externa.

También existe deuda histórica entre modelos y esquema: `alembic heads` y
`alembic current` coinciden en `0025_materials`, pero `alembic check` falla por
divergencias de índices y constraints. No se corrigió ni se generó una
migración en este bloque.

## Alcance y método

Se revisaron:

- Git, `.gitignore`, archivos locales ignorados y firmas comunes de secretos.
- Estructura de `apps/api`, `apps/web`, `docs`, `scripts`, README y Compose.
- Configuración, autenticación, routers, servicios, repositorios, schemas y
  modelos.
- Rutas y protección frontend, manejo de token, errores, formularios,
  navegación y responsividad.
- Cadena Alembic, constraints, volumen PostgreSQL y estado de la base activa.
- Reglas críticas de caja, ventas, cobros, inventario, producción, compras,
  nómina, anulaciones y reportes.
- Panel gerencial, Excel y PDF.
- Scripts de operación, backup y restauración.
- Pruebas automatizadas, build, health, navegación manual y conteos
  agregados de integridad.

No se mostraron secretos, datos personales ni contenido de dumps. No se
crearon datos, migraciones, seeds, endpoints, pantallas ni scripts.

## Estado general

| Componente | Estado | Evaluación |
| --- | --- | --- |
| Git y repositorio | Aprobado con observaciones | Árbol inicial limpio; `.env`, backups y artefactos pesados están ignorados |
| Estructura | Aprobado con deuda | Separación por capas clara; varios archivos crecieron demasiado |
| Backend | Aprobado | 917 pruebas; validaciones, Decimal/Numeric, bloqueos y anulaciones presentes |
| Frontend | Aprobado con deuda | 35 páginas de dashboard protegidas en cliente; typecheck/build correctos |
| Base de datos | Aprobado con reserva | Revisión correcta; integridad básica sin anomalías; `alembic check` falla |
| Docker local | Aprobado para desarrollo | Servicios activos y volumen persistente; exposición y endurecimiento no productivos |
| Seguridad | No apto para producción | Sin roles, contraseña PostgreSQL de desarrollo, HTTP y JWT en `localStorage` |
| Reportes/exportaciones | Aprobado | GET autenticados, servicios compartidos y archivos válidos de solo lectura |
| Backups/restauración | Insuficiente para producción | Backup manual disponible; falta automatización y restauración probada |
| Red local/Tailscale | No preparado | URLs/CORS son locales; no hay política de firewall ni despliegue de servidor |

## 1. Git y repositorio

### Evidencia

- Rama: `main`, alineada con `origin/main` al iniciar la auditoría.
- Último commit: `060e303`, fecha `2026-07-25T18:04:22-05:00`.
- 55 commits, 462 archivos versionados y ningún tag.
- `git status --short`: vacío al inicio.
- `git diff --cached --stat`: vacío al inicio.
- No se encontró historial de `.env`, dumps SQL, backups o claves privadas
  versionados.
- No se detectaron firmas fuertes comunes de claves privadas, tokens GitHub,
  AWS, Slack u OpenAI en los archivos actuales revisados.
- `.env.example` está versionado y contiene valores deliberadamente de
  ejemplo.

### Archivos locales sensibles o pesados

- `.env`: existe, está ignorado y no fue mostrado.
- `backups/`: contiene dos dumps SQL ignorados, de 16.993 y 22.881 bytes.
  Sus revisiones registradas son `0001_create_initial_tables` y
  `0002_expense_timing`; no respaldan el esquema actual `0025_materials`.
- `apps/api/.venv`, `apps/web/node_modules`, `apps/web/.next`,
  `__pycache__`, `.pytest_cache` y `*.tsbuildinfo`: ignorados.

La exclusión Git es correcta, pero `.env` y los dumps siguen siendo sensibles
en disco. Deben entrar en el plan de permisos, cifrado y copias del servidor.

### Recomendación Git

Después del commit manual del Bloque 53:

1. Crear una rama para roles, por ejemplo
   `codex/block-54-roles-permissions`.
2. Mantener `main` estable y exigir pruebas antes de fusionar.
3. Crear un tag anotado `audit-block-53-2026-07-25` sobre el commit documental.
4. Crear un segundo tag `pre-pilot-local-v1` solo cuando se hayan cerrado
   riesgos críticos, probado restore y aprobado el checklist del servidor.

No se creó rama ni tag durante esta auditoría.

## 2. Estructura del proyecto

La organización por monorepo es coherente:

```text
apps/api   -> FastAPI, SQLAlchemy, Alembic, servicios y pruebas
apps/web   -> Next.js, componentes, cliente API y tipos
docs       -> definición, operación, roadmap y auditorías
scripts    -> arranque, apagado, health, migración, seed, backup y restore
```

Fortalezas:

- Backend separado en endpoints, services, repositories, schemas y models.
- Frontend separado en rutas, componentes, cliente API y tipos.
- Dockerfiles propios y Compose con tres servicios.
- Migraciones lineales y pruebas organizadas por módulo.

Riesgos de crecimiento:

- `apps/web/lib/api.ts` tiene 2.831 líneas.
- Las páginas de gastos operativos, fórmulas, control de empleados, compras,
  precios y nómina tienen entre 1.219 y 2.172 líneas.
- Los servicios Excel, PDF y panel gerencial tienen 1.888, 1.305 y 924 líneas.
- La protección y el manejo de `401/403` se repiten en todas las páginas del
  dashboard.

Esto no bloquea el Bloque 54, pero aumenta el costo de cambios y el riesgo de
inconsistencias. Conviene extraer clientes API por dominio, hooks de
autenticación y componentes de formulario después de estabilizar producción.

## 3. Backend

### Arquitectura y protección

- Se contaron 199 operaciones declaradas con decoradores FastAPI.
- 196 operaciones quedan protegidas a nivel de router.
- `GET /auth/me` se protege explícitamente.
- Solo `POST /auth/login` y `GET /health` son públicos.
- Los 28 archivos de routers funcionales usan
  `Depends(get_current_user)`.
- En la API activa, un reporte sin token respondió `401`, mientras health
  respondió `200`.

La dependencia valida Bearer JWT, sujeto numérico, existencia del usuario y
estado activo. Los endpoints que necesitan trazabilidad reciben además el
usuario actual.

### Datos monetarios y cantidades

- Los modelos usan `Numeric` para dinero y cantidades.
- Los schemas y servicios usan `Decimal`.
- Dinero se normaliza generalmente a 2 decimales; inventario y producción a
  3 decimales; costos de fórmula a 4.
- Los servicios críticos rechazan `float` o convierten desde valores
  decimales controlados.
- Los totales oficiales se calculan en backend.

No se detectó uso de `Float` como tipo persistente para valores financieros.

### Fechas y horas

- Los instantes persistidos usan `DateTime(timezone=True)` y operaciones UTC.
- Las fechas operativas se modelan como `date`.
- Existe un riesgo de zona horaria: host `America/Guayaquil` (`-05`) y
  contenedores API/PostgreSQL en UTC.
- Los usos de `date.today()` en reportes, vencidos, precios y numeraciones
  pueden cambiar de día a las 19:00 hora de Ecuador.

Antes del piloto se debe definir una única zona de negocio, idealmente
`America/Guayaquil`, y probar explícitamente cierres y reportes alrededor del
cambio de fecha.

### Validaciones y errores

- Pydantic aplica longitudes, rangos, identificadores positivos, listas no
  vacías y valores monetarios no negativos/positivos.
- Los servicios validan estados, vínculos activos, stock, saldos y motivos.
- Los endpoints convierten errores de negocio conocidos a `400`/`404`/`409`
  según el módulo.
- Se manejan `IntegrityError` y rollback en múltiples transacciones críticas.
- Inventario, pagos, producción, rutas, nómina y otros flujos usan
  `SELECT ... FOR UPDATE` donde existe riesgo concurrente.

Deuda:

- No hay manejador global uniforme de excepciones ni logging estructurado.
- La creación concurrente del cuadre depende del constraint único para
  preservar integridad; un choque puede terminar como error interno no
  amigable.
- Las pruebas usan principalmente SQLite en memoria. Falta una suite de
  integración PostgreSQL para locks, constraints parciales y concurrencia.

## 4. Frontend

### Rutas y autenticación

- Existen 37 archivos `page.tsx`: raíz, login y 35 páginas bajo dashboard.
- Las 35 páginas de dashboard verifican `getToken()` y eliminan el token ante
  `401/403`.
- El token JWT se guarda en `localStorage`.
- No existe middleware o layout único de autenticación; los guardas están
  repetidos por página.
- Logout elimina el token local y redirige a login.

El patrón funciona para la aplicación actual, pero `localStorage` amplía el
impacto de una vulnerabilidad XSS. Para producción local debe combinarse con
dependencias actualizadas, CSP, HTTPS y una evaluación posterior de cookies
seguras/refresh tokens.

### Errores, formularios y usabilidad

- El cliente API transforma respuestas fallidas en `ApiError`.
- Los errores de validación de FastAPI se agregan en mensajes visibles.
- Formularios críticos deshabilitan acciones durante envíos y piden motivos
  en anulaciones/correcciones.
- Listas grandes usan contenedores con scroll horizontal.
- Se detectaron clases responsive en 82 archivos.

Para una secretaria, el dashboard ofrece muchos accesos a funciones
administrativas y gerenciales. Hasta que existan roles, la densidad de
navegación y la capacidad de anular o editar registros aumentan el riesgo
operativo.

### Validación responsive

A 390 x 844 píxeles se comprobaron:

- `/dashboard`
- `/dashboard/cash-session`
- `/dashboard/management`
- `/dashboard/exports`
- `/dashboard/payroll`

Todas mostraron su encabezado, sin error visible ni desbordamiento horizontal
de la página. Las tablas anchas conservan scroll interno.

## 5. Base de datos y migraciones

### Estado

- Archivos de migración: 25.
- Grafo: lineal, desde `0001_create_initial_tables` hasta
  `0025_materials`.
- `alembic heads`: `0025_materials`.
- `alembic current`: `0025_materials`.
- Consulta directa a `alembic_version`: `0025_materials`.
- No existe archivo `0026`.

### Constraints principales

Se observaron:

- Unicidad de `cash_sessions.session_date`.
- Unicidad de conteo por cuadre/denominación.
- Estados limitados por `CHECK`.
- Montos y cantidades positivos o no negativos.
- Unicidades en números de documentos.
- Claves foráneas entre cabeceras, ítems, usuarios y movimientos.
- Unicidad de aplicaciones/consumos activos y vínculos de inventario.
- Anulaciones representadas por estado, motivo y fecha, no borrado físico.

### Divergencias históricas de Alembic

`alembic check` terminó con código 255 y detectó operaciones nuevas. El
hallazgo es reproducible y se clasifica como deuda importante, no como daño
actual:

- En 13 campos con `unique=True, index=True`, PostgreSQL conserva un
  `UNIQUE CONSTRAINT` y un índice no único, mientras el metadata representa
  un índice único. Afecta números de anticipos, préstamos, abonos de préstamo,
  gastos, roles, fórmulas, compras, recibos/cierres/cargas/retornos y la
  identificación de proveedores.
- El índice parcial
  `uq_route_returns_active_route_load` existe en la base/migración, pero no
  está representado en metadata; un autogenerate ciego propondría removerlo.
- Seis índices históricos de `sales` y `sale_items` existen en la base, pero
  no en metadata.

Las restricciones existentes siguen protegiendo la base y las pruebas pasan.
El riesgo aparece al generar la próxima migración: aceptar automáticamente el
diff podría eliminar protección o rendimiento. El Bloque 54 debe crear y
revisar manualmente su migración, sin aceptar operaciones ajenas a roles.

No se corrigió esta divergencia en el Bloque 53.

### Persistencia y borrado

- PostgreSQL usa el volumen nombrado `postgres_data`.
- `docker compose down` conserva el volumen.
- `docker compose down -v` elimina el volumen y **no debe usarse con datos
  reales**.
- No hay endpoints HTTP `DELETE` para los registros operativos revisados.
- Los `drop_table` encontrados pertenecen a funciones `downgrade()` de
  migraciones; ejecutar downgrades en producción requerirá backup y plan
  explícito.

## 6. Docker y entorno local

`docker compose config` aprobó y resolvió:

- Servicios: `db`, `api`, `web`.
- Volumen: `postgres_data`.
- Puertos actuales: host `5432`, `8010` y `3000`.
- Los tres contenedores estaban activos.

Aspectos correctos:

- API ejecuta Uvicorn sin `--reload`.
- Web usa build multi-stage y `next start`, no `next dev`.
- La base tiene healthcheck.
- El frontend se construye en modo producción.

Faltantes para Bloque 55A:

- No publicar PostgreSQL al LAN; retirar `ports` o enlazar a `127.0.0.1`.
- Definir URL real accesible por los clientes y CORS asociado.
- Fijar zona horaria de negocio.
- Añadir healthchecks de API/web, políticas `restart`, límites y rotación de
  logs.
- Ejecutar contenedores como usuario no root cuando sea viable.
- Separar configuración Compose de desarrollo y producción.
- Definir migración previa al arranque, sin seeds automáticos.
- Añadir proxy/reverse proxy y decidir HTTPS.

Comandos seguros actuales:

```bash
./scripts/local-start.sh
./scripts/check-health.sh
./scripts/local-stop.sh
```

Advertencia permanente:

```text
NO ejecutar docker compose down -v con datos que deban conservarse.
```

## 7. Variables de entorno y seguridad

Se revisaron únicamente nombres, presencia y comparación contra defaults; no
se registraron valores.

Variables requeridas presentes:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`
- `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_IS_ACTIVE`
- `AUTH_SECRET_KEY`, `AUTH_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `BACKEND_CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`
- `API_PORT`, `WEB_PORT`, `ENVIRONMENT`

Hallazgos:

- `ADMIN_USERNAME`, `ADMIN_PASSWORD` y `AUTH_SECRET_KEY` locales difieren del
  ejemplo.
- `POSTGRES_PASSWORD` conserva `change-me`.
- `DATABASE_URL` conserva el valor de ejemplo correspondiente.
- `ENVIRONMENT` conserva `development`.
- Compose ofrece defaults inseguros si faltan variables.
- CORS solo admite orígenes localhost.
- `NEXT_PUBLIC_API_URL` se compila como localhost.
- `.env` está correctamente ignorado, pero no tiene control de permisos,
  cifrado ni gestor de secretos.

Antes de producción:

- Generar contraseñas y secreto JWT únicos y largos.
- Mantener `POSTGRES_PASSWORD` y `DATABASE_URL` coherentes.
- Eliminar defaults inseguros del Compose productivo o fallar si faltan.
- No compartir cuentas ni `.env`.
- Restringir permisos del archivo al usuario que opera el servidor.
- No adjuntar la salida completa de `docker compose config`, pues resuelve
  secretos.

## 8. Autenticación y permisos

Estado actual:

- Login con usuario/contraseña y JWT Bearer.
- Token con `sub` y `exp`.
- Expiración configurable, actualmente de corta duración.
- Usuario inactivo rechazado.
- Un solo usuario administrador creado por seed.
- Modelo `users` sin campo de rol.
- Sin autorización por módulo, acción o nivel de riesgo.

Riesgo: si la secretaria usa admin, puede acceder al panel gerencial,
exportaciones, correcciones, anulaciones, inventario, producción, nómina y
configuración operativa. Además, todas las acciones quedan atribuidas a la
misma cuenta compartida.

Recomendación para Bloque 54:

- Roles mínimos `operator` y `admin-auditor`.
- Cuentas personales; no compartir contraseña.
- Denegación por defecto en backend.
- Ocultar navegación no autorizada en frontend, sin depender de ello como
  control de seguridad.
- Reservar correcciones, anulaciones sensibles, nómina, panel gerencial,
  exportaciones y administración de usuarios al rol apropiado.
- Añadir pruebas de matriz endpoint/rol y conservar trazabilidad por usuario.

## 9. Reglas críticas de negocio

La revisión de código y pruebas confirma:

- Un cuadre principal por fecha, protegido por validación y constraint único.
- Cuadres cerrados no aceptan conteos ni gastos directos.
- Correcciones solo sobre cuadres cerrados y con motivo.
- Anulaciones sensibles conservan registro, motivo, usuario y fecha.
- Ventas no modifican caja automáticamente.
- Compras no modifican inventario ni caja automáticamente.
- Crear producción no mueve inventario.
- Aplicar producción y consumir insumos son acciones explícitas.
- El consumo de insumos crea movimientos y su anulación revierte stock en una
  transacción.
- Reportes, panel, Excel y PDF son operaciones GET sin commit ni escritura.
- Totales monetarios y de inventario se calculan en backend con Decimal.
- Los registros anulados se excluyen de totales activos y se reportan por
  separado cuando corresponde.

Estas separaciones son deliberadas, pero exigen capacitación y conciliación
manual durante el piloto.

## 10. Reportes y exportaciones

Estado:

- Panel gerencial autenticado por rango.
- Resumen diario y mensual autenticados.
- Diez exportaciones Excel.
- Cinco exportaciones PDF.
- Todos los endpoints de reporte/exportación usan GET.
- No se encontraron `add`, `delete`, `commit`, `flush`, `INSERT`, `UPDATE` o
  `DELETE` en los servicios de reportes revisados.
- Panel, Excel y PDF reutilizan los mismos servicios oficiales para panel,
  mensual y diario.

Pruebas automatizadas cubren:

- Rechazo sin autenticación.
- Rangos inválidos.
- Rangos sin datos.
- Apertura del Excel con `openpyxl`.
- Firma y final válido de PDF.
- Totales de cartera y nómina.
- Conteos de registros iguales antes y después de exportar.

Prueba local:

- Excel: HTTP 200, 15.087 bytes, reconocido como Microsoft Excel 2007+.
- PDF: HTTP 200, 4.497 bytes, PDF 1.4 de dos páginas.
- Conteos de 13 tablas iguales antes y después.

No se detectó divergencia funcional, aunque conviene añadir una prueba
parametrizada que compare explícitamente todas las métricas compartidas entre
JSON, Excel y PDF.

## 11. Pruebas y validaciones ejecutadas

| Validación | Resultado |
| --- | --- |
| `git status --short` inicial | Aprobado; vacío |
| Backend `.venv/bin/python -m pytest` | **917 passed**, 1 warning, 85,24 s |
| Warning backend | Deprecación Starlette TestClient/httpx |
| `npm run typecheck` | Aprobado |
| `npm run build` | Aprobado con Next.js 16.2.9; 37 rutas |
| `docker compose config` | Aprobado |
| Servicios activos | `db`, `api`, `web` |
| Health API | HTTP correcto; `status=ok` |
| Reporte sin token | HTTP 401 |
| Documentación `/docs` | HTTP 200; debe restringirse en producción |
| `alembic heads` | `0025_materials` |
| `alembic current` | `0025_materials` |
| Consulta `alembic_version` | `0025_materials` |
| `alembic check` | Falló por divergencias históricas documentadas |
| Migración 0026 | No existe |
| Exportación Excel local | HTTP 200 y archivo válido |
| Exportación PDF local | HTTP 200 y archivo válido |

El primer intento de build dentro del sandbox de auditoría fue impedido por
la restricción de enlazar un puerto de Turbopack. Repetido fuera de esa
restricción, el build finalizó correctamente; no es un fallo del proyecto.

## 12. Integridad básica de datos

Conteos agregados observados, sin leer datos personales:

| Tabla | Conteo |
| --- | ---: |
| `users` | 1 |
| `cash_sessions` | 11 |
| `expenses` | 34 |
| `customers` | 0 |
| `products` | 0 |
| `sales` | 0 |
| `credit_payments` | 0 |
| `inventory_movements` | 0 |
| `production_batches` | 0 |
| `production_material_consumptions` | 0 |
| `purchases` | 0 |
| `operating_expenses` | 0 |
| `payroll_runs` | 0 |

Comprobaciones adicionales:

- Fechas de cuadre duplicadas: 0.
- Estados de cuadre inválidos: 0.
- Denominaciones duplicadas dentro de un cuadre: 0.
- Conteos o subtotales negativos: 0.
- Gastos negativos: 0.
- Gastos huérfanos: 0.
- Cuadres abiertos: 0.

La muestra real de módulos distintos de caja está vacía; por tanto, esta
auditoría no demuestra todavía integridad de datos reales para ventas,
inventario, producción, compras o nómina. Esa validación corresponde al
piloto controlado.

## 13. Preparación para PC servidor local

Estado actual: **no preparado**.

Antes de mover el sistema:

- Cerrar riesgos críticos de
  [`19-hallazgos-riesgos-produccion.md`](19-hallazgos-riesgos-produccion.md).
- Completar
  [`20-checklist-preparacion-servidor-local.md`](20-checklist-preparacion-servidor-local.md).
- Implementar roles y cuentas personales.
- Crear Compose de producción.
- Definir IP fija o reserva DHCP.
- Hacer accesible la API desde los clientes sin usar `localhost`.
- Mantener PostgreSQL sin acceso remoto.
- Restringir firewall a LAN y Tailscale; no abrir puertos en Internet.
- Automatizar backup y probar restore.
- Proteger el equipo con UPS y apagado controlado.

Tailscale debe configurarse después del endurecimiento local, solo para George,
sin publicar el servicio globalmente ni usar funnels públicos.

## 14. Backups y restauración

Scripts existentes:

- `backup-db.sh`: levanta DB, espera disponibilidad y ejecuta
  `pg_dump --clean --if-exists` a SQL plano.
- `restore-db.sh`: valida un argumento y ejecuta el SQL con
  `ON_ERROR_STOP=1`.

Fortalezas:

- Backup lógico completo de la base.
- Archivo con timestamp.
- Carpeta ignorada por Git.
- Restore falla ante error SQL.

Faltantes:

- Un backup comprobado de la base actual en `0025_materials`; los dos archivos
  existentes corresponden a revisiones muy antiguas.
- Ejecución automática diaria.
- Retención y rotación.
- Compresión, checksum y cifrado.
- Copia externa separada del PC.
- Prueba documentada de restauración actual.
- Destino aislado por defecto.
- Manual de desastre, RPO, RTO y responsables.
- Respaldo seguro de configuración necesaria para reconstruir el servicio.

No se ejecutó restore en esta auditoría porque modifica datos y estaba fuera
del alcance.

## 15. Pruebas manuales

Con los servicios locales activos y una sesión ya autenticada:

- Abrir `/login` redirigió correctamente al dashboard.
- Dashboard cargó sin error visible.
- Se abrieron correctamente:
  - `/dashboard/management`
  - `/dashboard/exports`
  - `/dashboard/cash-session`
  - `/dashboard/history`
  - `/dashboard/products`
  - `/dashboard/customers`
  - `/dashboard/inventory`
  - `/dashboard/production`
  - `/dashboard/payroll`
- No hubo redirecciones indebidas ni errores visibles.
- Se activaron los botones de Excel y PDF sin error visible.
- Los endpoints autenticados devolvieron archivos válidos.
- Los conteos de negocio no cambiaron.

No se creó, editó, anuló ni eliminó ningún registro.

## Conclusión

**Continuar con reservas al Bloque 54.**

El código actual es suficientemente estable para implementar roles y permisos.
No se recomienda detener el avance técnico general, pero sí existe un
**punto de control obligatorio antes del Bloque 55A, del traslado al PC o del
piloto**: deben cerrarse los riesgos críticos de credenciales/puerto de base,
roles, configuración LAN y recuperación.

La divergencia Alembic no rompe la operación actual, pero obliga a revisar
manualmente cualquier migración del Bloque 54 y a no aceptar diffs
autogenerados ajenos a permisos.
