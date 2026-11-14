---
name: cosmic-api-contracts
description: Crear o cambiar contratos FastAPI/Pydantic, jobs Celery, persistencia PostgreSQL o controles Gemini en Cosmic Hunter AI con límites claros, trazabilidad y clientes OpenAPI coherentes.
---

# Contratos científicos del backend

Lee docs/api.md, docs/architecture.md y el código afectado. Para persistencia, también
docs/data-model.md y el SQL actual. No exponer rutas que aparenten procesar datos
cuando solo hay un placeholder. Un plan de consulta devuelve executed=false.

## HTTP y schemas

Definir unidades, marco de coordenadas, escala temporal, límites y política de campos
extra en Pydantic. Rechazar no finitos e intervalos incompletos/invertidos. Paginar
consultas y acotar radio/tiempo/volumen según capacidad medida. Documentar respuestas y
errores implementados. Evitar errores HTTP 200 con fallos ocultos en el cuerpo.
No filtrar claves, trazas internas ni respuestas privadas de proveedores al navegador.

Procesamiento pesado pasa a jobs, con entradas por IDs persistidos. Diferenciar
202 aceptado de resultado final. Idempotency-Key debe enlazar cuerpo/configuración:
misma clave con petición distinta es conflicto. Autorizar lecturas/escrituras por
recurso antes de persistir o entregar artefactos privados.

## Estado y persistencia

SQL mantiene estados; Redis no es la única evidencia de progreso. Resolver atomicidad
entre creación/enqueue con outbox u otro mecanismo explícito. Diseñar entregas repetidas,
fallos a mitad de escritura, retries acotados y cancelación antes de habilitar workers.
Crear resultados inmutables por ejecución/configuración. No serializar FITS por broker.
Evolucionar esquema con migraciones; el bootstrap actual solo inicializa una base nueva.
Verificar constraints y transacciones en PostgreSQL real antes de declararlos operativos.

## Gemini, cuando la tarea lo implemente

Solo backend, con evidencia persistida y modelo/precios verificados en documentación
oficial de Google. Reservar coste máximo atómicamente antes de llamar; incluir tokens,
concurrencia, reintentos y llamadas de resultado desconocido. Sin reserva no hay llamada.
Pruebas offline para caché, cuotas y presupuesto; pruebas de pago solo cuando estén
autorizadas. Respuestas con referencias verificadas; sin modificar medidas ni estados
de descubrimiento a partir del texto del modelo.

## Verificación

Agregar pruebas de aceptación/rechazo y fallos de proveedor apropiadas al cambio.
Regenerar con `uv run python scripts/export_openapi.py`, revisar diff y ejecutar
Ruff/pytest según AGENTS.md. No escribir manualmente el contrato generado. Al entregar,
indicar rutas realmente operativas y distinguir tests unitarios de integración real.
