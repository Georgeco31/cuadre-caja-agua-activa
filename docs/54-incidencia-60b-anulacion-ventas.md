# 54 - Incidencia 60B: anulación de ventas

## Identificación

| Dato | Registro |
| --- | --- |
| Fecha de diagnóstico | 2026-07-29 |
| Contexto | Piloto controlado Día 1, iniciado el 2026-07-28 |
| Módulos afectados | Ventas de contado y ventas a crédito |
| Rol que reportó el síntoma | `admin_auditor` |
| Síntoma visible | `Load failed` al intentar anular |
| Método paralelo | Continúa activo |
| Datos productivos modificados durante el diagnóstico | Ninguno |

No se registraron ventas de prueba, no se anuló ninguna venta real y no se
copiaron credenciales, tokens ni secretos.

## Contrato confirmado

Las ventas de contado y a crédito comparten un único flujo de anulación:

| Elemento | Contrato |
| --- | --- |
| Endpoint | `POST /api/v1/sales/{sale_id}/void` |
| Payload | `{"reason": "motivo obligatorio"}` |
| Rol permitido | `admin_auditor` |
| Rol no permitido | `operator` |
| Persistencia | Anulación lógica; la venta y sus ítems permanecen |
| Trazabilidad | `status`, `void_reason`, `voided_at` y `created_by` |

El backend exige un motivo no vacío. Una venta a crédito con abonos activos no
se fuerza: responde `409` y pide anular primero los abonos. Una venta asociada
a una carga con cierre financiero activo también responde `409`.

## Respuestas del backend

| Caso | Respuesta |
| --- | --- |
| Anulación administrativa permitida | `200` |
| Motivo ausente o vacío | `422` |
| `operator` intenta anular | `403` |
| Venta inexistente para un usuario autorizado | `404` |
| Venta ya anulada, con abonos activos o con cierre financiero activo | `409` |
| Error interno observado | Ninguno |

El preflight CORS del endpoint respondió `200` desde los orígenes configurados
de localhost, LAN y Tailscale. Una petición sin autenticación llegó al endpoint
y respondió `401` con JSON controlado.

## Evidencia de ejecución y causa

Los últimos 150 registros del API estaban ocupados por comprobaciones de
health. La búsqueda ampliada a las últimas 24 horas mostró consultas y
creaciones de ventas con `200` y `201`, pero no mostró ningún `OPTIONS` ni
`POST` a `/sales/{id}/void` asociado a la incidencia.

Por tanto, el intento que mostró `Load failed` no alcanzó el backend y no tuvo
un código HTTP real que clasificar como `400`, `403`, `404`, `409` o `500`.
El endpoint, método y payload definidos en el frontend sí coinciden con el
contrato del backend.

La causa corregible encontrada fue el manejo frontend: la función de anulación
dejaba escapar directamente el mensaje nativo del navegador cuando `fetch`
fallaba antes de recibir una respuesta. En Safari ese error de transporte se
muestra como `Load failed`. La evidencia disponible no permite atribuir
retrospectivamente la interrupción original a una causa de red más específica;
CORS, ruta y disponibilidad actuales quedaron comprobados.

## Corrección aplicada

La corrección se limitó al frontend de anulación de ventas:

- los errores HTTP del backend conservan su código y su mensaje de negocio;
- un error de transporte se convierte en un mensaje claro que pide verificar
  la conexión, reintentar y, si continúa, usar el método manual y avisar a
  George;
- la causa técnica original queda enlazada al `ApiError` para diagnóstico;
- un `403` en cualquiera de las dos pantallas muestra:
  `No tienes permiso para anular ventas. Solicita autorización a George.`;
- tras una anulación exitosa se conserva el refresco de la lista y el resumen
  visible de la venta.

No se modificó el backend, el esquema, los permisos, las reglas de negocio ni
`.env.production.local`.

## Pruebas con `admin_auditor`

Las pruebas automatizadas aisladas confirman:

- venta de contado anulable con motivo: `200`;
- venta a crédito anulable sin abonos activos: `200`;
- motivo obligatorio y normalizado;
- venta e ítems conservados después de la anulación lógica;
- segundo intento: `409`;
- venta a crédito con abonos activos: `409` con regla clara;
- saldo de la venta a crédito llevado a cero y estado de crédito `voided`
  cuando la anulación es válida;
- una venta de contado conserva `credit_status = none`.

No se anuló una venta real con la cuenta administrativa durante el diagnóstico,
porque no se dispuso de una sesión autenticada entregada por su titular y no se
debía alterar información real para fabricar una prueba.

## Pruebas con `operator`

El backend devuelve `403` antes de buscar o modificar la venta. La protección
no depende del tipo de venta porque contado y crédito comparten el endpoint.
El botón continúa oculto para `operator` y, si una interfaz desactualizada
intenta la petición, ambas pantallas muestran el mensaje de autorización
definido para el piloto.

No se cambió la matriz de permisos y `operator` continúa sin capacidad de
anular ventas ni cobros.

## Impacto por módulo

| Área | Resultado |
| --- | --- |
| Caja | Sin movimientos nuevos; las ventas todavía no modifican caja automáticamente |
| Cartera | La venta anulada deja de sumar saldo; una venta con abonos activos queda bloqueada |
| Inventario | Sin cambio directo por la anulación de venta |
| Rutas | Se conserva la venta vinculada y se bloquea la anulación si existe cierre financiero activo |
| Auditoría | Venta e ítems permanecen; se conservan motivo, fecha de anulación y creador original |

## Estado final

La causa de presentación de `Load failed` quedó corregida en el código
frontend. El backend ya cumplía el contrato, los permisos y las reglas de
negocio, por lo que no requirió cambios.

La imagen productiva de `web` se reconstruyó y se recreó sin reiniciar `api` ni
`db` y sin tocar volúmenes. El health posterior aprobó contenedores, API
localhost/LAN/Tailscale, Web LAN/Tailscale, Alembic y aislamiento de PostgreSQL,
sin fallos ni advertencias. Los artefactos dentro del contenedor contienen el
nuevo manejo de anulación.

La validación automatizada terminó con:

- 121 pruebas específicas de permisos y ventas aprobadas;
- 972 pruebas backend aprobadas, con un warning conocido de
  `TestClient/httpx`;
- `npm run typecheck` aprobado;
- `npm run build` aprobado localmente y dentro de la imagen Docker;
- `docker compose config --quiet` aprobado;
- health productivo aprobado después del despliegue.

La comprobación humana sobre una venta real autorizada queda pendiente para
George; por eso la incidencia se mantiene en revisión operativa. El piloto
mantiene el método manual paralelo. Si vuelve a ocurrir un error de conexión,
se debe conservar la referencia de la venta, la hora, el origen de acceso (LAN
o Tailscale) y el mensaje visible, sin repetir a ciegas la operación.

## Bloque posterior: corrección de fechas

La corrección de fechas no forma parte de 60B. Debe ejecutarse en un bloque
posterior y separado, con casos de borde para la zona `America/Guayaquil`,
fechas de venta y vencimiento, reportes y operaciones alrededor de medianoche.
No se debe mezclar ese cambio con la anulación ni con producción/insumos.
