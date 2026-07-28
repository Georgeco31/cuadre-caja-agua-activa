# 41 - Bloque 58D: pruebas integrales de permisos

## Estado

- Fecha: **2026-07-28**.
- Código fuente actual: **aprobado**.
- Suite específica de permisos: **42 passed**.
- Suite backend completa: **972 passed**.
- Frontend: **typecheck y build aprobados; 38 rutas generadas**.
- Navegación por rol y responsive: **aprobados en entorno aislado**.
- Health productivo LAN/Tailscale: **aprobado**.
- Rebuild productivo 58D-2: **aprobado y sin eliminación de volúmenes**.
- Smoke backend sobre la API productiva reconstruida: **26/26 comprobaciones
  aprobadas**.
- Artefacto web productivo: **sincronizado; contiene el bloqueo compilado de
  58C**.
- Smoke frontend productivo y responsive: **aprobado para ambos roles**.
- Cierre integral en producción: **58D aprobado sin reserva por deriva de
  despliegue**.

58D demostró que el código actual de 58B y 58C aplica la política aprobada y
detectó que las imágenes entonces desplegadas estaban desfasadas. George
autorizó expresamente 58D-2. Se realizó backup, se reconstruyeron `api` y `web`
con el código validado, se conservaron los volúmenes y la base de datos, y se
repitieron health y permisos reales sobre la API productiva.

## Objetivo

Comprobar de punta a punta que:

- `admin_auditor` conserva control total;
- `operator` conserva las tareas diarias aprobadas;
- el frontend oculta o bloquea las acciones restringidas;
- el backend actual responde `403` aunque se intente una petición directa;
- Excel y PDF siguen disponibles para administración;
- la interfaz mantiene su comportamiento en escritorio y móvil;
- LAN, Tailscale, Docker, Alembic y PostgreSQL continúan sanos.

## Relación con 58A, 58B y 58C

- **58A** definió la matriz y las decisiones oficiales de George.
- **58B** implementó la autorización real del backend.
- **58C** alineó tarjetas, navegación, rutas y acciones del frontend.
- **58D** ejecuta las pruebas específicas, la suite completa y el recorrido
  visual de ambos roles, y registra la diferencia encontrada entre el código y
  las imágenes productivas.
- **58D-2** reconstruye producción con autorización de George, conserva los
  datos y comprueba que la API desplegada ya aplica los `403` de 58B y que la
  compilación web desplegada ya contiene el bloqueo de 58C.

La interfaz continúa siendo una ayuda de uso. La autorización del backend es la
protección real.

## Resumen de roles

| Rol | Alcance validado |
| --- | --- |
| `admin_auditor` | 33 destinos, administración, configuración, personal, nómina, reportes sensibles, Excel/PDF, correcciones y anulaciones. |
| `operator` | 22 destinos, caja y cierre diario, clientes, ventas, cobros, producción diaria e inventario `entry`/`exit` sin costo. |

## Entorno de prueba visual

Las pruebas de navegador usaron el frontend actual y una API temporal con:

- código backend actual montado en modo solo lectura;
- SQLite dentro de un contenedor desechable;
- usuarios ficticios de ambos roles;
- ausencia total de conexión con la base productiva.

Solo se crearon en esa base desechable un cliente y un cuadre para comprobar el
cierre y la vista histórica. El contenedor y su base fueron eliminados al
terminar. No se borraron ni modificaron datos reales.

## Pruebas de `admin_auditor`

| Pantalla | Resultado |
| --- | --- |
| `/dashboard` | Aprobado; muestra **33 destinos disponibles** y acceso administrador. |
| `/dashboard/management` | Aprobado; panel gerencial y acciones de exportación visibles. |
| `/dashboard/exports` | Aprobado; botones **Descargar Excel** y **Descargar PDF** visibles. |
| `/dashboard/users` | Aprobado; listado, creación y acciones administrativas visibles. |
| `/dashboard/pricing` | Aprobado; listas y resolución de precios disponibles. |
| `/dashboard/payroll` | Aprobado; período, empleados y roles registrados disponibles. |
| `/dashboard/employees/control` | Aprobado; control de empleados accesible. |
| `/dashboard/production/recipes` | Aprobado; fórmulas y nueva fórmula visibles. |
| `/dashboard/reports` | Aprobado; resumen acumulado accesible. |
| `/dashboard/daily-summary` | Aprobado; resumen operativo diario accesible. |
| `/dashboard/monthly-summary` | Aprobado; reporte mensual y formatos visibles. |

Ninguna pantalla mostró un mensaje de restricción ni un error técnico crudo.
Todas las páginas revisadas mantuvieron ancho válido en el viewport probado.

## Pruebas de `operator`

| Pantalla o acción | Resultado |
| --- | --- |
| `/dashboard` | Aprobado; **22 destinos disponibles**, sin enlaces administrativos ni Reportes en la navegación. |
| `/dashboard/cash-session` | Aprobado; permite crear/abrir cuadre. |
| Crear cliente | `201 Created` en la base aislada y formulario visible. |
| Crear cuadre | `201 Created` en la base aislada. |
| Cerrar cuadre | `200 OK`; el estado quedó cerrado. |
| Corregir el cuadre cerrado | `403 Forbidden`; no hubo cambio. |
| `/dashboard/history/1` | Aprobado; muestra el detalle cerrado sin formularios ni logs de corrección. |
| `/dashboard/customers` | Aprobado; alta y consulta disponibles, sin edición administrativa. |
| `/dashboard/sales/cash` | Aprobado; **Registrar venta** visible, sin anulación. |
| `/dashboard/sales/credit` | Aprobado; **Registrar venta a crédito** visible, sin anulación. |
| `/dashboard/receivables` | Aprobado; **Registrar abono** visible, sin anulación. |
| `/dashboard/production` | Aprobado; registro diario visible, sin aplicar a inventario ni anular. |
| `/dashboard/inventory` | Aprobado; solo `Entrada` y `Salida`, sin costo, ajuste, ubicación ni anulación. |

Las pruebas automatizadas positivas también cubrieron cierre de caja, alta de
clientes, venta a crédito, cobro, producción diaria y movimientos operativos
de inventario.

## Pruebas de URL directa para `operator`

| URL | Resultado |
| --- | --- |
| `/dashboard/management` | Bloqueada. |
| `/dashboard/exports` | Bloqueada. |
| `/dashboard/users` | Bloqueada. |
| `/dashboard/pricing` | Bloqueada. |
| `/dashboard/payroll` | Bloqueada. |
| `/dashboard/employees/control` | Bloqueada. |
| `/dashboard/production/recipes` | Bloqueada. |

Las siete rutas mostraron:

- “Esta sección está disponible solo para administrador/auditor”;
- indicación de solicitar autorización a George;
- enlace para volver al panel operativo;
- ausencia del contenido administrativo;
- ausencia de `Forbidden`, `role mismatch` o mensajes internos.

## Pruebas backend

### Suite específica

```text
42 passed, 1 warning in 20.79s
```

La advertencia es la ya conocida de deprecación entre
`Starlette TestClient` y `httpx`; no representa un fallo funcional.

Los 42 casos comprueban:

- `401` sin autenticación;
- `403` del operador en familias administrativas y acciones críticas;
- denegación de acciones que, si fueran autorizadas, producirían escrituras;
- acceso del administrador a familias restringidas;
- operaciones aprobadas de caja, clientes, ventas, cobros, producción e
  inventario.

### Suite completa

```text
972 passed, 1 warning in 348.88s
```

### Peticiones directas contra el código actual

| Método y endpoint | Resultado `operator` |
| --- | ---: |
| `GET /reports/management-dashboard` | `403` |
| `GET /reports/exports/management-dashboard.xlsx` | `403` |
| `GET /users` | `403` |
| `GET /employees` | `403` |
| `GET /payroll/runs` | `403` |
| `POST /pricing/price-lists` | `403` |
| `POST /production/recipes` | `403` |

La prueba de cierre aislada obtuvo `201` al crear el cuadre, `200` al cerrarlo y
`403` al intentar corregirlo después.

## Pruebas frontend

| Comando | Resultado |
| --- | --- |
| `npm run typecheck` | Aprobado. |
| `npm run build` | Aprobado con Next.js 16.2.9. |
| Generación de rutas | 38 rutas; sin fallo de compilación ni TypeScript. |

No fue necesario cambiar componentes ni lógica: no se encontró un bug en el
código frontend actual durante el recorrido.

## Pruebas responsive

Se validaron ambos roles y la pantalla de acceso restringido:

| Viewport | `admin_auditor` | `operator` |
| --- | --- | --- |
| `1366x768` | 33 destinos, Reportes visible, acción principal visible, sin scroll horizontal. | 22 destinos, sin Reportes restringido, acción principal visible, mensaje legible y sin scroll horizontal. |
| `1440x900` | 33 destinos, Reportes visible, acción principal visible, sin scroll horizontal. | 22 destinos, sin Reportes restringido, acción principal visible, mensaje legible y sin scroll horizontal. |
| `390x844` | Bottom nav visible con Reportes; sin scroll horizontal. | Bottom nav visible sin Reportes; mensaje restringido visible y sin scroll horizontal. |
| `412x915` | Bottom nav visible con Reportes; sin scroll horizontal. | Bottom nav visible sin Reportes; mensaje restringido visible y sin scroll horizontal. |

## Excel y PDF

Los botones se accionaron desde la pantalla de exportaciones del administrador.
Además, se verificaron la respuesta y el contenido contra el backend actual:

| Formato | Estado | Tipo de contenido | Tamaño |
| --- | ---: | --- | ---: |
| Excel gerencial | `200` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | 14.776 bytes |
| PDF gerencial | `200` | `application/pdf` | 4.479 bytes |

`operator` recibió `403` al solicitar directamente la exportación Excel y no
vio botones de descarga en el frontend.

## Docker, LAN y Tailscale

`prod-local-health.ps1` terminó con:

```text
RESULTADO: OK. Fallos críticos: 0. Advertencias informativas: 0.
```

| Comprobación | Resultado |
| --- | --- |
| Compose config | Aprobado. |
| `db` | Healthy. |
| `api` | Healthy. |
| `web` | Healthy. |
| API localhost | `status=ok`. |
| API LAN | `status=ok`. |
| API Tailscale | `status=ok`. |
| Web LAN | Responde. |
| Web Tailscale | Responde. |
| Alembic | `0026_user_roles`. |
| PostgreSQL 5432 | No publicado por Compose. |
| `.env.production.local` | Ignorado y no versionado. |

## Ejecución productiva 58D-2

George autorizó explícitamente la reconstrucción productiva controlada.

### Backup previo

El script `scripts/prod-local-backup-db.ps1` creó:

- `agua-activa-postgres-20260728-051506.dump`;
- su archivo `.dump.sha256`;
- su manifiesto `.dump.json`.

`pg_restore --list` aprobó la verificación. Ninguno de esos archivos apareció
en `git status`.

### Rebuild y health

`scripts/prod-local-rebuild.ps1` reconstruyó `api` y `web` desde el código
actual. No se ejecutó `docker compose down -v`, no se borraron volúmenes y no se
ejecutaron migraciones manuales.

La nueva imagen API quedó creada el `2026-07-28T10:15:45Z` y la web el
`2026-07-28T10:16:00Z`. El health posterior aprobó inmediatamente:

- `db`, `api` y `web` healthy;
- API por localhost, LAN y Tailscale;
- web por LAN y Tailscale;
- Alembic en `0026_user_roles`;
- PostgreSQL 5432 no publicado;
- cero fallos críticos y cero advertencias informativas.

### Smoke backend sobre producción reconstruida

Se seleccionaron dentro del contenedor un `operator` y un `admin_auditor`
activos existentes y se emitieron JWT efímeros solo en memoria. No se
mostraron tokens, no se cambiaron contraseñas y no se crearon usuarios.

| Prueba | `operator` | `admin_auditor` |
| --- | ---: | ---: |
| Empleados | `403` | `200` |
| Nómina | `403` | `200` |
| Usuarios | `403` | `200` |
| Precios administrativos | `403` | `200` |
| Panel gerencial | `403` | `200` |
| Exportación Excel gerencial | `403` | `200` |
| Exportación PDF gerencial | `403` | `200` |

También aprobaron:

- corrección de cuadre, anulación de venta y anulación de cobro con
  `operator`: `403`;
- resumen operativo, caja, clientes, ventas, cobros, producción diaria,
  ubicaciones, existencias y movimientos de inventario con `operator`: `200`;
- Excel productivo:
  `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`,
  14.712 bytes;
- PDF productivo: `application/pdf`, 4.519 bytes.

Las tres solicitudes POST restringidas usaron IDs inexistentes y se detuvieron
en autorización con `403`; no alteraron datos.

### Artefactos desplegados

- Los hashes de los endpoints de empleados, nómina y fórmulas dentro de la
  imagen API reconstruida coinciden exactamente con los archivos actuales.
- La imagen web reconstruida contiene en los chunks del servidor y del cliente
  el mensaje compilado de acceso restringido de 58C.

### Smoke frontend sobre producción reconstruida

George inició las sesiones reales sin compartir contraseñas. `admin_auditor`
se validó por la dirección LAN y `operator` por el puerto productivo publicado
en el host; ambas direcciones sirven el mismo contenedor `web` reconstruido.

`admin_auditor` aprobó:

- **33 destinos disponibles**;
- gerencia, exportaciones, usuarios, precios, nómina, control laboral y
  fórmulas visibles;
- ausencia de mensajes de restricción;
- descarga desde la interfaz de Excel y PDF gerenciales;
- confirmación en logs de los dos `GET 200`.

`operator` aprobó:

- **22 destinos disponibles**;
- ausencia de enlaces a gerencia, exportaciones, usuarios, precios
  administrativos, nómina, control laboral y fórmulas;
- las siete URLs directas muestran “Acceso restringido”, “No tienes permiso”,
  “Solicita autorización” y “Volver al panel operativo”;
- ninguna URL directa monta contenido administrativo ni muestra mensajes
  técnicos;
- caja, clientes, ventas de contado y crédito, cobros, producción e inventario
  cargan sin restricción;
- no aparecen anulaciones, aplicación de producción a inventario, fórmulas,
  costos ni ajustes;
- inventario ofrece únicamente `Entrada` y `Salida`.

En `1366x768`, `1440x900`, `390x844` y `412x915`, ambos roles conservaron el
conteo esperado y no presentaron desbordamiento horizontal. En móvil, el bottom
nav de administrador muestra Reportes y el del operador no. La pantalla de
acceso restringido también aprobó los cuatro viewports.

No se creó, editó, cerró, corrigió ni anuló ningún registro productivo durante
el recorrido visual. Las dos sesiones se cerraron al terminar.

## Deriva de despliegue detectada en 58D y resuelta en 58D-2

Los healthchecks prueban disponibilidad, pero no que las imágenes correspondan
al código actual.

### API productiva

La imagen `agua-activa-erp-prod-local-api` fue creada el
`2026-07-27T15:39:45Z`. Los hashes de sus endpoints de empleados, nómina y
fórmulas difieren de los archivos actuales.

En una API desechable creada desde esa imagen, sin conectarla a producción:

| Petición de `operator` | Imagen desplegada | Código actual |
| --- | ---: | ---: |
| `GET /employees` | `200` | `403` |
| `GET /payroll/runs` | `200` | `403` |
| `POST /production/recipes` con cuerpo vacío | `422` | `403` |

Esto demuestra que la imagen productiva no incorpora toda la protección de
58B, aunque el código actual y sus pruebas sí la incorporan. 58D-2 reemplazó
esa imagen mediante reconstrucción y el smoke productivo posterior confirmó
los `403` esperados.

### Web productiva

La compilación local actual contiene el mensaje de bloqueo de 58C. La búsqueda
de esa misma cadena en todo `/app/.next` de la imagen web productiva no encontró
coincidencias. Por tanto, la imagen web tampoco puede considerarse validada como
la versión de 58C sin una reconstrucción. 58D-2 reconstruyó la imagen y confirmó
la cadena en los chunks productivos nuevos.

La credencial inicial configurada para automatización ya no coincide con la
cuenta productiva vigente. No se mostró ni se cambió ninguna credencial. George
completó los dos inicios de sesión directamente en el navegador.

## Mejoras independientes del cierre 58D

1. P1-01 sigue abierto para automatización frontend de `401/403` y
   centralización completa de sesión.
2. La advertencia TestClient/httpx puede resolverse en mantenimiento, sin
   mezclarla con el despliegue.

## Seguridad y Git

- No se cambiaron permisos, backend, frontend, endpoints, payloads, cálculos,
  migraciones, seeds, Docker, scripts ni variables.
- Solo se crean o actualizan documentos de 58D.
- No aparecen `.env.production.local`, `backups/`, dumps, tokens ni secretos en
  los cambios.
- No se usó `docker compose down -v`.
- No se hizo `git add`, commit ni push.

## Conclusión

La política de permisos está validada en el **código fuente actual**:
backend bloquea, frontend acompaña, `operator` conserva la operación diaria y
`admin_auditor` conserva el control total.

La deriva de imágenes está resuelta. El backend productivo aplica la política
real, la web productiva contiene y presenta los bloqueos de 58C, `operator`
conserva únicamente su operación aprobada y `admin_auditor` mantiene control
total.

El Bloque 58D queda **aprobado sin reserva por deriva de despliegue**.

## Estado de la recomendación 58D-2

El bloque ejecutó:

1. backup previo verificado;
2. reconstrucción controlada con el script productivo existente;
3. health completo;
4. smoke backend de ambos roles sin crear datos;
5. `403` representativos reales;
6. Excel/PDF de administrador;
7. confirmación LAN/Tailscale;
8. verificación de artefactos e imágenes nuevas;
9. recorrido visual productivo autenticado y responsive de ambos roles.

58D-2 queda completado.
