# 21 - Plan de correcciones preproducción

## Objetivo

Cerrar de forma verificable los riesgos encontrados en el Bloque 53 sin
mezclar cambios de negocio, infraestructura y recuperación en un solo paso.

## Estado del Bloque 54

El bloqueador base de roles quedó resuelto en código:

- [x] `operator` y `admin_auditor` definidos.
- [x] Usuarios existentes migran a `admin_auditor`.
- [x] Administración de cuentas personales protegida en backend.
- [x] Correcciones, anulaciones, precios, panel y exportaciones críticas
  protegidas con `403`.
- [x] Navegación y botones críticos limitados según rol.
- [x] No se puede desactivar o degradar al último administrador activo.
- [x] Suite backend, typecheck, build y migración local validados.

Esto no cierra los riesgos de servidor, red, backups, restore, auditoría
avanzada ni piloto. La matriz vigente está en
[`22-matriz-permisos-roles.md`](22-matriz-permisos-roles.md).

## Estado del Bloque 55A

El repositorio ya contiene Compose productivo separado, Dockerfiles
productivos, plantilla de variables sin secretos, healthchecks, rotación de
logs y scripts seguros de arranque, health, logs y apagado. PostgreSQL no
publica 5432, la API no usa reload y la Web no usa el servidor de desarrollo.

Por tanto, P0-05 y la preparación de código de P0-06 quedan **preparados, no
cerrados**. Su cierre exige construir y probar en la PC, verificar desde otro
equipo que 5432 no sea accesible y registrar evidencia. Continúan abiertos
P0-07, P0-08, P0-09, todos los controles de red, los backups automáticos y la
restauración demostrada. La guía está en
[`23-docker-produccion-local.md`](23-docker-produccion-local.md).

## Correcciones obligatorias antes de producción

| ID | Bloque sugerido | Corrección | Responsable | Prioridad | Criterio de cierre |
| --- | --- | --- | --- | --- | --- |
| P0-01 | 54 | Roles `operator` y `admin_auditor`, cuentas personales y permisos backend | Desarrollo + George | Crítica | Matriz aprobada; pruebas permiten/deniegan cada grupo; secretaria no usa admin |
| P0-02 | 54 | Auditoría de acciones por usuario para correcciones/anulaciones críticas | Desarrollo | Crítica | Cada acción conserva usuario y motivo; pruebas lo verifican |
| P0-03 | 54 | Migración de roles revisada manualmente | Desarrollo | Crítica | Upgrade/downgrade aislados; diff no elimina índices/constraints históricos |
| P0-04 | 54B | Reconciliar deuda Alembic en bloque dedicado | Desarrollo | Alta | `alembic check` limpio o baseline de excepciones explícito y aprobado |
| P0-05 | 55A/55A-2 | Compose productivo endurecido (preparado en repositorio; pendiente prueba en PC) | Desarrollo/infraestructura | Crítica | Sin reload/dev; restart, healthchecks, logs, usuarios y volumen verificados en PC |
| P0-06 | 55A/55A-2 | Retirar exposición de PostgreSQL (sin `ports` en Compose; pendiente prueba en red) | Infraestructura | Crítica | `5432` no accesible desde otro equipo; API sí conecta internamente |
| P0-07 | 55A | Rotar contraseña PostgreSQL y secretos productivos | George + infraestructura | Crítica | No hay defaults; health/login pasan; secretos no se publican |
| P0-08 | 55B | Resolver URL de API, CORS, IP/DNS y firewall LAN | Infraestructura | Crítica | Login y módulos cargan desde PC cliente; origen no autorizado falla |
| P0-09 | 55A | Definir zona `America/Guayaquil` | Desarrollo/infraestructura | Alta | Host, API y reglas de negocio usan fecha esperada antes/después de 19:00 |
| P0-10 | 55B | Backup automático, retención, checksum, cifrado y copia externa | Infraestructura + George | Crítica | Ejecución diaria comprobada y alerta de fallo |
| P0-11 | 55B | Restauración real en ambiente aislado | Infraestructura + George | Crítica | Restore aprobado; conteos, Alembic, health, login y muestras coinciden |
| P0-12 | 55B | Manual de recuperación y responsables | George + infraestructura | Alta | Documento puede seguirse de principio a fin y registra RPO/RTO |

## Correcciones recomendadas antes del piloto

| ID | Bloque sugerido | Corrección | Responsable | Prioridad | Criterio de cierre |
| --- | --- | --- | --- | --- | --- |
| P1-01 | 54 | Centralizar guardas y sesión frontend | Desarrollo | Alta | Todas las rutas usan un único mecanismo y pruebas cubren 401/403 |
| P1-02 | 54 | Limitar navegación según rol | Desarrollo | Alta | Operator solo ve módulos permitidos; backend sigue siendo autoridad |
| P1-03 | 54/55A | Rate limit y registro de intentos de login | Desarrollo | Alta | Intentos excesivos se limitan sin bloquear operación legítima |
| P1-04 | 55A | Restringir documentación OpenAPI | Desarrollo | Media | `/docs` y `/openapi.json` no quedan públicos en producción |
| P1-05 | 55A | HTTPS local o acceso cifrado equivalente | Infraestructura | Alta | Credenciales/token no viajan en texto claro por red no confiable |
| P1-06 | 55A | Monitor de contenedores, health, disco y backups | Infraestructura | Alta | Fallos generan aviso útil para George |
| P1-07 | 55A | UPS y apagado limpio | George + infraestructura | Alta | Corte controlado no corrompe datos; reinicio queda documentado |
| P1-08 | 55B | Pruebas de integración PostgreSQL | Desarrollo | Alta | Locks, concurrencia, índices parciales y constraints pasan en PostgreSQL |
| P1-09 | 56 | Smoke E2E | Desarrollo | Media | Login, caja, historial, panel y exportaciones pasan en servidor |
| P1-10 | 56 | Capacitación y guía de secretaria | George | Alta | Operador completa flujo diario sin acceso administrativo |

## Mejoras que pueden esperar

| ID | Bloque sugerido | Mejora | Responsable | Criterio de cierre |
| --- | --- | --- | --- | --- |
| P2-01 | Postpiloto | Dividir `apps/web/lib/api.ts` por dominios | Desarrollo | Clientes API pequeños y sin cambio funcional |
| P2-02 | Postpiloto | Dividir páginas de más de 1.000 líneas | Desarrollo | Componentes/hooks extraídos con typecheck/build |
| P2-03 | Postpiloto | Dividir servicios Excel/PDF | Desarrollo | Generadores reutilizables y pruebas equivalentes |
| P2-04 | Postpiloto | Auditoría general de cambios de maestros | Desarrollo + George | Historial consultable por usuario, fecha y entidad |
| P2-05 | Mantenimiento | Resolver warning TestClient/httpx | Desarrollo | Suite sin warning y sin salto de versiones no probado |
| P2-06 | Mantenimiento | Pipeline CI y escaneo de dependencias | Desarrollo | Pruebas y build automáticos por rama/PR |
| P2-07 | Postpiloto | Evaluar cookies seguras y refresh tokens | Desarrollo | Decisión documentada y amenaza XSS/CSRF considerada |
| P2-08 | Postpiloto | Métricas y logs estructurados | Desarrollo/infraestructura | Incidentes trazables sin secretos |

## Secuencia propuesta

```text
Bloque 53 aprobado
  |
  v
Bloque 54: roles, cuentas y permisos
  |
  +--> revisión manual de su migración
  v
Bloque 54B: reconciliación Alembic controlada
  |
  v
Bloque 55A: servidor, red, zona horaria y seguridad Docker
  |
  v
Bloque 55B: backup, retención, copia externa y restore
  |
  v
Bloque 56: piloto controlado
```

## Guardas obligatorias para el Bloque 54

1. Crear backup antes de aplicar la migración en cualquier base relevante.
2. Ejecutar `alembic heads` y `alembic current`.
3. No aceptar automáticamente la salida de autogenerate.
4. Revisar que el archivo solo incluya tablas/columnas/constraints de usuarios,
   roles o permisos aprobados.
5. Rechazar cualquier `drop_index`, `drop_constraint` o modificación de
   ventas/rutas/gastos/nómina no relacionada.
6. Probar upgrade y downgrade en base desechable.
7. Probar roles contra PostgreSQL.
8. Volver a ejecutar las 917 pruebas, typecheck y build.

## Matriz mínima de permisos por decidir

La tabla quedó implementada como matriz base. El detalle operativo está en el
documento 22:

| Capacidad | Operator | Admin-auditor |
| --- | --- | --- |
| Login y dashboard operativo | Sí | Sí |
| Caja abierta: conteo/gastos/cierre | Sí | Sí |
| Historial de caja | Lectura | Lectura |
| Correcciones de cuadre cerrado | No | Sí |
| Catálogos operativos | Según módulo | Sí |
| Ventas/cobros/rutas | Sí | Sí |
| Inventario/producción | Operación normal | Sí |
| Anulaciones sensibles | No | Sí |
| Gastos/compras/nómina | Según puesto | Sí |
| Panel gerencial | No | Sí |
| Excel/PDF gerencial | No | Sí |
| Usuarios, roles y configuración | No | Sí |

## Criterio final de preproducción

La preproducción queda cerrada cuando:

- no quedan hallazgos críticos abiertos;
- los permisos se prueban en backend;
- PostgreSQL no es accesible desde la red;
- la aplicación funciona desde un PC cliente autorizado;
- fecha/hora reflejan Ecuador;
- backup automático y restore aislado están aprobados;
- pruebas y build pasan desde el commit etiquetado;
- el checklist 20 está completo y firmado por George.
