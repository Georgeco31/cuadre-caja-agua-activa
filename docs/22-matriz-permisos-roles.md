# 22 - Matriz de permisos por rol

## Alcance

Agua Activa ERP usa dos roles controlados:

- `operator`: registra y consulta la operación diaria.
- `admin_auditor`: puede realizar toda la operación y las acciones críticas.

El backend consulta el usuario activo en base de datos para cada petición. El
rol guardado por el frontend y el rol incluido en el JWT sirven para adaptar la
interfaz, pero no sustituyen la autorización del backend.

## Matriz

| Acción | operator | admin_auditor |
| --- | --- | --- |
| Iniciar sesión y consultar `/auth/me` | Sí | Sí |
| Ver dashboard operativo | Sí | Sí |
| Crear y cerrar cuadre abierto | Sí | Sí |
| Registrar conteo y gasto de cuadre abierto | Sí | Sí |
| Consultar historial de cuadres | Sí | Sí |
| Corregir cuadre cerrado | No | Sí |
| Consultar logs de corrección | No | Sí |
| Crear clientes y productos | Sí | Sí |
| Registrar venta de contado o crédito | Sí | Sí |
| Anular venta | No | Sí |
| Registrar cobro o abono | Sí | Sí |
| Anular cobro o abono | No | Sí |
| Consultar cuentas por cobrar | Sí | Sí |
| Registrar movimiento normal de inventario | Sí | Sí |
| Registrar ajuste directo de inventario | No | Sí |
| Anular movimiento de inventario | No | Sí |
| Registrar producción | Sí | Sí |
| Aplicar producción a inventario | Sí | Sí |
| Anular producción o aplicación a inventario | No | Sí |
| Registrar consumo de insumos | Sí | Sí |
| Anular consumo de insumos | No | Sí |
| Registrar carga, retorno, cierre y recibo de ruta | Sí | Sí |
| Anular carga, retorno, cierre o recibo de ruta | No | Sí |
| Registrar compra | Sí | Sí |
| Anular compra | No | Sí |
| Registrar o editar gasto operativo activo | Sí | Sí |
| Anular gasto operativo | No | Sí |
| Administrar categorías y plantillas de gastos | No | Sí |
| Registrar asistencia, anticipo, préstamo y abono | Sí | Sí |
| Anular anticipo, préstamo o abono | No | Sí |
| Crear y consultar rol de pago | Sí | Sí |
| Anular rol de pago | No | Sí |
| Consultar o resolver precios para una venta | Sí | Sí |
| Crear, editar, activar o desactivar listas de precios | No | Sí |
| Ver panel gerencial completo | No | Sí |
| Descargar exportaciones gerenciales Excel/PDF | No | Sí |
| Listar, crear o modificar usuarios | No | Sí |
| Activar/desactivar usuarios o cambiar contraseñas | No | Sí |
| Cambiar roles | No | Sí |

## Reglas de seguridad

- Una petición sin credenciales válidas recibe `401`.
- Un usuario inactivo recibe `403`.
- Un usuario autenticado sin el rol requerido recibe `403` con el mensaje
  `No tienes permisos para realizar esta acción.`
- No se puede desactivar ni degradar al último `admin_auditor` activo.
- Los usuarios nuevos creados desde administración son `operator` si no se
  especifica otro rol.
- La migración `0026_user_roles` convierte los usuarios existentes en
  `admin_auditor` para no bloquear la cuenta administrativa actual.
- Ningún endpoint de usuarios devuelve `password_hash`.

## Interfaz

`/dashboard/users`, el panel gerencial, las exportaciones completas y la
administración de listas de precios son visibles solo para
`admin_auditor`. Los botones de corrección, anulación y ajuste directo también
se ocultan a `operator`. Una URL o petición directa sigue siendo validada por
el backend.
