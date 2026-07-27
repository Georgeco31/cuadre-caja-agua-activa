# 29 - Restauracion controlada de PostgreSQL

## Objetivo

El Bloque 56B demuestra que un backup real de Agua Activa ERP puede restaurarse
y validarse sin tocar la base productiva. La prueba se ejecuta en un contenedor
PostgreSQL temporal, sin red, sin puertos publicados, sin montar
`postgres_prod_data` y sin modificar los contenedores productivos `db`, `api` o
`web`.

Esta prueba reduce el riesgo de conservar backups que parecen validos pero que
no pueden recuperarse. No autoriza restaurar sobre produccion ni iniciar el
piloto.

## Por que no se restaura sobre produccion

Una restauracion reemplaza o crea objetos y datos. Ejecutarla directamente sobre
la base real puede sobrescribir informacion, dejar el esquema a medias o
interrumpir la operacion. Por eso el Bloque 56B usa un destino desechable y
aislado:

- nombre unico `agua-activa-restore-test-YYYYMMDD-HHMMSS`;
- imagen PostgreSQL detectada desde `docker-compose.prod.yml`;
- usuario y base exclusivos de la prueba;
- password temporal generado en memoria y nunca impreso;
- red Docker `none`;
- ningun puerto publicado;
- directorio de datos temporal en memoria, sin volumen Docker;
- eliminacion del contenedor al finalizar correctamente.

El script solo consulta el estado de produccion antes y despues. Nunca ejecuta
`pg_restore` contra el servicio `db` productivo.

## Que se valida

`prod-local-restore-test.ps1` comprueba, en este orden:

1. existencia de `docker-compose.prod.yml` y `.env.production.local`;
2. disponibilidad de Docker y Docker Compose;
3. configuracion Compose valida;
4. `db`, `api` y `web` productivos en estado `running/healthy`;
5. ausencia de publicacion de PostgreSQL 5432;
6. seleccion del `.dump` mas reciente o del indicado con `-BackupPath`;
7. tamano mayor que cero e integridad SHA256 cuando existe el `.sha256`;
8. `pg_restore --list` dentro del contenedor temporal;
9. restauracion real con `--no-owner`, `--no-privileges` y
   `--exit-on-error`;
10. existencia de `alembic_version` y revision exacta `0026_user_roles`;
11. existencia de las tablas principales:
    `users`, `cash_sessions`, `denominations`, `cash_count_items`, `expenses`,
    `correction_logs`, `customers`, `products`, `employees`,
    `delivery_routes`, `vehicles`, `purchases` y `payroll_runs`;
12. conteos numericos de esas tablas, sin mostrar filas ni datos de negocio;
13. salud de produccion y ausencia de publicacion de 5432 despues del restore;
14. eliminacion del contenedor temporal.

`pg_restore --list` por si solo no demuestra recuperacion. El Bloque 56B exige
que el dump se restaure realmente y que el esquema resultante se consulte.

## Ejecutar con el backup mas reciente

Desde la raiz del repositorio:

```powershell
.\scripts\prod-local-restore-test.ps1
```

La forma explicita con `powershell.exe` es:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prod-local-restore-test.ps1
```

## Ejecutar con un backup especifico

```powershell
.\scripts\prod-local-restore-test.ps1 `
  -BackupPath .\backups\postgres\agua-activa-postgres-20260727-133213.dump
```

La ruta puede ser relativa a la raiz del repositorio o absoluta. El archivo debe
existir, tener extension `.dump` y tamano mayor que cero.

## Conservar el contenedor solo si falla

Para depuracion excepcional:

```powershell
.\scripts\prod-local-restore-test.ps1 -KeepContainer
```

`-KeepContainer` solo conserva el contenedor cuando la prueba falla. Una prueba
exitosa siempre lo elimina. El contenedor conservado sigue sin puertos y sin red;
debe eliminarse manualmente despues de la depuracion, verificando primero su
nombre exacto. No usar este parametro en la operacion normal.

## Evidencia segura

Cada ejecucion que alcanza la preparacion de la prueba escribe un JSON en:

```text
backups/restore-tests
```

El nombre sigue el formato:

```text
restore-test-YYYYMMDD-HHMMSS.json
```

La evidencia incluye fecha, PC, nombre/tamano/hash del backup, contenedor
temporal, imagen PostgreSQL, Alembic restaurado, estados de tablas, conteos
numericos, `pg_restore --list`, restore, salud productiva antes/despues y
cleanup.

No incluye passwords, tokens, `AUTH_SECRET_KEY`, `ADMIN_PASSWORD`, contenido de
`.env.production.local`, nombres de personas ni filas de negocio. Toda la carpeta
`backups/` esta ignorada por Git.

Listar evidencias sin modificar nada:

```powershell
.\scripts\prod-local-restore-test-list.ps1
```

El listado muestra solo fecha, archivo JSON, backup probado, estado, Alembic y
cleanup.

## Que significa una restauracion exitosa

La prueba es exitosa unicamente cuando:

- el hash coincide, si el backup dispone de `.sha256`;
- `pg_restore --list` aprueba;
- `pg_restore` termina sin error en el contenedor aislado;
- Alembic queda exactamente en `0026_user_roles`;
- todas las tablas principales existen y sus conteos son numericos;
- produccion sigue healthy y PostgreSQL 5432 sigue sin publicarse;
- el contenedor temporal queda eliminado;
- el JSON seguro registra todos esos estados como `OK`.

## Que hacer si falla

1. Leer el mensaje final y la evidencia JSON, si fue creada.
2. Confirmar que `db`, `api` y `web` productivos siguen healthy con:

   ```powershell
   .\scripts\prod-local-health.ps1
   ```

3. Confirmar que no quedaron contenedores temporales:

   ```powershell
   docker ps -a --filter "name=agua-activa-restore-test"
   ```

4. No reintentar sobre produccion.
5. Repetir con otro backup solo despues de comprobar su origen y SHA256.
6. Usar `-KeepContainer` exclusivamente si una depuracion aislada lo requiere.

## Que no hacer

- No ejecutar `pg_restore` en el contenedor `db` productivo.
- No restaurar sobre la base real.
- No montar ni borrar `postgres_prod_data`.
- No usar `docker compose down -v`.
- No usar `docker volume prune` o `docker system prune`.
- No publicar PostgreSQL 5432.
- No subir dumps, backups o evidencias a GitHub.
- No compartir evidencia que contenga datos sensibles.
- No abrir router, cambiar firewall ni configurar Tailscale para esta prueba.
- No crear migraciones, cambiar seeds o modificar frontend/backend.
- No iniciar el piloto por haber aprobado esta restauracion.

## Evidencia de la prueba en KERNELOS-PC

El 27 de julio de 2026 se probo
`agua-activa-postgres-20260727-133213.dump`:

- SHA256
  `e8a0e748a139e0aeba7bff1cab2da00f570edd290e1ccf71132a554c1d39234f`
  coincidente;
- imagen temporal `postgres:16-alpine`, igual a la productiva;
- contenedor temporal sin red, puertos publicados ni volumen Docker;
- `pg_restore --list` y restauracion real aprobados;
- Alembic restaurado `0026_user_roles`;
- 13 tablas principales presentes y conteos numericos generados;
- `db`, `api` y `web` healthy antes y despues;
- PostgreSQL 5432 sin publicacion antes y despues;
- evidencia final `restore-test-20260727-135341.json` creada e ignorada por Git;
- contenedor temporal eliminado; no quedo ninguno vivo.

No se mostro ningun dato de negocio ni secreto, no se modifico produccion y no se
apagaron sus contenedores.

## Estado y pendientes antes del piloto

- Restauracion demostrada: implementada y comprobada.
- Backup automatico registrado: pendiente; la tarea diaria no fue activada.
- Reserva DHCP: pendiente.
- Rotacion de passwords definitivos: pendiente.
- Copia periodica de backups a disco externo: pendiente.
- Pruebas integrales finales: pendientes.
- Piloto paralelo controlado: pendiente y no autorizado por este bloque.
