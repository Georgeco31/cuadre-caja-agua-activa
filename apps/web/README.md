# Frontend - Cuadre de Caja Agua Activa

App web Next.js para el MVP de Cuadre de Caja Agua Activa.

Este bloque incluye solamente login, dashboard inicial y comunicación básica con la API. Todavía no incluye formularios de cuadre diario, conteo de monedas, gastos, historial visual, correcciones, cookies ni refresh tokens.

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

## Build

```bash
npm run build
```

## Flujo actual

- Login en `/login`.
- Dashboard protegido en `/dashboard`.
- Token JWT guardado en `localStorage` para el MVP inicial.
- Logout elimina el token y vuelve a `/login`.

El uso de `localStorage` es una solución simple para desarrollo. No reemplaza una estrategia completa de seguridad para producción.
