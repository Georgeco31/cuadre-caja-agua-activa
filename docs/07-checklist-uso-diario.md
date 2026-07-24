# 07 - Checklist de uso diario

> **Documento histórico del MVP de caja.** El checklist vigente para el ERP
> completo está en `docs/14-checklist-uso-real-agua-activa.md`.

Checklist simple para operar el MVP local durante la prueba piloto.

## Inicio del dia o prueba

- [ ] Encender Docker Desktop.
- [ ] Entrar a la carpeta del proyecto.
- [ ] Verificar que `.env` exista y tenga valores locales correctos.
- [ ] Levantar el sistema:

  ```bash
  ./scripts/local-start.sh
  ```

- [ ] Verificar salud local:

  ```bash
  ./scripts/check-health.sh
  ```

- [ ] Abrir el frontend:

  ```text
  http://localhost:3000/login
  ```

- [ ] Iniciar sesion con el usuario administrador local.

## Durante el cuadre

- [ ] Abrir `Cuadre diario`.
- [ ] Crear o abrir el cuadre del dia.
- [ ] Registrar monedas.
- [ ] Registrar billetes.
- [ ] Registrar gastos antes del conteo, si aplican.
- [ ] Registrar gastos despues del conteo, si aplican.
- [ ] Confirmar que el resumen muestra total contado, gastos antes del conteo, gastos despues del conteo y total final.
- [ ] Confirmar que el total final resta solo los gastos despues del conteo.
- [ ] Comparar el total del sistema con el cuadre manual.
- [ ] Anotar cualquier diferencia.

## Cierre

- [ ] Revisar total final.
- [ ] Revisar gastos antes del conteo y despues del conteo.
- [ ] Cerrar el cuadre cuando este validado.
- [ ] Verificar que el cuadre aparece en historial.
- [ ] Abrir el detalle del historial y revisar resumen, conteos y gastos separados por momento.
- [ ] Hacer backup:

  ```bash
  ./scripts/backup-db.sh
  ```

- [ ] Apagar el sistema sin borrar datos:

  ```bash
  ./scripts/local-stop.sh
  ```

## Si se necesita corregir un cuadre cerrado

- [ ] Abrir el detalle desde historial.
- [ ] Registrar la correccion con motivo claro.
- [ ] Confirmar que el resumen se actualiza.
- [ ] Confirmar que aparece el log de correccion.
- [ ] Anotar la correccion tambien en el control manual de prueba.

## Advertencias

- No usar `docker compose down -v` con datos reales.
- No borrar volumenes de Docker durante la prueba.
- No subir `.env` a GitHub.
- No subir `backups/` a GitHub.
- No compartir la contrasena admin.
- No compartir backups con datos reales por canales inseguros.
- No abandonar el cuadre manual hasta cerrar la prueba piloto.
