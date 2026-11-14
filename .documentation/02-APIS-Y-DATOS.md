# APIs, datos y primer experimento

## Qué está disponible

Según la [documentación de acceso de IRSA](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access/), SIA2 permite encontrar imágenes por posición, banda y tiempo; la respuesta incluye `access_url` para recuperar datos. IRSA también ofrece acceso mediante Python con Astroquery y PyVO. Endpoint SIA: `https://irsa.ipac.caltech.edu/SIA`. TAP: `https://irsa.ipac.caltech.edu/TAP`.

Documentación alternativa del mismo archivo: https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/ . La URL de IRSA fue accesible en una consulta anterior del chat pero falló en la última revisión; verificar ambas si una falla.

No asumir respuesta JSON o PNG: inspeccionar el formato de cada servicio. Tampoco asumir ausencia de autenticación, cuotas o restricciones de navegador sin probarlo en el entorno de despliegue.

## Tutorial inicial recomendado

El [tutorial de imágenes espectrales](https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/) muestra consulta con Astroquery, lectura FITS con Astropy e inspección de WCS. Su versión consultada recomienda DR1/QR3 frente a QR2 y enumera `spherex_dr1`, `spherex_dr1_deep`, `spherex_qr3` y `spherex_qr3_deep`. Verificar colecciones en ejecución: no fijar nombres basándose en ejemplos antiguos.

### Ejemplo de arranque, adaptado del tutorial; no ejecutado aquí

```python
from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.ipac.irsa import Irsa

print(Irsa.list_collections(servicetype="SIA", filter="spherex"))
coord = SkyCoord(ra=304.693508808 * u.deg, dec=42.4436872991 * u.deg)
results = Irsa.query_sia(
    pos=(coord, 1 * u.arcsec),
    collection=["spherex_dr1", "spherex_qr3"],
)
print(results.colnames)
print(len(results))
if len(results):
    print(results["access_url"][0])
```

Las coordenadas son del ejemplo del tutorial; no se presentan como posición de un objetivo del reto. Este código solo descubre archivos. No alinea imágenes ni garantiza varias fechas, una misma banda o movimiento visible.

## Recortes

El [servicio de recortes](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/cutout_tool.html) extrae regiones pequeñas conservando estructura y metadatos de los FITS. Su documentación muestra parámetros `center` y `size` añadidos a la URL de una imagen. Utilizar una URL obtenida de una consulta actual y comprobar unidades/semántica antes de automatizar; evitar copiar rutas antiguas de ejemplos.

## Herramienta adicional existente

El [Source Discovery Tool](https://caltech-ipac.github.io/irsa-tutorials/spherex-source-discovery-tool-demo/) demuestra búsqueda y descarga, extracción de fuentes, visualización y espectros. Es un recurso para estudiar o adaptar, no un backend terminado para nuestra web. Su ejemplo de sustracción para localizar fuentes rojas no debe confundirse automáticamente con detección temporal de movimiento.

## Experimento de viabilidad propuesto

1. Crear un entorno Python aislado siguiendo el tutorial; registrar versiones realmente instaladas.
2. Listar colecciones vigentes y guardar respuesta y fecha.
3. Resolver posiciones de los cinco objetivos del reto mediante una fuente astronómica fiable. Registrar sistema de coordenadas, época y procedencia; considerar movimiento propio cuando corresponda.
4. Consultar cobertura y revisar columnas reales de la respuesta.
5. Inventariar archivos por identificador, tiempo, colección, cobertura y canal relevante.
6. Comprobar qué observaciones son independientes y comparables; una fila no equivale necesariamente a una época nueva.
7. Descargar pocos recortes y examinar HDUs, unidades, WCS y máscaras disponibles.
8. Preparar una secuencia pequeña y verificarla antes de construir el resto del producto.

## Riesgos de interpretación — controles propuestos

- DR1 y QR3 podrían contener productos relacionados: no contar reprocesamientos de una misma observación como fechas nuevas. Investigar identificadores.
- Diferencias de banda, PSF, ruido, cobertura o calibración pueden simular variabilidad.
- Usar un sistema de coordenadas común y comprobar alineación con fuentes de referencia.
- Separar normalización visual de mediciones físicas; un cambio de contraste no es fotometría.
- No rellenar huecos con datos sintéticos sin etiquetarlos claramente y excluirlos de afirmaciones científicas.
- Si no hay suficientes épocas comparables, mostrar la limitación y buscar otro caso; no inventar una secuencia.

## Registro de procedencia propuesto

Guardar por fotograma: ID de observación, colección/release, URL original, tiempo y su escala/unidad, coordenadas y sistema, banda/detector, HDU, unidades, flags utilizados, fecha de descarga, transformaciones, parámetros y versión del procesamiento. Adaptar nombres a los metadatos reales, sin inventar campos del proveedor.
