# 05 - Backup y restauracion

Los backups locales de PostgreSQL se guardan en `backups/`. Esta carpeta esta ignorada por Git.

Antes de usar datos reales, probar el flujo completo de backup y restauracion con datos de prueba.

## Crear backup

Desde la raiz del proyecto:

```bash
./scripts/backup-db.sh
```

El script:

- Crea `backups/` si no existe.
- Levanta `db` si hace falta.
- Ejecuta `pg_dump` dentro del contenedor de PostgreSQL.
- Genera un archivo con formato `backups/cuadre_caja_YYYYMMDD_HHMMSS.sql`.

## Restaurar backup

Desde la raiz del proyecto:

```bash
./scripts/restore-db.sh backups/nombre_backup.sql
```

El script requiere la ruta del archivo como argumento y restaura usando `psql` dentro del contenedor `db`.

## Precauciones

- Restaurar un backup puede reemplazar datos actuales.
- Hacer backup antes de restaurar.
- Confirmar que el archivo de backup pertenece a este proyecto.
- No subir backups a Git.
- No compartir backups con datos reales por canales inseguros.

## Flujo recomendado de prueba

1. Levantar el sistema con `./scripts/local-start.sh`.
2. Ejecutar `./scripts/local-migrate.sh`.
3. Ejecutar `./scripts/local-seed.sh`.
4. Crear datos de prueba desde la app.
5. Ejecutar `./scripts/backup-db.sh`.
6. Confirmar que existe el archivo en `backups/`.
7. Restaurar en un entorno local de prueba con `./scripts/restore-db.sh backups/nombre_backup.sql`.
8. Abrir la app y verificar que los datos restaurados aparecen correctamente.
