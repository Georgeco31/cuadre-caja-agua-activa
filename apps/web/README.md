# Frontend - Cuadre de Caja Agua Activa

App web Next.js para el MVP de Cuadre de Caja Agua Activa.

Este frontend incluye login, dashboard inicial, pantalla de cuadre diario, historial con detalle de cuadres e interfaz de correcciones controladas para cuadres cerrados. Todavía no incluye edición de gastos, eliminación de gastos, edición desde historial, cookies ni refresh tokens.

## Requisitos

- Node.js 20 o superior.
- Backend FastAPI levantado.

## Variables

Crear `.env.local` en `apps/web` si se desea cambiar la URL de la API:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8010/api/v1
```

Si el backend se levanta con Docker en el puerto por defecto:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
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

## Build

```bash
npm run build
```

## Flujo actual

- Login en `/login`.
- Dashboard protegido en `/dashboard`.
- Enlace desde dashboard hacia `/dashboard/cash-session`.
- Enlace desde dashboard hacia `/dashboard/history`.
- La pantalla de cuadre diario consulta o crea el cuadre del día.
- El historial lista cuadres desde `GET /api/v1/cash-sessions`.
- El detalle consulta resumen, conteos y gastos del cuadre.
- Denominaciones cargadas desde `GET /api/v1/denominations`.
- Conteos enviados con `POST /api/v1/cash-sessions/{id}/count-items`.
- Conteos listados desde `GET /api/v1/cash-sessions/{id}/count-items`.
- Gastos listados desde `GET /api/v1/cash-sessions/{id}/expenses`.
- Gastos registrados con `POST /api/v1/cash-sessions/{id}/expenses`.
- Resumen cargado desde `GET /api/v1/cash-sessions/{id}/summary`.
- Cierre de cuadre con `POST /api/v1/cash-sessions/{id}/close`.
- Correcciones listadas desde `GET /api/v1/cash-sessions/{id}/corrections`.
- Conteos corregidos desde `POST /api/v1/cash-sessions/{id}/corrections/count-items`.
- Gastos correctivos registrados desde `POST /api/v1/cash-sessions/{id}/corrections/expenses`.
- Token JWT guardado en `localStorage` para el MVP inicial.
- Logout elimina el token y vuelve a `/login`.

En el detalle de historial, las correcciones solo se habilitan para cuadres con estado `closed`. Despues de cada correccion, el frontend vuelve a consultar el resumen oficial, los listados afectados y los logs de correccion desde la API.

El uso de `localStorage` es una solución simple para desarrollo. No reemplaza una estrategia completa de seguridad para producción.
