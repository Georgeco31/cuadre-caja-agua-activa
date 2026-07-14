# 06 - Prueba piloto local

Esta guia prepara una prueba piloto local del MVP de Cuadre de Caja Agua Activa.
La prueba debe servir para comparar el sistema contra el cuadre manual actual sin
reemplazarlo todavia.

## Objetivo

Validar que el sistema permite registrar el cuadre diario, gastos antes y
despues del conteo, cierre, historial, correcciones, reportes basicos, backup y
restauracion en un flujo real de trabajo local.

## Duracion recomendada

- 7 a 15 dias.
- Usar dias con movimiento normal del negocio.
- Registrar observaciones todos los dias, aunque no haya errores.

## Reglas de prueba

- Usar el sistema en paralelo con el cuadre manual actual.
- No abandonar todavia el metodo manual.
- Comparar resultados al final de cada dia.
- No usar datos reales sin haber probado backup y restauracion.
- No borrar volumenes de Docker durante la prueba.
- No usar `docker compose down -v` con datos reales.
- No subir `.env` ni backups a GitHub.

## Preparacion

Desde la raiz del proyecto:

1. Verificar que Docker Desktop este abierto.
2. Crear `.env` si no existe:

   ```bash
   cp .env.example .env
   ```

3. Revisar `.env` y cambiar al menos:

   - `POSTGRES_PASSWORD`
   - `DATABASE_URL`
   - `ADMIN_PASSWORD`
   - `AUTH_SECRET_KEY`

4. Levantar el sistema:

   ```bash
   ./scripts/local-start.sh
   ```

5. Ejecutar migraciones:

   ```bash
   ./scripts/local-migrate.sh
   ```

6. Ejecutar seeds:

   ```bash
   ./scripts/local-seed.sh
   ```

7. Revisar salud local:

   ```bash
   ./scripts/check-health.sh
   ```

8. Abrir:

   ```text
   http://localhost:3000/login
   ```

9. Probar login con `ADMIN_USERNAME` y `ADMIN_PASSWORD`.

## Flujo diario

1. Iniciar sesion.
2. Crear o abrir el cuadre del dia.
3. Registrar monedas.
4. Registrar billetes.
5. Registrar gastos antes del conteo si ya salieron de caja antes de contar.
6. Registrar gastos despues del conteo si se pagaron luego del conteo.
7. Revisar el resumen oficial del backend.
8. Confirmar que solo los gastos despues del conteo se restan del total contado.
9. Comparar contra el cuadre manual.
10. Cerrar el cuadre cuando el total este revisado.
11. Revisar el historial.
12. Revisar el detalle del cuadre.
13. Hacer backup.
14. Apagar el sistema sin borrar datos.

## Backup antes y despues de la prueba

Antes de iniciar la prueba del dia:

```bash
./scripts/backup-db.sh
```

Despues de cerrar el cuadre del dia:

```bash
./scripts/backup-db.sh
```

Los backups se guardan en `backups/`. Esa carpeta esta ignorada por Git.

## Apagar sin borrar datos

Usar:

```bash
./scripts/local-stop.sh
```

Este comando apaga los contenedores y conserva el volumen `postgres_data`.

No usar:

```bash
docker compose down -v
```

Ese comando borra volumenes y puede eliminar la base de datos local.

## Restaurar backup en caso de error

1. No seguir registrando datos hasta entender el problema.
2. Hacer un backup del estado actual, aunque parezca incorrecto:

   ```bash
   ./scripts/backup-db.sh
   ```

3. Elegir el backup a restaurar desde `backups/`.
4. Restaurar:

   ```bash
   ./scripts/restore-db.sh backups/nombre_backup.sql
   ```

5. Abrir la app y verificar historial, detalle y reportes.

Restaurar un backup puede reemplazar datos actuales. Confirmar el archivo antes
de ejecutar el comando.

## Limpieza manual y segura de datos de prueba

La limpieza solo debe hacerse si todos los datos son de prueba. Antes de limpiar:

1. Hacer backup:

   ```bash
   ./scripts/backup-db.sh
   ```

2. Confirmar que no hay datos reales que deban conservarse.
3. Mantener `denominations` y `users`; limpiar solo datos operativos de prueba.

Opcion manual con SQL desde la raiz del proyecto:

```bash
docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" "$POSTGRES_DB"'
```

Luego ejecutar en `psql`:

```sql
BEGIN;
TRUNCATE TABLE correction_logs, expenses, cash_count_items, cash_sessions RESTART IDENTITY;
COMMIT;
```

Despues de limpiar, abrir la app y confirmar que el historial quedo vacio.

No usar `docker compose down -v` como limpieza diaria. Solo considerar borrar el
volumen manualmente en un entorno 100% de prueba y despues de tener backup.

## Que hacer si hay error

- Anotar fecha, hora, usuario, pantalla y accion realizada.
- Tomar captura si el navegador muestra un error.
- No borrar la base de datos.
- Hacer backup del estado actual.
- Revisar `./scripts/check-health.sh`.
- Comparar con el cuadre manual.
- Si el error bloquea el uso, restaurar el ultimo backup valido.

## Datos a anotar durante la prueba

Usar una tabla externa o cuaderno con:

- Fecha.
- Total manual.
- Total del sistema.
- Diferencia.
- Gastos antes del conteo registrados.
- Gastos despues del conteo registrados.
- Estado del cuadre: abierto o cerrado.
- Si hubo correccion, motivo.
- Observacion.

## Criterios de exito

La prueba piloto se considera exitosa si:

- El sistema se puede usar durante 7 a 15 dias sin perdida de datos.
- Cada dia se puede crear o abrir el cuadre correspondiente.
- Los conteos se guardan y se precargan al recargar la pantalla.
- Los gastos antes y despues del conteo aparecen separados en el resumen.
- El total final resta solo los gastos despues del conteo.
- El cierre bloquea la edicion normal.
- Las correcciones de cuadres cerrados quedan registradas con motivo.
- El historial y el detalle permiten revisar dias anteriores.
- Los reportes acumulados ayudan a revisar totales, sin confundirse con ventas reales.
- El backup se ejecuta correctamente al cierre.
- La restauracion fue probada al menos una vez con datos de prueba.
