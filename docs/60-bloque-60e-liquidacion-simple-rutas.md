# 60 - Bloque 60E: liquidación simple de rutas

## Contexto

Agua Activa continúa en piloto controlado. La producción local parte de
Alembic `0027_sale_date_corrections`, julio todavía no ha cerrado y no se ha
registrado stock inicial real de agosto. El método manual sigue activo en
paralelo.

El Bloque 60D confirmó que la carga rechaza cantidades superiores al stock,
que el retorno mueve el sobrante hacia una ubicación no vehicular y que ventas,
cobros y cierre financiero pueden asociarse a una carga. También confirmó que
esos registros estaban separados y no ofrecían una comparación física sencilla.

## Problema operativo

George necesita revisar cada carro con la secuencia real:

`cantidad cargada - cantidad retornada = cantidad vendida físicamente`

Esa cantidad debe compararse con las partidas de ventas asociadas a la carga.
El efectivo esperado debe compararse con el dinero entregado que ya registra el
cierre financiero. Antes de este bloque había que reunir esos datos en
pantallas separadas.

## Alcance implementado

Se agregó un resumen calculado y de solo lectura:

`GET /api/v1/route-loads/{id}/settlement-summary`

El endpoint reutiliza las tablas existentes de carga, retorno, ventas, cobros y
cierre financiero. No fue necesaria una tabla nueva ni una migración 0028.

La pantalla `/dashboard/route-closures` pasó a presentar una
**Liquidación simple de ruta**. Cualquier usuario autenticado con acceso al
módulo puede seleccionar una carga activa y consultar el resumen. Solo
`admin_auditor` conserva la capacidad de registrar o anular el cierre
financiero.

La pantalla muestra:

- carga, fecha, ruta, vehículo y conductor de referencia cuando existe;
- cantidad cargada y retornada;
- vendido físico calculado;
- vendido registrado y diferencia física;
- detalle por producto;
- importe de ventas registradas;
- cobros registrados;
- dinero esperado;
- dinero entregado;
- diferencia de dinero;
- estado y mensajes operativos;
- observaciones de retorno y de cierre.

## Qué calcula el resumen

Por producto y para el total de la carga:

- `physical_sold_quantity = loaded_quantity - returned_quantity`;
- `physical_vs_registered_difference = physical_sold_quantity -
  registered_sold_quantity`;
- `registered_sales_amount = cash_sales_amount + credit_sales_amount`;
- `expected_cash_amount = cash_sales_amount + registered_payments_amount`;
- `cash_difference = delivered_cash_amount - expected_cash_amount`.

Si existe un cierre activo, los importes monetarios se leen de sus snapshots
oficiales. Si todavía no existe, se leen de la actividad comercial activa de la
carga. Consultar el resumen no congela ni modifica esos datos.

Un producto registrado en ventas que no estaba en la carga también aparece en
el detalle, con cantidad cargada cero, para que la diferencia sea visible.

## Estados y mensajes

- `pending`: falta un retorno activo o todavía no existe dinero entregado en un
  cierre activo.
- `balanced`: existe retorno, existe dinero entregado y las diferencias de
  producto y dinero son cero.
- `with_difference`: la información está completa y existe diferencia de
  producto o dinero.

La interfaz presenta mensajes claros:

- “No hay retorno registrado todavía.”
- “No hay dinero entregado registrado todavía.”
- “La ruta tiene diferencia de producto.”
- “La ruta tiene diferencia de dinero.”
- “La ruta está cuadrada.”

Cuando el administrador va a registrar un cierre y la pantalla ya detecta una
diferencia física o una diferencia estimada de dinero, la observación se vuelve
obligatoria en la interfaz para dejar el motivo visible.

## Reglas de negocio conservadas

1. Una carga sigue requiriendo stock suficiente en la ubicación de origen.
2. Un retorno no puede superar la cantidad cargada ni el stock del vehículo.
3. Solo existe un retorno activo por carga.
4. Solo existe un cierre financiero activo por carga.
5. El resumen queda pendiente si falta retorno.
6. El resumen queda pendiente si falta dinero entregado.
7. La consulta no crea, edita ni anula ventas.
8. La consulta no crea, edita ni anula cobros.
9. La consulta no mueve inventario.
10. El cierre financiero conserva sus bloqueos y snapshots existentes.
11. No se borra ningún registro.

## Permisos

| Acción | `operator` | `admin_auditor` |
| --- | --- | --- |
| Consultar liquidación simple | Sí | Sí |
| Consultar cierres e historial | Sí | Sí |
| Registrar cierre financiero | No | Sí |
| Anular cierre financiero | No | Sí |

La protección se conserva tanto en backend como en frontend. El nuevo endpoint
es de solo lectura y no introduce una acción crítica adicional.

## Impacto

### Inventario

El resumen lee la carga y el retorno existentes. No descuenta ventas del
vehículo, no crea ajustes, no cambia stock y no registra el stock inicial de
agosto.

### Caja

El resumen muestra dinero esperado, entregado y diferencia. No crea un cuadre,
no cambia denominaciones, no registra automáticamente el dinero en caja y no
reemplaza el módulo trazable de recibos de ruta.

### Rutas

La revisión física y financiera queda reunida por carga y por producto. El
cierre sigue siendo financiero: no se convierte en una liquidación automática
de inventario.

### Relación con agosto

El bloque prepara la revisión de rutas de agosto, pero no autoriza registrar
stock inicial. Primero debe cerrar julio, completarse el conteo físico por
ubicación y existir autorización expresa de George. Hasta entonces no se
inventan cantidades y el método manual se mantiene.

## Qué no resuelve todavía

- Las ventas de ruta no descuentan inventario del vehículo automáticamente.
- No existe liquidación automática completa que genere salidas por venta.
- No existe detalle agrupado por precio dentro de la liquidación.
- El control avanzado de bidones retornables sigue pendiente.
- El stock por ubicación existe, pero no hay conciliación automática
  bodega/carro contra conteo físico.
- No se persiste una diferencia de inventario por chofer/ruta como incidencia
  independiente.
- El cierre financiero no exige técnicamente que el retorno se registre antes.
- La integración exacta con agosto depende del cierre de julio y del conteo
  físico real.

## Pruebas agregadas

Backend:

- carga sin retorno ni cierre queda pendiente;
- carga, retorno y ventas calculan vendido físico y diferencia;
- retorno y cierre sin diferencias quedan cuadrados;
- diferencia de dinero queda visible con su observación;
- `operator` y `admin_auditor` pueden consultar;
- consultar no modifica ventas, cobros, cierres, movimientos ni stock;
- el endpoint exige autenticación;
- las pruebas existentes de retorno mayor a carga, cargas, retornos y cierres
  permanecen vigentes.

Frontend:

- etiquetas de los tres estados;
- mensajes de pendiente, diferencia y cuadrada;
- observación exigida en la interfaz cuando hay diferencia;
- presentación adaptable con tarjetas y tabla desplazable en pantallas
  estrechas;
- acciones administrativas ocultas para `operator`.

## Validaciones realizadas

Durante el desarrollo y el cierre técnico aprobaron:

- `python -m pytest tests/test_route_closures_endpoints.py -q`: 30 pruebas;
- `.venv\Scripts\python.exe -m pytest`: 994 pruebas;
- `npm run test`: 16 pruebas;
- `npm run typecheck`;
- `npm run build`: 38 rutas generadas;
- `docker compose -f docker-compose.prod.yml --env-file
  .env.production.local config --quiet`;
- `scripts/prod-local-health.ps1`: localhost, LAN y Tailscale OK; `db`, `api` y
  `web` saludables; Alembic en 0027; PostgreSQL 5432 no publicado;
- revisión visual temporal en escritorio y 390 px: sin desbordamiento de
  página, tarjetas adaptables, tabla desplazable, motivo obligatorio y cero
  errores de consola.

La revisión final de Git confirmó `git diff --check` limpio y staging vacío.

## Despliegue productivo controlado 60E-2

El 2026-07-29 se construyeron y recrearon únicamente `api` y `web` con
`--no-deps --force-recreate`. No se ejecutó `down`, no se borraron volúmenes,
no se aplicaron migraciones, no se modificó `.env.production.local` y no se
reinició PostgreSQL.

La comprobación antes y después registró para `db` el mismo contenedor, la misma
hora de inicio (`2026-07-28T04:43:27.981193771Z`) y `RestartCount = 0`. Alembic
permaneció en `0027_sale_date_corrections`; no existe ni se aplicó una revisión
0028.

El health posterior aprobó:

- `db`, `api` y `web` en estado saludable;
- API por localhost, LAN y Tailscale;
- Web por LAN y Tailscale;
- PostgreSQL 5432 sin publicar;
- Compose productivo válido.

## Humo productivo 60E-2

Se usaron usuarios activos existentes y tokens efímeros conservados solo en
memoria. No se mostraron usuarios, contraseñas ni tokens.

Resultados:

- lecturas de clientes, ventas, cobros, cargas, cierres, caja y resumen diario
  respondieron para `operator`;
- usuarios, panel gerencial y exportación de rutas respondieron para
  `admin_auditor`;
- usuarios, panel, exportaciones, anulación y corrección de fecha restringidos
  devolvieron `403` para `operator`;
- una carga inexistente devolvió `404` en `settlement-summary`;
- no existía ninguna carga real en producción para obtener un `200`;
- una huella de las 49 tablas y 705 filas fue idéntica antes y después del humo;
- no aparecieron respuestas 5xx, trazas ni errores recientes en API o Web.

La fórmula, los tres estados y el acceso de ambos roles sobre una carga
existente permanecen cubiertos por las 30 pruebas dirigidas aprobadas antes del
despliegue. No se crearon cargas falsas para sustituir la evidencia operativa.

El formulario de acceso productivo respondió por localhost, LAN y Tailscale.
Con credenciales ficticias mostró `Usuario o contraseña incorrectos.`, liberó
el botón y no generó errores de consola. En 390 × 844 no hubo desbordamiento
horizontal. Una navegación sin sesión a cierre de rutas volvió correctamente a
`/login`.

No había una sesión autenticada disponible para inspeccionar en producción la
pantalla de cierre con `admin_auditor` y `operator`, y no se usaron ni cambiaron
credenciales reales. Por tanto quedan pendientes:

1. abrir la liquidación con una carga real cuando exista y comprobar su `200`
   contra la revisión manual;
2. confirmar visualmente en escritorio y móvil el resumen autenticado;
3. reconfirmar que `operator` no ve acciones administrativas y que
   `admin_auditor` sí las conserva.

Hasta completar esas comprobaciones con datos y cuentas reales autorizados, el
método manual paralelo continúa vigente. El despliegue no cargó stock inicial,
no modificó ventas, cobros, caja, inventario, precios, permisos ni credenciales.
