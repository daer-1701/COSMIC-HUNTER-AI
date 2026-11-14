# Arquitectura y plan de ejecución propuestos

Todo este archivo es diseño del equipo, no una especificación de NASA ni una aplicación existente.

## Stack candidato

- Backend Python para acceso astronómico y preparación de imágenes; FastAPI como opción.
- Astropy/Astroquery para datos y coordenadas; evaluar reproyección cuando sea necesaria.
- Frontend TypeScript con React como opción para visor y reproducción.
- Caché local para el prototipo; almacenamiento persistente si el despliegue lo requiere.

No fijar versiones hasta verificar compatibilidad en el entorno del equipo. No instalar herramientas avanzadas de extracción de fuentes si el MVP no las necesita.

## Flujo interno

Formulario → backend de búsqueda → archivo IRSA → inventario → selección de observaciones → recortes FITS → preparación común → fotogramas y manifiesto → visor.

Separar descarga/procesamiento del ciclo de animación: el visor reproduce fotogramas preparados y muestra su fecha, no solicita un FITS grande en cada paso.

## Responsabilidades de módulos

- `archive`: consultas externas, tiempos de espera, reintentos limitados y adaptación del esquema.
- `inventory`: procedencia, duplicados, filtros y orden temporal.
- `processing`: lectura FITS, WCS, recortes, máscaras y productos de visualización.
- `jobs`: estado y cancelación de trabajos largos si resulta necesario.
- `viewer`: controles, leyenda, errores y accesibilidad.
- `examples`: manifiestos de casos reales reproducibles.

## Contrato interno candidato

Estos endpoints serían nuestros; no existen todavía ni pertenecen a IRSA.

- `POST /api/search`: RA/Dec en grados, tamaño de región y filtros; devuelve inventario o trabajo pendiente.
- `POST /api/sequences`: selección de observaciones y parámetros; devuelve estado del procesamiento.
- `GET /api/sequences/{id}`: manifiesto de fotogramas, advertencias y procedencia.
- `GET /api/sequences/{id}/frames/{frame_id}`: imagen procesada.

Definir límites de tamaño y cantidad de imágenes antes de exponer la API. No aceptar URLs externas arbitrarias del cliente para descargar archivos: resolverlas desde consultas controladas al archivo.

## Modelo candidato de secuencia

ID, consulta original, colección/release, tiempo de consulta, configuración de procesamiento, lista ordenada de fotogramas y advertencias. Cada fotograma referencia su observación original y su producto procesado. Conservar metadatos científicos aparte de parámetros de reproducción como velocidad.

## Etapas con puertas de salida

### A. Viabilidad de datos

Salida: una consulta reproducible, inventario real y un caso con suficientes observaciones comparables. Si no se cumple, reducir o cambiar región/filtros antes de ampliar producto.

### B. Prueba de procesamiento

Salida: secuencia pequeña con alineación revisada, escala coherente y procedencia. Guardar resultados y parámetros.

### C. Producto mínimo

Salida: entrada de coordenadas, búsqueda, selección, reproducción, fechas y estados vacíos. Conectar primero un flujo completo.

### D. Validación y entrega

Salida: ejemplos revisados, limitaciones documentadas, demo reproducible y documentación de arranque.

### E. Mejoras

Solo después: diferencias, anotaciones, compartir consultas, catálogos y espectros.

## Reparto posible entre personas o agentes

Esta es una propuesta de coordinación; no se crearon subagentes al preparar el paquete.

- Datos: demostrar acceso/cobertura y generar inventario.
- Procesamiento: verificar comparabilidad y producir fotogramas.
- Backend: orquestar consultas, caché y respuestas.
- Frontend: implementar visor sobre contrato acordado.
- Validación/comunicación: comprobar afirmaciones y preparar narrativa.

Frontend puede usar fixtures de desarrollo explícitamente etiquetados mientras llega el backend. La demo científica final debe identificar los datos reales utilizados.
