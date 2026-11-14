# Contexto, objetivo y alcance

## Base del reto

Fuente principal: [enunciado oficial](https://www.spaceappschallenge.org/2026/challenges/planet-x-and-spherex/). No accesible durante esta revisión (502).

La [reproducción de HackAthlone](https://hackathlone.com/challenges/planet-x-and-spherex) describe una herramienta web pública que acepta ascensión recta y declinación y reproduce imágenes de esa región en secuencia temporal. Propone probar Barnard’s Star, Epsilon Indi B, WISE 0855, RW Aurigae y R Draconis. Entre las ideas opcionales figuran campo de visión configurable, suma/resta de imágenes, espectros y capas de otros archivos. Clasifica el reto como avanzado.

Esto no implica que debamos descubrir un planeta nuevo para completar el objetivo descrito. Consultar nuevamente el original antes de la entrega y revisar las reglas de presentación por separado.

## Interpretación del equipo — propuesta

Problema de producto: una persona necesita explorar observaciones astronómicas sin manejar directamente archivos científicos y herramientas de escritorio.

Flujo propuesto:

1. Introducir RA/Dec en grados; ofrecer objetivos de ejemplo como ayuda.
2. Elegir región y filtros admitidos.
3. Consultar las observaciones disponibles.
4. Preparar imágenes comparables con sus fechas y procedencia.
5. Reproducir, pausar, avanzar y retroceder.
6. Inspeccionar un posible cambio y consultar limitaciones.

## MVP propuesto

- Entrada arbitraria de coordenadas, validación y mensajes comprensibles.
- Búsqueda real en el archivo y listado de observaciones.
- Una secuencia útil para al menos un objetivo, con fechas reales y reproducción temporal.
- Controles de velocidad, zoom y fotograma individual.
- Identificación de banda/detector y colección utilizados.
- Estado vacío cuando no hay observaciones o épocas comparables.
- Procedencia y transformaciones accesibles al usuario.
- Caché de un ejemplo real para una demo reproducible, etiquetado con fecha de consulta.

Los objetivos preseleccionados ayudan a demostrar el producto, pero no deben reemplazar permanentemente la entrada de coordenadas solicitada.

## Ampliaciones después del MVP

- Marcadores de candidatos y exportación de una ficha de revisión.
- Comparación por parpadeo o diferencia entre imágenes correctamente preparadas.
- Enlaces compartibles que conservan coordenadas y parámetros.
- Capas externas, fotometría y espectros cuando exista experiencia para validarlos.

Fuera del primer alcance: identificación automática de planetas, reconstrucción de todo el cielo, descarga masiva, alertas científicas certificadas y clasificación por IA sin evidencia.

## Criterio de éxito propuesto

Una persona puede abrir una región, entender qué observaciones existen y explorar una secuencia sin confundir variaciones de visualización con movimiento confirmado. El equipo puede reconstruir el resultado a partir de datos y parámetros registrados.
