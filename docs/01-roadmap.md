# 01 - Roadmap

Este roadmap divide el proyecto en bloques pequeños para evitar avanzar antes de tener claridad.

## Bloque 0 - Base documental y estructura inicial

Objetivo:

- Crear la estructura inicial del repositorio.
- Documentar el alcance del MVP.
- Documentar reglas de negocio.
- Documentar modelo de datos inicial.
- Dejar archivos seguros de configuracion base.

Entregables:

- `README.md`
- `docs/00-definicion-base.md`
- `docs/01-roadmap.md`
- `docs/02-modelo-datos.md`
- `docs/03-reglas-negocio.md`
- `.gitignore`
- `.env.example`
- `docker-compose.yml` placeholder
- `apps/api/.gitkeep`
- `apps/web/.gitkeep`

Estado:

- En preparacion.

## Bloque 1 - Base tecnica del backend

Objetivo:

- Crear la estructura minima de FastAPI.
- Preparar configuracion de entorno.
- Definir dependencias iniciales.
- Agregar una ruta simple de salud si corresponde.

No incluir todavia:

- Autenticacion.
- Modelos completos.
- Migraciones reales.
- Logica de cuadre.

## Bloque 2 - Base tecnica del frontend

Objetivo:

- Crear la estructura minima de Next.js con TypeScript y Tailwind CSS.
- Preparar layout inicial responsive.
- Dejar una pantalla base sin funcionalidad completa.

No incluir todavia:

- Formularios completos.
- Conexion real a API.
- Historial.
- Autenticacion.

## Bloque 3 - Modelo de datos y migraciones iniciales

Objetivo:

- Implementar modelos reales segun el modelo documentado.
- Configurar Alembic.
- Crear migraciones iniciales.
- Preparar conexion a PostgreSQL.

No incluir todavia:

- Reglas avanzadas de correccion.
- Reportes.
- Funciones fuera del MVP.

## Bloque 4 - Registro de cuadre diario

Objetivo:

- Crear el flujo para registrar un cuadre por fecha.
- Registrar monedas y billetes por denominacion.
- Calcular subtotales y totales desde el sistema.

Debe respetar:

- Un solo cuadre principal por fecha.
- Cantidades mayores o iguales a cero.
- Totales calculados, no escritos manualmente.

## Bloque 5 - Registro de gastos

Objetivo:

- Permitir registrar gastos asociados a un cuadre.
- Calcular total de gastos.
- Calcular total final.

Debe respetar:

- Gastos con monto mayor a cero.
- Gastos asociados a una sesion de caja.

## Bloque 6 - Cierre de cuadre

Objetivo:

- Permitir cerrar un cuadre diario.
- Evitar cambios silenciosos despues del cierre.
- Preparar registro de correcciones.

Debe respetar:

- Los cambios posteriores al cierre deben quedar trazados.
- No borrar registros importantes sin trazabilidad.

## Bloque 7 - Historial basico

Objetivo:

- Consultar cuadres anteriores.
- Ver detalle de monedas, billetes, gastos y totales.
- Mantener una interfaz simple y clara.

No incluir:

- Reportes avanzados.
- Graficas complejas.
- Exportaciones, salvo que se definan en un bloque futuro.

## Bloque 8 - Correcciones con trazabilidad

Objetivo:

- Registrar motivo de correccion.
- Guardar total anterior y total nuevo.
- Asociar la correccion al usuario que la realiza.

Debe respetar:

- No editar cuadres cerrados sin dejar registro.
- No borrar historial de correcciones.

## Bloques futuros fuera del MVP

Estos temas quedan excluidos por ahora:

- Facturacion.
- Inventario.
- Clientes.
- Rutas de reparto.
- Ventas.
- WhatsApp.
- Reportes avanzados.
- Multiples cajas o turnos.
