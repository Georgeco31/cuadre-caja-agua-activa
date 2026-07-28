# Bloque 57E - Branding, logos e identidad visual

## Objetivo

Integrar los archivos reales de marca de Agua Activa en el frontend del ERP,
manteniendo intactos la autenticación, los permisos, los endpoints, los
payloads, los cálculos y la lógica de negocio.

## Archivos usados

- `apps/web/public/brand/logo-horizontal.png`: marca completa con la mascota,
  el nombre y el lema, en formato PNG de 1105 × 739 px.
- `apps/web/public/brand/logo-icon.png`: mascota de Agua Activa, en formato PNG
  de 1080 × 1435 px.

Los archivos se copiaron desde los originales proporcionados para el bloque. No
se recortaron, deformaron, recomprimieron ni sustituyeron por imágenes externas.

## Aplicación de la marca

### Login

El logo completo aparece centrado sobre el encabezado del formulario, con ancho
y alto máximos y `object-contain` para respetar su proporción. El texto
`Agua Activa ERP` permanece visible y el formulario conserva su estructura,
campos, envío, autenticación y redirecciones.

### Sidebar de escritorio

La mascota reemplaza al marcador temporal `AA` dentro de un contenedor blanco
de 44 × 44 px. Se mantienen el ancho del sidebar y los textos `Agua Activa` y
`Gestión ERP`.

### Topbar móvil

La mascota reemplaza al marcador temporal `AA` en el acceso compacto al inicio.
El contenedor conserva 40 × 40 px, no invade el contenido y no cambia la
navegación inferior.

### Favicon y metadata

`logo-icon.png` se configuró como icono y Apple touch icon provisionales. El
título general se actualizó a `Agua Activa ERP` y la descripción a
`Gestión operativa de Agua Activa`.

## Componente `BrandLogo`

`apps/web/components/ui/BrandLogo.tsx` es un componente presentacional con las
variantes `full` e `icon` y una propiedad opcional `className`. Usa únicamente:

- `/brand/logo-horizontal.png`;
- `/brand/logo-icon.png`.

Ambas variantes incluyen `alt="Agua Activa"` y `object-contain`. El componente
no hace `fetch`, no lee tokens, no consulta permisos y no llama a la API.

Si un archivo no puede cargarse, el componente muestra el fallback textual
`Agua Activa ERP`. Una ausencia accidental del PNG no rompe el build.

## Validaciones realizadas

- `git diff --check`: aprobado, sin errores;
- `npm run typecheck` en `apps/web`: aprobado;
- `npm run build` en `apps/web`: aprobado, 38 rutas generadas;
- `docker compose ... config --quiet`: aprobado;
- `docker compose ... ps`: `db`, `api` y `web` saludables;
- `/login` en 1280 × 900 px: aprobado visualmente;
- `/login` en 390 × 844 px y 412 × 915 px: aprobado visualmente;
- shell del dashboard en 1280 × 900 px: logo del sidebar aprobado;
- shell del dashboard en 390 × 844 px y 412 × 915 px: logo compacto,
  topbar y navegación inferior aprobados;
- imágenes: carga completa, dimensiones naturales correctas y
  `object-fit: contain`;
- favicon y título `Agua Activa ERP`: aprobados;
- ausencia de scroll horizontal en las vistas comprobadas: aprobada;
- `/dashboard` y `/dashboard/exports` sin sesión: ambas rutas conservan la
  redirección a `/login`;
- rebuild de producción local: aprobado;
- health check final: aprobado;
- `/login` productivo, logo y textos de Agua Activa ERP: aprobados;
- login real: aprobado;
- `/dashboard` productivo, sidebar y topbar: aprobados;
- `/dashboard/exports`: aprobado;
- acceso por LAN: aprobado;
- acceso por Tailscale: aprobado cuando fue incluido en la prueba;
- revisión responsive y ausencia de scroll horizontal: aprobadas;
- `git diff --cached --stat`: vacío; no existe staging.

George completó la validación real después del despliegue local. La reserva
anterior por falta de una sesión autenticada quedó resuelta.

## Seguridad y alcance

- No se modificó `apps/api`.
- No se modificaron migraciones ni seeds.
- No se modificaron Dockerfiles, archivos Compose ni scripts.
- No se modificó `.env.production.local`.
- No se cambiaron autenticación, redirecciones, permisos, endpoints, payloads
  ni cálculos.
- No se instalaron dependencias.
- No se hizo `git add`, commit ni push.
- No se exponen secretos ni archivos de `backups/`.

## Problemas pendientes

No hay archivos de marca faltantes ni validaciones funcionales pendientes para
el alcance de este bloque.

## Recomendación futura

Crear un favicon o isotipo simplificado específico de 512 × 512 px, con buena
legibilidad a tamaños pequeños, y sustituir el uso provisional de la mascota
completa en metadata.

## Cierre

La integración de branding y logos queda validada en producción local y lista
para cierre. No se modificaron credenciales, backend, endpoints ni permisos
durante la validación.
