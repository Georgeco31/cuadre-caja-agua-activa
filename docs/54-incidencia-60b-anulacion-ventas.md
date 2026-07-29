# 54 - Incidencia 60B/60B-2: anulación de ventas

## Identificación

| Dato | Registro |
| --- | --- |
| Fecha de diagnóstico | 2026-07-29 |
| Contexto | Piloto controlado Día 1, iniciado el 2026-07-28 |
| Módulos afectados | Ventas de contado y ventas a crédito |
| Rol que reportó el síntoma | `admin_auditor` |
| Síntoma inicial | `Load failed` |
| Síntoma después de 60B | Mensaje de imposibilidad de contactar al servidor |
| Estado de API LAN durante el incidente | `health` respondía `200` |
| Método paralelo | Continúa activo |
| Datos productivos modificados durante el diagnóstico | Ninguno |

No se registraron ventas de prueba, no se anuló ninguna venta real y no se
copiaron credenciales, tokens, secretos ni contenido de
`.env.production.local`.

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

El backend exige un motivo no vacío. Una venta a crédito con abonos activos
responde `409` y pide anular primero los abonos. Una venta asociada a una carga
con cierre financiero activo también responde `409`.

## Evidencia exacta y corrección del diagnóstico anterior

Los logs ampliados demostraron que la falla no era una caída general de red ni
una URL LAN equivocada. El navegador completó el preflight y la llamada llegó
al API:

```text
OPTIONS /api/v1/sales/{id}/void 200
POST /api/v1/sales/{id}/void 500
```

La excepción real de PostgreSQL fue:

```text
psycopg.errors.FeatureNotSupported:
FOR UPDATE cannot be applied to the nullable side of an outer join
```

`get_sale_for_update` cargaba la venta junto con sus relaciones opcionales de
carga, ruta y vehículo mediante `LEFT OUTER JOIN` y aplicaba `FOR UPDATE` sin
indicar tabla. PostgreSQL intentaba bloquear también el lado anulable de esos
joins y rechazaba la consulta. La suite basada en SQLite no había reproducido
esa diferencia del motor.

Por tanto, la afirmación inicial de 60B de que el intento no alcanzó el API
queda reemplazada por esta evidencia: el `POST` sí llegó, pero terminó en un
`500` no controlado. El navegador no recibió una respuesta HTTP utilizable y
el frontend lo clasificó como error de transporte, produciendo el falso
mensaje de conexión.

## Auditoría de arquitectura frontend

La anulación de contado y crédito ya compartía `voidCashSale` y no tenía una IP
fija ni un `fetch` dentro de las pantallas. La auditoría completa de `apps/web`
encontró dos inconsistencias relacionadas:

- la resolución anterior usaba el hostname dinámico para LAN/Tailscale, pero
  localhost, `127.0.0.1` y `::1` heredaban el fallback compilado; en producción
  este podía apuntar a Tailscale;
- las descargas Excel/PDF contenían el único `fetch` alterno, separado del
  camino normal de solicitudes JSON.

No se encontró `axios`, una IP LAN/Tailscale fija en código productivo ni otro
cliente HTTP paralelo. Después de la corrección queda un solo `fetch`, dentro
del helper central.

## Corrección aplicada

### Backend mínimo

La consulta conserva la carga de relaciones, pero limita el lock a la tabla
dueña de la operación:

```python
.with_for_update(of=Sale)
```

PostgreSQL genera `FOR UPDATE OF sales`, mantiene la protección de concurrencia
sobre la venta y ya no intenta bloquear los `LEFT JOIN`. No se cambió el
esquema, una migración, los permisos ni las reglas de negocio.

Se agregó una prueba que compila la consulta con el dialecto PostgreSQL y exige
simultáneamente los joins y `FOR UPDATE OF sales`, para evitar que SQLite oculte
de nuevo esta regresión.

### Frontend central

La construcción de URL se separó en `apps/web/lib/apiUrl.ts` y todas las
solicitudes pasan por `apiFetch` en `apps/web/lib/api.ts`:

- en navegador se conserva el protocolo y se usa siempre
  `window.location.hostname`, puerto `8010` y prefijo `/api/v1`;
- en SSR o contextos sin `window` se usa `NEXT_PUBLIC_API_URL`;
- las solicitudes JSON, anulaciones y descargas usan el mismo constructor;
- los errores HTTP conservan su estado y mensaje de negocio;
- solo una falla real antes de recibir respuesta se clasifica como transporte;
- un `500` con respuesta válida muestra un mensaje de servidor, no uno de
  autorización.

También se corrigió el puerto por defecto del Dockerfile de desarrollo de
`8000` a `8010`. No se hardcodeó ninguna IP en componentes.

## Resolución comprobada por origen

Las siete pruebas puras de URL aprobaron:

| Acceso Web | API resuelta para la anulación |
| --- | --- |
| `http://192.168.100.220:3000` | `http://192.168.100.220:8010/api/v1/sales/{id}/void` |
| `http://100.121.163.126:3000` | `http://100.121.163.126:8010/api/v1/sales/{id}/void` |
| `http://localhost:3000` | `http://localhost:8010/api/v1/sales/{id}/void` |
| `http://127.0.0.1:3000` | `http://127.0.0.1:8010/api/v1/sales/{id}/void` |
| `http://[::1]:3000` | `http://[::1]:8010/api/v1/sales/{id}/void` |
| SSR/sin `window` | `NEXT_PUBLIC_API_URL` normalizada |

Esto aplica igualmente a iPhone, MacBook y navegador de oficina: la API usa el
hostname con el que el dispositivo abrió la Web y no localhost remoto.

## Comportamiento por rol y reglas

Las pruebas automatizadas confirman para `admin_auditor`:

- venta de contado anulable con motivo: `200`;
- venta a crédito anulable sin abonos activos: `200`;
- motivo ausente o vacío: `422`;
- venta inexistente: `404`;
- segundo intento, abonos activos o cierre financiero activo: `409`;
- venta e ítems permanecen después de la anulación lógica;
- saldo y estado de crédito se actualizan solo cuando la anulación es válida.

Para `operator`:

- el endpoint devuelve `403` antes de buscar o modificar la venta;
- el botón permanece oculto;
- contado y crédito muestran:
  `No tienes permiso para anular ventas. Solicita autorización a George.`

No se cambió la matriz de permisos.

## Otras llamadas críticas revisadas

| Área | Resultado |
| --- | --- |
| Login y sesión | Usan el cliente central |
| Dashboard y cuadre | Usan el cliente central |
| Ventas contado/crédito | Comparten el cliente y `voidCashSale` |
| Cobros y cartera | Usan el cliente central |
| Clientes | Usa el cliente central |
| Reportes administrativos | Usan el cliente central |
| Exportaciones Excel/PDF | Migradas al mismo `apiFetch` |
| Usuarios, precios, inventario, producción y nómina | Usan el cliente central |

No se hizo una reestructuración masiva de `api.ts`; solo se unificó el
transporte y la URL. Dividir el cliente por dominios continúa como deuda
postpiloto, sin duplicar la lógica de red.

## Validación y despliegue

Validaciones aprobadas:

- 122 pruebas dirigidas de permisos, contado y crédito;
- 973 pruebas backend completas, con un warning conocido de
  `TestClient/httpx`;
- 7 pruebas de URL para LAN, Tailscale, localhost y SSR;
- preflight `POST` con `status=200` y `Access-Control-Allow-Origin` correcto
  para LAN, Tailscale y localhost;
- `npm run typecheck`;
- `npm run build`, con 38 rutas;
- build Docker productivo de `api` y `web`;
- `docker compose config --quiet`;
- consulta real contra PostgreSQL con ID inexistente y rollback:
  `POSTGRES_LOCK_QUERY_OK`.

El despliegue se hizo con `--no-deps` y recreó únicamente `api` y `web`.
El contenedor `db` conservó su identidad y tiempo de ejecución; no se reinició,
no se ejecutaron migraciones y no se tocaron volúmenes.

El health posterior confirmó:

- `db`, `api` y `web` en estado `healthy`;
- API localhost, LAN y Tailscale: `status=ok`;
- Web LAN y Tailscale disponible;
- Alembic en `0026_user_roles`;
- PostgreSQL `5432` no publicado;
- cero fallos críticos y cero advertencias informativas.

Después del despliegue se envió un `POST` no autenticado y sin posibilidad de
modificar datos a un ID inexistente. El API lo registró y respondió `401`, como
corresponde; no apareció `500`. La ejecución PostgreSQL separada con rollback
confirmó que la consulta corregida sí es aceptada por el motor productivo.

## Estado operativo

La causa técnica está corregida y desplegada. No se anuló una venta real porque
no hubo autorización explícita de George para alterar una operación productiva.
La comprobación humana con `admin_auditor`, motivo real y una venta cuya
anulación esté autorizada continúa pendiente; hasta entonces la incidencia se
mantiene **en revisión operativa** y el método manual paralelo sigue activo.

Si la regla de negocio responde `409`, se debe conservar su mensaje y resolver
primero el vínculo indicado. Si surge otra incidencia, registrar hora, usuario,
origen LAN/Tailscale, referencia de venta y mensaje visible sin reintentar a
ciegas.

## Bloque posterior: corrección de fechas

La corrección de fechas no forma parte de 60B-2. Debe ejecutarse en un bloque
posterior y separado, con casos de borde para `America/Guayaquil`, fechas de
venta y vencimiento, reportes y operaciones alrededor de medianoche. No debe
mezclarse con anulación ni con producción/insumos.
