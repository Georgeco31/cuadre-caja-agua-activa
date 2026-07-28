# Ajuste de textos profesionales de la interfaz

## Objetivo

Actualizar únicamente los textos visibles del login y del encabezado principal
del dashboard para presentar Agua Activa como un ERP de gestión integral, sin
alterar lógica de negocio, autenticación, permisos, endpoints ni navegación.

## Login

Los textos del encabezado quedaron así:

- título: `Agua Activa ERP`;
- subtítulo: `Sistema de gestión operativa y control interno`;
- texto secundario:
  `Accede para gestionar caja, ventas, rutas, producción, reportes y administración.`

El formulario, sus campos, el envío, el manejo de errores y las redirecciones
permanecen sin cambios. El logo integrado en el bloque 57E se conserva.

## Dashboard

El título dinámico que incluía el username se reemplazó por el título fijo
`Panel operativo`. El username permanece únicamente como información secundaria
en la topbar y en la tarjeta de sesión del sidebar.

La descripción usa el rol ya cargado por la página:

- `admin_auditor`:
  `Gestiona caja, ventas, rutas, producción y reportes desde un solo lugar.`;
- `operator`: `Gestiona las tareas operativas asignadas del día.`

Se mantienen sin cambios los badges `Acceso administrador` y
`Acceso operador`.

## Alcance preservado

- No se modificó `apps/api`.
- No se modificaron autenticación, permisos, endpoints ni payloads.
- No se modificó la lógica de carga del dashboard.
- No se modificaron navegación, destinos ni exportaciones.
- No se modificaron migraciones, seeds, Docker, scripts ni
  `.env.production.local`.
- No se instalaron dependencias.
- No se hizo `git add`, commit ni push.

## Validaciones

- `npm run typecheck`: aprobado;
- `npm run build`: aprobado, 38 rutas generadas;
- `git diff --check`: aprobado;
- `/login` en 412 × 915 px: textos nuevos y logo aprobados;
- encabezado del dashboard para `admin_auditor`: título, descripción y badge
  aprobados;
- encabezado del dashboard para `operator`: título, descripción y badge
  aprobados;
- encabezados del dashboard en 390 × 844 px: aprobados;
- ausencia de los textos anteriores en login y dashboard: comprobada;
- ausencia de un username en el título principal: comprobada;
- ausencia de scroll horizontal en las vistas revisadas: comprobada;
- `/dashboard` sin sesión conserva la redirección a `/login`;
- rebuild de producción local: aprobado;
- health check final: aprobado;
- `/login` productivo y login real: aprobados;
- título y textos profesionales del login: aprobados;
- ausencia de los dos textos antiguos del login: comprobada;
- `/dashboard` productivo con `Panel operativo`: aprobado;
- ausencia de `Buen día, admin` y `Buen día, estherdelgado31` como título
  principal: comprobada;
- username limitado a topbar y sidebar como dato secundario: comprobado;
- `/dashboard/exports`: aprobado;
- acceso por LAN: aprobado;
- acceso por Tailscale: aprobado cuando fue incluido en la prueba;
- revisión responsive y ausencia de scroll horizontal: aprobadas;
- staging: vacío.

George completó la validación real después del despliegue local. La reserva por
falta de una sesión autenticada quedó resuelta sin modificar credenciales,
usuarios, datos, permisos ni autenticación.

## Problemas pendientes

No quedan problemas ni validaciones pendientes para el alcance de este ajuste.

## Cierre

El ajuste de textos profesionales de login y dashboard queda validado en
producción local y listo para cierre.
