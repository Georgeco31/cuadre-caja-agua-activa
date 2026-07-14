# Frontend - Cuadre de Caja Agua Activa

App web Next.js para el MVP de Cuadre de Caja Agua Activa.

Este frontend incluye login, panel operativo de dashboard, pantalla de cuadre diario, historial con detalle de cuadres, reporte acumulado, gastos separados por momento del conteo e interfaz de correcciones controladas para cuadres cerrados. Todavía no incluye edición de gastos, eliminación de gastos, edición desde historial, cookies ni refresh tokens.

## Requisitos

- Node.js 20 o superior.
- Backend FastAPI levantado.

## Variables

Crear `.env.local` en `apps/web` si se desea cambiar la URL de la API:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8010/api/v1
```

Si el backend se levanta con Docker en el puerto por defecto del proyecto:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8010/api/v1
```

## Instalación

Desde `apps/web`:

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

Abrir:

```text
http://localhost:3000/login
```

Rutas principales:

- `/login`
- `/dashboard`
- `/dashboard/cash-session`
- `/dashboard/history`
- `/dashboard/history/[cashSessionId]`
- `/dashboard/reports`

## Build

```bash
npm run build
```

## Docker Compose

Desde la raiz del proyecto:

```bash
./scripts/local-start.sh
```

La web queda disponible en:

```text
http://localhost:3000/login
```

## Flujo actual

- Login en `/login`.
- Dashboard protegido en `/dashboard`.
- El dashboard consulta el usuario actual desde `GET /api/v1/auth/me`.
- El dashboard consulta el cuadre de hoy desde `GET /api/v1/cash-sessions/by-date/{session_date}`.
- Si existe cuadre de hoy, el dashboard muestra el resumen oficial desde `GET /api/v1/cash-sessions/{id}/summary`.
- El dashboard muestra acciones rápidas hacia `/dashboard/cash-session`, `/dashboard/history` y `/dashboard/reports`.
- El dashboard muestra los últimos cuadres registrados desde `GET /api/v1/cash-sessions` y el total final desde el resumen oficial de cada cuadre.
- El dashboard muestra un recordatorio de backup para el cierre del día o fin de pruebas.
- La pantalla de cuadre diario muestra un selector de fecha con la fecha actual por defecto.
- Al cambiar la fecha, la pantalla consulta `GET /api/v1/cash-sessions/by-date/{session_date}` y limpia los datos visibles de la fecha anterior.
- Si no existe cuadre para la fecha seleccionada, muestra la opcion para crearlo con `POST /api/v1/cash-sessions`.
- Si existe cuadre para la fecha seleccionada, lo carga sin crear duplicados.
- La pantalla de cuadre diario precarga montos contados desde el `subtotal` guardado en `GET /api/v1/cash-sessions/{id}/count-items`.
- Si no hay conteo guardado para una denominación, el input muestra `0.00`.
- El operador ingresa monto contado por denominación; el frontend convierte ese monto a `quantity` antes de enviar al backend.
- El historial lista cuadres desde `GET /api/v1/cash-sessions`.
- El historial permite filtrar por fecha desde, fecha hasta y estado usando `date_from`, `date_to` y `status`.
- El detalle consulta resumen, conteos y gastos del cuadre.
- Denominaciones cargadas desde `GET /api/v1/denominations`.
- Conteos enviados con `POST /api/v1/cash-sessions/{id}/count-items`; el backend sigue recibiendo `quantity` y calculando `subtotal`.
- Conteos listados desde `GET /api/v1/cash-sessions/{id}/count-items`.
- Gastos listados desde `GET /api/v1/cash-sessions/{id}/expenses`.
- Gastos antes del conteo registrados con `POST /api/v1/cash-sessions/{id}/expenses` usando `expense_timing: "before_count"`.
- Gastos despues del conteo registrados con `POST /api/v1/cash-sessions/{id}/expenses` usando `expense_timing: "after_count"`.
- Resumen cargado desde `GET /api/v1/cash-sessions/{id}/summary`.
- El resumen muestra gastos antes del conteo como control y gastos despues del conteo como el monto que se resta del total contado.
- Cierre de cuadre con `POST /api/v1/cash-sessions/{id}/close`.
- Antes de cerrar, el frontend muestra una confirmación con el resumen oficial actual.
- Resumen acumulado cargado desde `GET /api/v1/reports/cash-summary`.
- Correcciones listadas desde `GET /api/v1/cash-sessions/{id}/corrections`.
- Conteos corregidos desde `POST /api/v1/cash-sessions/{id}/corrections/count-items`.
- Gastos correctivos registrados desde `POST /api/v1/cash-sessions/{id}/corrections/expenses`.
- Token JWT guardado en `localStorage` para el MVP inicial.
- Logout elimina el token y vuelve a `/login`.

En el detalle de historial, los gastos se muestran separados entre antes del conteo y despues del conteo. Las correcciones solo se habilitan para cuadres con estado `closed`. Despues de cada correccion, el frontend vuelve a consultar el resumen oficial, los listados afectados y los logs de correccion desde la API.

La pantalla `/dashboard/reports` muestra el resumen acumulado de caja basado en cuadres registrados, incluyendo gastos antes del conteo y gastos despues del conteo. No representa ventas reales porque el sistema aun no registra ventas ni saldo inicial de caja.

El uso de `localStorage` es una solución simple para desarrollo. No reemplaza una estrategia completa de seguridad para producción.
