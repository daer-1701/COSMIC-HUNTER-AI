# Contexto de incorporación para agentes

Leer primero README.md y los archivos 01 a 05 de esta carpeta. Este documento es una guía compartible, no confirma que exista código ni habilita despliegues o publicaciones externas.

## Objetivo

Ayudar al equipo a construir una web para el reto Planet X and SPHEREx de NASA Space Apps 2026: coordenadas → observaciones reales → secuencia temporal interpretable.

## Estado al entregar esta documentación

Solo documentación. No dependencias instaladas, API probada, datos descargados, objetivos validados ni stack aprobado. No reportar como implementadas las propuestas de estos archivos. La consulta oficial del reto falló; revisar el original cuando vuelva a estar disponible.

## Prioridad de trabajo recomendada

1. Inspeccionar estado actual del repositorio e instrucciones aplicables; puede haber cambiado desde esta guía.
2. Verificar datos y cobertura antes de diseñar una aplicación grande.
3. Entregar una secuencia pequeña y reproducible con metadatos.
4. Implementar un flujo vertical de búsqueda y reproducción.
5. Documentar resultados y limitaciones con evidencia.

## Restricciones de calidad

- Distinguir requisitos del reto, decisiones del equipo e hipótesis pendientes.
- No inventar URLs de archivos, campos del proveedor, resultados de consulta ni imágenes científicas.
- No mezclar silenciosamente bandas, releases o reprocesamientos como si fueran épocas distintas.
- No afirmar descubrimiento ni movimiento confirmado a partir de una animación sin validación.
- Conservar procedencia, fechas y configuración del procesamiento.
- Consultar documentación actual de librerías antes de fijar firmas/versiones.
- Mantener ejemplos sintéticos etiquetados y separados de resultados reales.
- Coordinar cambios a contratos entre frontend/backend antes de implementar integraciones incompatibles.

## Reporte de cada contribución

Indicar archivos cambiados, datos usados, comandos realmente ejecutados, resultados observados y pendientes. Registrar decisiones técnicas nuevas en un archivo de decisiones con fecha, motivo y alternativas. No transformar recomendaciones de esta documentación en requisitos atribuidos a NASA.

## Prompt listo para otro agente

> Lee `.documentation/README.md`, `AGENT-CONTEXT.md` y las guías 01–05. Estamos trabajando en Planet X and SPHEREx. Distingue el estado real de las propuestas. Inspecciona el repositorio antes de cambiarlo. Tu primera contribución debe demostrar una consulta real reproducible y evaluar observaciones comparables de un objetivo del reto, registrando procedencia y limitaciones. No afirmes que la API o la secuencia funcionan sin ejecutar y revisar el resultado. Después propone el siguiente paso mínimo según la evidencia.
