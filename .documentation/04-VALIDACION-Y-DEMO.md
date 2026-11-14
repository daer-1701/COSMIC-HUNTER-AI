# Validación y presentación propuestas

## Comprobaciones mínimas con valor

### Datos

- Una consulta real termina y su respuesta queda registrada.
- Cada fotograma tiene fecha y observación rastreable.
- No se confunden releases o canales diferentes con observaciones temporales independientes.
- Se inspeccionan cobertura y calidad antes de afirmar un cambio.

### Procesamiento

- Revisar alineación con referencias en varios puntos del campo.
- Mostrar regiones sin cobertura como inválidas, no como señal nula física.
- Registrar interpolación y normalización; revisar que no generan un movimiento aparente.
- Si se implementan diferencias, contrastarlas con los originales y comprobar supuestos de banda, PSF y calibración.
- Los ensayos sintéticos pueden servir para probar software, siempre separados de evidencia astronómica.

### Producto

- Coordenadas fuera de rango reciben explicación: convención propuesta RA [0,360), Dec [-90,90] grados.
- No hay resultados, un único fotograma, archivos fallidos y servicio caído tienen estados distintos.
- Pausa, avance y retroceso corresponden a fechas correctas.
- La reproducción respeta preferencias de movimiento y permite inspección manual.
- Una segunda ejecución puede recuperar el ejemplo almacenado sin presentarlo como consulta en vivo.

## Matriz de objetivos a completar

Crear una ficha por Barnard’s Star, Epsilon Indi B, WISE 0855, RW Aurigae y R Draconis: fuente de posición, épocas disponibles, bandas utilizadas, calidad, resultado visual y limitaciones. Al momento de redactar estas guías todos están pendientes de prueba. No prometer que todos muestran cambios visibles con cualquier intervalo.

## Entregables propuestos

1. Código con instrucciones de instalación y versiones probadas.
2. Web o ejecución local verificable.
3. Manifiesto de un ejemplo real y procesamiento reproducible.
4. Explicación del problema, usuario, solución y decisiones.
5. Fuentes, atribuciones y limitaciones.
6. Video de respaldo si el equipo lo considera útil.

Verificar en la plataforma oficial los campos, formatos, duración del video, licencias y fecha límite. Esta lista es preparación interna y no sustituye los requisitos oficiales.

## Guion de demo candidato de tres minutos

- 0:00–0:25: explicar la dificultad de explorar observaciones dispersas.
- 0:25–0:55: introducir coordenadas y mostrar las observaciones encontradas.
- 0:55–1:45: reproducir y pausar un caso real comprobado.
- 1:45–2:20: enseñar procedencia y cómo controlamos cambios artificiales.
- 2:20–3:00: explicar límites y próximo paso.

Es una duración propuesta; adaptar a las reglas reales de presentación.

## Lenguaje de resultados

Usar «cambio aparente», «candidato para revisión» o «variación observada» según corresponda. Reservar «descubrimiento confirmado» para una validación externa suficiente. Una superposición con catálogos ayuda a interpretar; no demuestra por sí sola la naturaleza de una fuente.
