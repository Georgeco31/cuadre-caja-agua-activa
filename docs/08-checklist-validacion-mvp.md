# 08 - Checklist de validacion MVP

> **Documento histórico del MVP inicial.** Las exclusiones al final ya no
> describen el ERP actual. Para el corte vigente usar
> `docs/13-auditoria-general-erp.md` y
> `docs/14-checklist-uso-real-agua-activa.md`.

Checklist tecnico funcional para validar el MVP antes y durante la prueba piloto.

## Autenticacion

- [ ] Login valido permite entrar al dashboard.
- [ ] Login invalido muestra error.
- [ ] Logout elimina la sesion local y vuelve a `/login`.
- [ ] `/dashboard` redirige a `/login` si no hay token.
- [ ] Rutas protegidas no muestran datos sin token.

## Dashboard

- [ ] Dashboard muestra usuario autenticado.
- [ ] Dashboard muestra estado del cuadre de hoy.
- [ ] Dashboard muestra acciones rapidas.
- [ ] Dashboard muestra ultimos cuadres o estado vacio claro.
- [ ] Dashboard muestra recordatorio de backup.

## Cuadre diario

- [ ] Crear cuadre del dia.
- [ ] Evitar duplicado por fecha.
- [ ] Abrir cuadre existente del dia.
- [ ] Registrar monedas.
- [ ] Registrar billetes.
- [ ] Precargar conteos al recargar la pantalla.
- [ ] Registrar gastos antes del conteo.
- [ ] Registrar gastos despues del conteo.
- [ ] Ver resumen oficial.
- [ ] Confirmar que gastos antes del conteo no se restan del total contado.
- [ ] Confirmar que gastos despues del conteo si se restan del total contado.
- [ ] Cerrar cuadre.
- [ ] Bloquear edicion normal cuando el cuadre esta `closed`.

## Historial

- [ ] Ver historial.
- [ ] Filtrar por fecha desde.
- [ ] Filtrar por fecha hasta.
- [ ] Filtrar por estado `open`.
- [ ] Filtrar por estado `closed`.
- [ ] Limpiar filtros.
- [ ] Ver detalle desde el historial.
- [ ] Mostrar mensaje claro si no hay resultados.

## Detalle de cuadre

- [ ] Ver resumen.
- [ ] Ver conteos.
- [ ] Ver gastos antes del conteo.
- [ ] Ver gastos despues del conteo.
- [ ] Ver estado y fecha de cierre.
- [ ] Volver al historial.

## Correcciones

- [ ] Corregir conteo cerrado con motivo.
- [ ] Agregar gasto correctivo con motivo.
- [ ] Ver `correction_logs`.
- [ ] Ver resumen actualizado despues de la correccion.
- [ ] Confirmar que las correcciones normales no aparecen para cuadres abiertos.

## Reportes

- [ ] Ver resumen acumulado.
- [ ] Filtrar por fecha desde.
- [ ] Filtrar por fecha hasta.
- [ ] Filtrar por estado.
- [ ] Ver gastos antes y despues del conteo en el acumulado.
- [ ] Confirmar nota de que no son ventas reales.
- [ ] Confirmar estado vacio si no hay resultados.

## Operacion local

- [ ] `docker compose config` pasa.
- [ ] `./scripts/local-start.sh` levanta `db`, `api` y `web`.
- [ ] `./scripts/local-migrate.sh` aplica migraciones.
- [ ] `./scripts/local-seed.sh` carga denominaciones y admin.
- [ ] `./scripts/check-health.sh` revisa backend y frontend sin modificar datos.
- [ ] `./scripts/backup-db.sh` genera archivo en `backups/`.
- [ ] `./scripts/restore-db.sh backups/nombre_backup.sql` esta documentado.
- [ ] `./scripts/local-stop.sh` apaga sin borrar datos.
- [ ] No se usa `docker compose down -v` con datos reales.

## Validacion tecnica

- [ ] Backend:

  ```bash
  cd apps/api
  pytest
  ```

- [ ] Frontend typecheck:

  ```bash
  cd apps/web
  npm run typecheck
  ```

- [ ] Frontend build:

  ```bash
  cd apps/web
  npm run build
  ```

- [ ] Docker Compose:

  ```bash
  docker compose config
  ```

## Exclusiones confirmadas

- [ ] No hay ventas reales.
- [ ] No hay facturacion.
- [ ] No hay inventario.
- [ ] No hay clientes.
- [ ] No hay rutas.
- [ ] No hay WhatsApp.
- [ ] No hay multiempresa.
- [ ] No hay exportacion PDF/Excel.
