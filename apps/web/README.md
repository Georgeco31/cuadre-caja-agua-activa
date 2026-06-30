# Frontend - Cuadre de Caja Agua Activa

App web Next.js para el MVP de Cuadre de Caja Agua Activa.

Este frontend incluye login, dashboard inicial y pantalla de cuadre diario para registrar cantidades de monedas, billetes y gastos contra la API. Todavía no incluye historial visual, correcciones, edición de gastos, eliminación de gastos, cookies ni refresh tokens.

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

## Build

```bash
npm run build
```

## Flujo actual

- Login en `/login`.
- Dashboard protegido en `/dashboard`.
- Enlace desde dashboard hacia `/dashboard/cash-session`.
- La pantalla de cuadre diario consulta o crea el cuadre del día.
- Denominaciones cargadas desde `GET /api/v1/denominations`.
- Conteos enviados con `POST /api/v1/cash-sessions/{id}/count-items`.
- Gastos listados desde `GET /api/v1/cash-sessions/{id}/expenses`.
- Gastos registrados con `POST /api/v1/cash-sessions/{id}/expenses`.
- Resumen cargado desde `GET /api/v1/cash-sessions/{id}/summary`.
- Cierre de cuadre con `POST /api/v1/cash-sessions/{id}/close`.
- Token JWT guardado en `localStorage` para el MVP inicial.
- Logout elimina el token y vuelve a `/login`.

El uso de `localStorage` es una solución simple para desarrollo. No reemplaza una estrategia completa de seguridad para producción.
