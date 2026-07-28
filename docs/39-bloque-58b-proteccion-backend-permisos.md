# 39 - Bloque 58B: protección backend de permisos

## Estado

- Bloque: **58B**.
- Fecha: **2026-07-28**.
- Estado: **implementado y validado**.
- Alcance: autorización backend fija para los roles `admin_auditor` y
  `operator`.
- Fuera de alcance: frontend, permisos configurables en base de datos, nuevos
  roles, migraciones, seeds, Docker y cambios de contratos o cálculos.

## Objetivo

Convertir la matriz aprobada en una frontera real de seguridad en el backend.
Un usuario autenticado sin permiso recibe `403` antes de ejecutar el servicio o
producir efectos laterales. Las tareas operativas aprobadas continúan
disponibles para `operator`.

## Política aplicada

`admin_auditor` conserva acceso total. `operator` mantiene:

- abrir, consultar, contar, registrar gastos y cerrar el cuadre diario;
- crear clientes y consultar clientes;
- consultar productos;
- registrar y consultar ventas de contado y a crédito;
- registrar y consultar cobros y cartera operativa;
- resolver el precio aplicable durante una venta;
- registrar y consultar producción diaria;
- consultar inventario y crear movimientos `entry`/`exit` sin `unit_cost`;
- consultar las pantallas y reportes operativos aprobados.

`operator` no puede:

- corregir cuadres cerrados ni consultar sus logs;
- anular ventas, cobros, compras, gastos, operaciones de ruta, movimientos,
  producción, consumos, anticipos, préstamos, abonos o nómina;
- administrar listas o ítems de precios;
- ver el panel gerencial, el reporte acumulado o el resumen mensual;
- descargar Excel o PDF;
- administrar usuarios;
- ver o gestionar empleados, asistencia, anticipos, préstamos, abonos o
  nómina;
- crear o modificar fórmulas, ítems de recetas o configuración productiva;
- aplicar producción a inventario ni confirmar consumo de insumos;
- administrar ubicaciones de inventario, crear ajustes o indicar costos;
- ejecutar mutaciones administrativas o aún no aprobadas sobre clientes,
  productos, rutas, vehículos, proveedores, compras y gastos operativos.

## Autorización reutilizada

Se reutilizaron los helpers existentes en `app/api/deps.py`:

- `require_roles(...)`: dependencia declarativa para uno o más roles;
- `require_admin_auditor`: dependencia fija para operaciones administrativas;
- `ensure_admin_auditor(user)`: comprobación interna para endpoints que mezclan
  acciones permitidas y restringidas;
- constantes `ROLE_OPERATOR`, `ROLE_ADMIN_AUDITOR` y mensaje común de permiso
  denegado.

No se añadieron tablas, permisos configurables, roles ni migraciones.

## Endpoints protegidos

El prefijo común es `/api/v1`.

### Protecciones que ya existían y se conservaron

| Grupo | Endpoints |
| --- | --- |
| Correcciones de caja | `POST /cash-sessions/{id}/corrections/count-items`, `POST /cash-sessions/{id}/corrections/expenses`, `GET /cash-sessions/{id}/corrections` |
| Anulaciones | `POST /sales/{id}/void`, `POST /credit-payments/{id}/void`, anulaciones de compras, gastos, rutas, inventario, producción, consumos y nómina |
| Precios | Mutaciones de listas e ítems de precios |
| Gerencia y exportaciones | `GET /reports/management-dashboard`, todos los endpoints `/reports/exports/*.xlsx` y `/reports/exports/*.pdf` |
| Usuarios | Todo el router `/users`, incluida contraseña, rol y activación |

### Brechas cerradas en 58B

| Grupo | Protección efectiva |
| --- | --- |
| Precios sensibles | `GET /pricing/price-lists` y `GET /pricing/price-lists/{id}` son administrativos; `GET /pricing/resolve` sigue permitido |
| Empleados | Todo `/employees` de datos maestros y control laboral exige `admin_auditor` |
| Nómina | Todo `/payroll` y el resumen de nómina por empleado exige `admin_auditor` |
| Fórmulas | Crear, editar, activar/desactivar recetas e ítems exige `admin_auditor`; las consultas permanecen autenticadas |
| Producción con impacto de inventario | Aplicar un lote a inventario y confirmar consumo de materiales exige `admin_auditor` |
| Inventario | Mutaciones de ubicaciones, ajustes, anulaciones y movimientos con `unit_cost` exigen `admin_auditor` |
| Datos maestros | Mutaciones de productos, rutas y vehículos exigen `admin_auditor`; el alta de cliente sigue permitida, pero su edición/activación exige administrador |
| Operación pendiente | Crear proveedores, compras, gastos operativos fuera de caja y operaciones de ruta exige `admin_auditor`; las consultas aprobadas se mantienen |
| Reportes financieros | Reporte acumulado de caja y resumen mensual exigen `admin_auditor`; resumen diario y comparación de ruta siguen operativos |

## Validación condicional de inventario

`POST /inventory/movements` conserva el mismo payload y diferencia la acción
antes de llamar al servicio:

| Solicitud de `operator` | Resultado |
| --- | --- |
| `movement_type=entry`, sin `unit_cost` | Permitido |
| `movement_type=exit`, sin `unit_cost` | Permitido |
| `movement_type=adjustment_in` | `403` |
| `movement_type=adjustment_out` | `403` |
| Cualquier tipo con `unit_cost` | `403` |

El movimiento permitido conserva `created_by`, fecha, producto, ubicación,
tipo, cantidad, motivo si fue enviado y timestamps. No existe endpoint de
eliminación de movimientos.

## Comportamiento `401` y `403`

- Sin credenciales, token inválido o usuario inexistente: `401` con encabezado
  `WWW-Authenticate: Bearer`.
- Usuario autenticado pero inactivo: `403` con detalle específico.
- Usuario activo con rol insuficiente: `403` con
  `No tienes permisos para realizar esta acción.`.
- Las dependencias de autorización se resuelven antes de ejecutar el servicio;
  una denegación no escribe datos.

## Pruebas

Se creó `apps/api/tests/test_operator_permissions.py` con 42 casos:

- acceso positivo de `admin_auditor` a familias restringidas;
- `401` sin autenticación;
- `403` de `operator` en correcciones, anulaciones, precios, reportes,
  exportaciones, usuarios, empleados, nómina, fórmulas e inventario sensible;
- cierre de cuadre permitido y corrección posterior denegada;
- producción diaria permitida;
- inventario `entry`/`exit` permitido y trazado;
- ajustes y `unit_cost` denegados;
- venta a crédito y cobro permitidos.

Resultados:

```text
tests/test_operator_permissions.py: 42 passed
suite backend completa:           972 passed
```

La única advertencia es una deprecación externa de `Starlette TestClient`
relacionada con `httpx`; no representa un fallo funcional.

## Acciones no aplicables

- No existe endpoint para reabrir un cuadre.
- No existen endpoints `DELETE` para ventas, cobros, movimientos, fórmulas o
  registros de nómina; las operaciones existentes usan anulación lógica.
- No existe un tipo literal `adjustment`; el sistema usa `adjustment_in` y
  `adjustment_out`, ambos restringidos.
- No se creó ningún endpoint nuevo.
- No se implementaron permisos configurables ni excepciones por usuario.

## Riesgos pendientes

- El cierre de caja registra `closed_at`, pero el modelo actual no tiene
  `closed_by`. Agregar ese actor requeriría una decisión de modelo y una
  migración; se dejó fuera de 58B.
- No existe alcance por registro, turno, ruta o ubicación. Un permiso operativo
  aplica a todos los registros visibles para el rol.
- Algunas consultas operativas devuelven campos de costo ya incluidos en sus
  contratos. 58B impide modificarlos; una política futura de ocultamiento
  requeriría diseñar respuestas separadas.
- El frontend todavía puede mostrar controles que ahora reciben `403`; esto se
  corregirá en 58C sin convertir la UI en autoridad de seguridad.

## Siguiente bloque

58C debe adaptar navegación y controles visuales a esta política, centralizar
las capacidades del rol y presentar un estado de acceso denegado coherente. El
backend implementado en 58B seguirá siendo la fuente real de seguridad.
