# 14 - Checklist de uso real de Agua Activa ERP

Este checklist organiza la operación real sin asumir automatizaciones que el
sistema todavía no tiene. Durante el piloto debe usarse junto con el control
manual vigente.

## Reglas antes de marcar un punto

- Marcar una tarea solo después de revisar el resultado guardado.
- Usar fechas reales de la operación; no crear movimientos para “probar” en la
  misma base operativa.
- Si hay una diferencia no explicada, no cerrar ni anular por impulso.
- Una venta no descuenta inventario automáticamente.
- Una producción no aumenta stock hasta aplicarla a inventario.
- Un cierre o recibo de ruta no modifica el conteo de caja.
- Los gastos del cuadre no sustituyen el futuro módulo de gastos operativos
  generales.

## Inicio del día

- [ ] Encender Docker Desktop.
- [ ] Entrar en la raíz del proyecto.
- [ ] Confirmar que se está usando la carpeta y la base correctas.
- [ ] Iniciar sin borrar volúmenes:

  ```bash
  ./scripts/local-start.sh
  ```

- [ ] Verificar backend y frontend:

  ```bash
  ./scripts/check-health.sh
  ```

- [ ] Confirmar manualmente que responde:

  ```text
  http://localhost:8010/api/v1/health
  http://localhost:3000/login
  ```

- [ ] Iniciar sesión y confirmar que abre `/dashboard`.
- [ ] Revisar que la fecha del equipo sea correcta.
- [ ] Confirmar que existe un backup reciente.
- [ ] Si empieza un hito importante, una carga inicial o un cambio masivo de
  catálogos, crear backup previo:

  ```bash
  ./scripts/backup-db.sh
  ```

## Operación diaria

### 1. Preparar caja y datos maestros

- [ ] Crear o consultar el cuadre del día en `Cuadre diario`.
- [ ] Confirmar que no se creó un cuadre duplicado.
- [ ] Revisar que clientes, productos, rutas, vehículos y ubicaciones que se
  usarán estén activos y correctos.
- [ ] No cambiar datos maestros en medio de una operación vinculada sin
  registrar la razón en la bitácora del piloto.

### 2. Registrar producción

- [ ] Abrir `Producción`.
- [ ] Registrar cantidades producidas y merma con sus unidades correctas.
- [ ] Revisar productos, cantidades y fecha antes de guardar.
- [ ] Aplicar la producción a la ubicación de inventario correcta.
- [ ] Confirmar en `Inventario` que el stock aumentó por la cantidad neta.
- [ ] No volver a aplicar un lote que ya tenga aplicación activa.

### 3. Preparar y cargar ruta

- [ ] Confirmar stock disponible en la ubicación origen.
- [ ] Abrir `Carga de camión`.
- [ ] Elegir ruta, vehículo, origen y ubicación de vehículo correctos.
- [ ] Registrar los productos y cantidades efectivamente cargados.
- [ ] Confirmar que la salida del origen y la entrada al vehículo aparecen en
  inventario.

### 4. Registrar actividad comercial

- [ ] Registrar ventas de contado.
- [ ] Registrar ventas a crédito solo para clientes habilitados.
- [ ] Asociar la venta a la carga correcta cuando corresponda.
- [ ] Registrar cobros o abonos con método, fecha y carga correctos.
- [ ] Confirmar que ningún abono supera el saldo.
- [ ] Revisar la actividad comercial de la carga.
- [ ] Recordar que las ventas registradas no descuentan inventario de forma
  automática.

### 5. Registrar retorno y cierre de ruta

- [ ] Contar físicamente lo que regresa en el vehículo.
- [ ] Registrar el retorno hacia una ubicación no vehicular.
- [ ] Confirmar que las cantidades no superan lo cargado ni el stock del
  vehículo.
- [ ] Revisar inventario después del retorno.
- [ ] Abrir `Actividad de ruta` y comparar ventas de contado, crédito y cobros.
- [ ] Contar el efectivo entregado.
- [ ] Crear el cierre financiero de ruta.
- [ ] Revisar efectivo esperado, entregado y diferencia.
- [ ] Investigar y anotar toda diferencia antes de continuar.

### 6. Registrar dinero de ruta en caja

- [ ] Confirmar que el cuadre del día está abierto.
- [ ] Registrar el efectivo recibido desde el cierre de ruta.
- [ ] Confirmar cierre, cuadre, fecha y monto.
- [ ] Recordar que este registro es trazabilidad y no cambia denominaciones,
  gastos ni total contado.

### 7. Registrar caja y gastos

- [ ] Registrar conteos de monedas y billetes.
- [ ] Registrar gastos de caja con el momento correcto:
  `before_count` o `after_count`.
- [ ] Confirmar que los gastos anteriores al conteo se informan, pero no se
  restan.
- [ ] Confirmar que los gastos posteriores al conteo sí se restan.
- [ ] Mantener por separado los gastos generales que aún no pertenecen a este
  módulo.

### 8. Revisar resumen diario

- [ ] Abrir `Resumen diario`.
- [ ] Revisar caja, producción, merma, ventas, cobros, cargas, retornos,
  cierres y dinero de ruta.
- [ ] Leer todas las alertas.
- [ ] Comparar contra documentos y controles manuales.

## Cierre del día

- [ ] Confirmar que todas las rutas del día tienen estado y explicación.
- [ ] Abrir `Rutas vs caja`.
- [ ] Revisar cierres activos frente al total contado.
- [ ] Abrir `Resumen diario` y revisar nuevamente alertas y totales.
- [ ] Revisar diferencias de caja, ruta, cobros e inventario.
- [ ] Registrar en la bitácora las diferencias explicadas y las pendientes.
- [ ] Confirmar que no falta aplicar producción.
- [ ] Confirmar que no falta registrar retorno de rutas completadas.
- [ ] Confirmar que no falta registrar dinero de cierres recibido en caja.
- [ ] Cerrar el cuadre solo cuando los conteos y gastos estén revisados.
- [ ] Si se requiere una corrección posterior, usar el flujo de correcciones
  con motivo; no cambiar la base directamente.
- [ ] Crear backup de cierre:

  ```bash
  ./scripts/backup-db.sh
  ```

- [ ] Confirmar que el archivo nuevo existe en `backups/` y tiene tamaño mayor
  que cero.
- [ ] Apagar conservando los datos:

  ```bash
  ./scripts/local-stop.sh
  ```

- [ ] No usar `docker compose down -v`.

## Checklist semanal

- [ ] Revisar que haya un backup por cada día operativo.
- [ ] Copiar backups a un segundo medio seguro y con acceso restringido.
- [ ] Confirmar que no se guardaron backups, `.env` o capturas sensibles en
  Git.
- [ ] Revisar clientes, productos, rutas, vehículos, empleados y ubicaciones
  inactivos o duplicados.
- [ ] Revisar ventas a crédito vencidas y saldos pendientes.
- [ ] Comparar una muestra de inventario físico contra el sistema.
- [ ] Revisar lotes sin aplicación, cargas sin retorno, cierres pendientes y
  dinero de ruta no registrado en caja.
- [ ] Revisar anulaciones y correcciones de la semana con sus motivos.
- [ ] Revisar el resumen mensual acumulado hasta la fecha.
- [ ] Consolidar incidencias y priorizar las que afectan dinero o inventario.
- [ ] Probar restauración únicamente en un entorno aislado y nunca encima de
  la base operativa sin un backup previo.

## Checklist mensual

- [ ] Ejecutar el reporte mensual del período cerrado.
- [ ] Conciliar totales mensuales contra controles externos.
- [ ] Revisar cartera por cliente y vencimientos.
- [ ] Realizar o programar conteo físico completo de inventario.
- [ ] Revisar diferencias recurrentes por ruta.
- [ ] Revisar merma y producción por producto.
- [ ] Confirmar que los gastos generales fuera de caja siguen controlados por
  un medio externo hasta implementar su módulo.
- [ ] Revisar usuarios, acceso al equipo y vigencia de credenciales.
- [ ] Seleccionar un backup mensual, copiarlo a almacenamiento seguro y
  documentar su fecha.
- [ ] Probar la restauración mensual en un entorno aislado.
- [ ] Revisar espacio disponible del equipo y del medio de backup.
- [ ] Revisar el roadmap y decidir qué bloque es seguro iniciar.

## Si ocurre un error

- [ ] Detener solo el flujo afectado; no borrar registros.
- [ ] Anotar fecha, hora, módulo, pantalla, acción e identificadores visibles.
- [ ] Tomar captura sin mostrar contraseñas, tokens ni datos innecesarios.
- [ ] Ejecutar `./scripts/check-health.sh`.
- [ ] Hacer backup del estado actual si la base sigue accesible.
- [ ] Comparar con el registro manual.
- [ ] No ejecutar SQL de corrección ni restaurar hasta entender el alcance.
- [ ] Si se restaura, crear antes un backup del estado actual y hacerlo con el
  responsable designado.

## Checklist técnico antes de una nueva versión

- [ ] `git status --short`
- [ ] Backend: `.venv/bin/python -m pytest`
- [ ] Frontend: `npm run typecheck`
- [ ] Frontend: `npm run build`
- [ ] Raíz: `docker compose config`
- [ ] Alembic: confirmar la revisión esperada.
- [ ] `git diff --check`
- [ ] Revisar que no existan migraciones o seeds inesperados.

