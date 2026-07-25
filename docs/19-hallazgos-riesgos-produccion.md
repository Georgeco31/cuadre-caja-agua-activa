# 19 - Hallazgos y riesgos de producción

## Criterio

- **Crítico:** puede exponer credenciales, causar pérdida de datos, impedir la
  operación o romper integridad financiera.
- **Importante:** puede causar errores manuales, resultados confusos o
  despliegues frágiles.
- **Menor:** deuda de mantenimiento, documentación u optimización.

Los riesgos críticos descritos son bloqueadores de producción/piloto, no del
avance al Bloque 54.

## Hallazgos críticos

| ID | Hallazgo | Evidencia | Impacto | Acción obligatoria |
| --- | --- | --- | --- | --- |
| C-01 | PostgreSQL conserva contraseña de desarrollo y publica `5432` en todas las interfaces | `.env` coincide con el default para PostgreSQL; contenedor publica `0.0.0.0:5432` y `:::5432` | Acceso o pérdida de datos desde la red local | Rotar contraseña, mantener `DATABASE_URL` coherente y retirar el puerto remoto o enlazar solo a loopback |
| C-02 | No existen roles ni cuentas personales | `users` no tiene rol; solo hay un admin; 197 operaciones protegidas aceptan al mismo usuario | Secretaria con acceso total, cuenta compartida y trazabilidad insuficiente | Implementar `operator` y `admin-auditor` en Bloque 54, denegación backend por defecto y cuentas separadas |
| C-03 | Recuperación insuficiente | Los dos dumps existentes son de revisiones `0001` y `0002`, no de `0025_materials`; además no hay automatización, retención, copia externa ni restore actual probado | Pérdida prolongada o irreversible ante daño del PC/volumen | Crear backup actual, automatizarlo, aplicar retención/copia cifrada externa/checksum y demostrar restauración aislada |
| C-04 | Configuración actual no funciona para clientes LAN | `NEXT_PUBLIC_API_URL` y CORS usan localhost | Cada PC cliente intentaría llamar su propia API o sería rechazado por CORS | Definir hostname/IP del servidor o proxy mismo origen; configurar CORS exacto y probar desde otro equipo |

## Hallazgos importantes

| ID | Hallazgo | Riesgo | Recomendación |
| --- | --- | --- | --- |
| I-01 | `alembic check` falla por divergencias históricas | Una migración autogenerada puede proponer eliminar constraints o índices relevantes | Revisar manualmente la migración de roles; reconciliar metadata/esquema en bloque dedicado, con backup |
| I-02 | API y DB operan en UTC, negocio en Ecuador | Defaults de `date.today()` pueden pasar al día siguiente desde las 19:00 locales | Definir `America/Guayaquil` y probar límites diarios/mensuales |
| I-03 | JWT se guarda en `localStorage` y el tráfico es HTTP | XSS o una red no confiable puede exponer credenciales/token | CSP, actualizaciones, firewall, HTTPS o Tailscale; evaluar cookie segura en fase posterior |
| I-04 | Login sin rate limit, lockout ni auditoría de intentos | Intentos repetidos de contraseña dentro de la red | Rate limit local, logs y alerta; contraseña robusta |
| I-05 | Compose carece de endurecimiento productivo | Reinicio manual, logs sin rotación, servicios root y falta de healthchecks API/web | Compose productivo con `restart`, healthchecks, usuarios no root, límites y logging |
| I-06 | Pruebas de persistencia usan principalmente SQLite | No validan totalmente locks, índices parciales ni comportamiento PostgreSQL | Añadir pruebas de integración PostgreSQL para reglas financieras críticas |
| I-07 | Protección frontend repetida en 35 páginas | Una pantalla futura puede omitir guardas o manejar distinto `401/403` | Centralizar sesión/guardas después de definir roles |
| I-08 | Archivos frontend/backend excesivamente grandes | Cambios pequeños tienen mayor superficie de regresión | Refactor gradual por dominio después de estabilización |
| I-09 | No hay monitoreo ni recuperación automática | Un fallo puede detectarse tarde | Health periódico, espacio en disco, estado de contenedores y alertas de backup |
| I-10 | Restore opera sobre la base seleccionada | Error humano puede reemplazar datos vigentes | Restore aislado por defecto, confirmación de destino y backup previo |
| I-11 | No hay evidencia E2E automatizada | Navegación crítica depende de revisión manual | Añadir smoke E2E de login, dashboard, caja y exportaciones |
| I-12 | Documentación OpenAPI queda disponible | Expone inventario técnico de rutas a cualquier usuario de la red | Deshabilitar o restringir `/docs` y `/openapi.json` en producción |

## Hallazgos menores

| ID | Hallazgo | Recomendación |
| --- | --- | --- |
| M-01 | No existen tags Git | Etiquetar cortes auditados y pre-piloto |
| M-02 | Warning deprecado de Starlette TestClient/httpx | Resolver en mantenimiento de dependencias, sin actualizar a ciegas |
| M-03 | README aún contenía referencias históricas a PDF pendiente | Mantener estado y documentos vigentes sincronizados |
| M-04 | Documentos 00–08 son históricos | Conservarlos, pero enlazar siempre auditoría/checklist actuales |
| M-05 | No se encontró pipeline CI versionado | Ejecutar pruebas localmente de forma obligatoria; añadir CI cuando convenga |
| M-06 | `.env` no debe tratarse como script shell | Dejar claro que Docker Compose lo carga; no ejecutar `source .env` |

## Detalle de la deuda Alembic

La base y el código coinciden en la revisión `0025_materials`, pero no en la
representación completa del esquema.

### Unicidad representada de forma distinta

Trece campos tienen en PostgreSQL constraint único más índice no único, y en
metadata aparecen como índice único:

- `employee_advances.advance_number`
- `employee_loan_payments.payment_number`
- `employee_loans.loan_number`
- `operating_expense_categories.name`
- `operating_expenses.expense_number`
- `payroll_runs.payroll_number`
- `production_recipes.recipe_number`
- `purchases.purchase_number`
- `route_cash_receipts.receipt_number`
- `route_closures.closure_number`
- `route_loads.load_number`
- `route_returns.return_number`
- `suppliers.identification`

La unicidad sí está protegida actualmente. El problema es el ruido y el riesgo
de una migración futura.

### Índices presentes solo en la base/migraciones

- `uq_route_returns_active_route_load`, parcial y funcionalmente importante.
- `ix_sale_items_product_id`
- `ix_sale_items_sale_id`
- `ix_sales_customer_credit_balance`
- `ix_sales_customer_id`
- `ix_sales_sale_date`
- `ix_sales_status`

No eliminar ni recrear estos objetos sin análisis de consultas, concurrencia y
datos.

## Riesgos aceptados temporalmente

Se aceptan solo para desarrollo actual, en un PC controlado y sin abrir la red:

- Un único admin mientras se implementa el Bloque 54.
- Separaciones manuales entre ventas/caja/inventario/compras/producción.
- Backups manuales mientras no sea el sistema oficial.
- HTTP localhost durante desarrollo.
- Divergencia Alembic mientras no se autogenere ni aplique un diff ciego.
- Archivos grandes y guardas frontend repetidos.

Estos riesgos dejan de estar aceptados al iniciar piloto con datos reales.

## Deuda técnica

1. Reconciliar metadata, migraciones y PostgreSQL.
2. Pruebas de integración PostgreSQL y smoke E2E.
3. Centralizar autenticación/autorización frontend.
4. Dividir `api.ts`, páginas extensas y servicios de exportación.
5. Logging estructurado y auditoría general de cambios de maestros.
6. Estrategia de sesión más resistente a XSS.
7. CI, escaneo de dependencias y actualización controlada.
8. Procedimiento de actualización y rollback del servidor.

## Prioridad recomendada

### P0 - Antes de servidor/piloto

- C-01 a C-04.
- Zona horaria.
- Restore aislado aprobado.
- Migración de roles revisada sin operaciones Alembic históricas.
- Firewall: PostgreSQL nunca accesible desde otros dispositivos.

### P1 - Antes de ampliar usuarios

- Rate limit de login.
- Pruebas PostgreSQL.
- Healthchecks/restart/log rotation.
- HTTPS o acceso exclusivamente cifrado y restringido.
- Monitoreo de backup y disco.

### P2 - Después del piloto inicial

- Refactor de archivos grandes.
- E2E completo.
- CI y observabilidad avanzada.
- Auditoría transversal de maestros.

## Decisión

**Continuar con reservas al Bloque 54.**

No mover el sistema al servidor ni iniciar piloto hasta que los cuatro
hallazgos críticos estén cerrados y exista evidencia de restauración.
