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
| 2026-07-29 | No registrada | Rol `admin_auditor` | Ventas de contado y a crédito | Intentar anular una venta con motivo | Anulación lógica permitida o regla de negocio clara | El `POST` sí llegó al API y devolvió `500`: PostgreSQL rechazó `FOR UPDATE` sobre el lado anulable de un `LEFT JOIN`; la interfaz lo presentó como fallo de conexión | [`54-incidencia-60b-anulacion-ventas.md`](54-incidencia-60b-anulacion-ventas.md) | Alta | Se limitó el lock a `sales`, se centralizó la URL/fetch del frontend y se actualizaron `api`/`web` sin reiniciar `db` ni cambiar datos reales | Desarrollo + George | En revisión | Corrección técnica validada; método manual paralelo activo y comprobación humana con una operación real autorizada pendiente |
| 2026-07-29 | No registrada | Roles `admin_auditor` y `operator` | Login remoto | Iniciar sesión desde MacBook/iPhone por WiFi/LAN, también en navegación privada | Entrar al dashboard o mostrar un error claro | La pantalla permanecía en `Iniciando...`; después de 60B-3 agotaba el timeout. La llamada productiva sin `location` usaba el fallback compilado de Tailscale y los dispositivos LAN sin Tailscale no alcanzaban el API | [`54-incidencia-60b-anulacion-ventas.md`](54-incidencia-60b-anulacion-ventas.md) | Alta | 60B-3 añadió timeout, liberación del loading y error claro; 60B-4 corrigió `buildApiUrl` para usar `window.location` en navegador. Solo `web` fue recreada, sin cambiar entorno/backend | Desarrollo + George | En revisión | URL productiva, JSON, CORS y `401` falso comprobados en LAN/Tailscale/localhost; UI LAN/Tailscale libera el botón. Falta prueba física con ambas cuentas reales en MacBook/iPhone, localhost y Tailscale |
| 2026-07-29 | No registrada | George / `admin_auditor` | Ventas de contado y a crédito | Detectar una venta real registrada con fecha incorrecta | Corregir solo la fecha con autorización y trazabilidad | El sistema no tenía una corrección limitada; la alternativa era anular una venta válida y volverla a registrar | [`55-bloque-60c-correccion-fecha-ventas.md`](55-bloque-60c-correccion-fecha-ventas.md) | Alta | Corrección auditada exclusiva de `admin_auditor`, con motivo obligatorio, bloqueos de cierre y conservación de pagos/montos/partidas; backup y migración productiva 0027 aprobados sin reiniciar PostgreSQL | Desarrollo + George | En revisión | Despliegue técnico saludable; falta comprobación visual productiva por rol y corrección de una venta real expresamente autorizada, auditada y conciliada |

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
