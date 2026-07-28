# 46 - Registro de incidencias del piloto

## Uso de la plantilla

Crear una fila por cada problema, bloqueo, diferencia o comportamiento
inesperado. Registrar el hecho lo antes posible y actualizar la misma fila
hasta resolverlo.

No incluir contraseñas, tokens, contenido de `.env.production.local`, dumps ni
otros secretos. Una captura debe mostrar solo la información necesaria.

## Tabla de incidencias

| Fecha | Hora | Usuario | Módulo | Acción realizada | Resultado esperado | Resultado obtenido | Captura o evidencia si existe | Gravedad (baja/media/alta/crítica) | Acción tomada | Responsable | Estado (abierto/en revisión/resuelto) | Observaciones |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAAA-MM-DD | HH:MM | Usuario individual | Módulo | Describir el paso realizado | Describir qué debía ocurrir | Describir qué ocurrió, sin secretos | Nombre o ubicación controlada de la evidencia | Baja / Media / Alta / Crítica | Acción segura realizada o “ninguna” | Nombre | Abierto / En revisión / Resuelto | Punto de corte, registro relacionado o seguimiento |

Agregar filas debajo de la fila de ejemplo. No borrar una incidencia resuelta:
cambiar su estado y conservar la explicación.

## Cómo asignar la gravedad

| Gravedad | Definición | Respuesta esperada |
| --- | --- | --- |
| Baja | Dificultad visual o de uso que no cambia datos ni bloquea la tarea | Registrar y revisar al cierre |
| Media | Una tarea se retrasa o necesita ayuda, pero existe una alternativa segura | Informar a George y dar seguimiento durante el día |
| Alta | Bloqueo de un módulo, diferencia de datos, backup fallido o riesgo de duplicado | Pausar el módulo, usar el método actual y revisar de inmediato |
| Crítica | Posible pérdida/corrupción, acceso indebido, credencial comprometida o diferencia material sin control | Detener nuevas entradas en el ERP y activar contingencia |

George puede aumentar la gravedad al encontrar impacto adicional. Para
reducirla debe dejar la razón en observaciones.

## Información mínima de una evidencia

Cuando sea posible, la evidencia debe permitir identificar:

- fecha y hora;
- usuario y rol, sin contraseña;
- módulo;
- referencia o número del registro;
- mensaje visible;
- último paso realizado;
- si el registro quedó también en el método actual.

No es necesario fotografiar información personal completa si una referencia
parcial permite investigar.

## Reglas de seguimiento

1. `Abierto`: el problema fue registrado y todavía no tiene diagnóstico.
2. `En revisión`: existe un responsable investigando o conciliando.
3. `Resuelto`: la causa o acción quedó documentada y el resultado fue
   comprobado.
4. Una diferencia no conciliada no puede marcarse como resuelta.
5. Una solución no debe borrar la descripción original.
6. Si una incidencia provoca una corrección administrativa, registrar el motivo
   y la referencia del cambio.
7. Relacionar en observaciones las incidencias repetidas.

## Resumen diario

Completar al finalizar cada jornada:

| Dato | Registro |
| --- | --- |
| Fecha | |
| Incidencias abiertas | |
| Incidencias en revisión | |
| Incidencias resueltas | |
| Incidencias altas | |
| Incidencias críticas | |
| Módulos pausados | |
| Diferencias pendientes | |
| Responsable de revisión | |
| Decisión para el día siguiente | Continuar / Pausar módulo / Detener |

## Cierre de una incidencia

Antes de marcar `Resuelto`, confirmar:

- [ ] la causa o explicación está registrada;
- [ ] la acción tomada no generó duplicados;
- [ ] el ERP y el método actual fueron conciliados cuando aplica;
- [ ] existe evidencia del resultado;
- [ ] George revisó los casos altos o críticos;
- [ ] no se incluyeron secretos;
- [ ] el módulo puede reanudarse con seguridad.
