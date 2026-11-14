---
name: cosmic-spherex-pipeline
description: Implementar o revisar ingestión IRSA SPHEREx, lectura FITS, WCS, compatibilidad entre épocas y mediciones de movimiento aparente en Cosmic Hunter AI. Usar para código científico de astronomy o detection.
---

# Pipeline SPHEREx verificable

Trabaja desde la raíz del repositorio. Lee docs/research.md, docs/science.md y el
módulo afectado. Comprueba qué está implementado antes de extenderlo.

## Elegir entradas

Verifica documentación vigente de IRSA sobre colección, versión y HDUs antes de
implementar acceso nuevo. Punto de partida registrado: DR1/QR3; no asumir que sigue
vigente sin comprobarlo. Construir una URL SIA2 no equivale a descargar ni interpretar
una respuesta VOTable. Inspeccionar errores/OVERFLOW del servicio y límites de consulta.
Conservar consulta, respuesta, fecha y versión del producto.

En descarga, validar hosts/redirecciones, tamaño máximo y timeout; escribir temporal
y publicar solo tras validar archivo/checksum. No desactivar verificación TLS.
Los archivos se guardan fuera de Git y las matrices grandes fuera de PostgreSQL.

## Inspeccionar y comparar

No asumir que HDU 0 contiene la imagen o fijar nombres de extensiones sin inspección.
Identificar imagen, incertidumbre, máscara, WCS y respuesta espectral según el producto.
Preservar encabezados originales y unidades. Verificar WCS con transformación de ida
y vuelta, convención de píxel y prueba de posición conocida. Época/escala temporal y
observador deben quedar explícitos; no confundir MJD con JD ni grados con radianes.

Antes de diferencia/alineación, evaluar solapamiento, longitud de onda efectiva por
píxel, calibración, PSF, saturación y flags. Documentar motivos de exclusión. Reproyectar
con máscaras y propagar errores; interpolación crea correlaciones. No tratar ruido
reproyectado como independiente. Preservar originales; normalización de pantalla no
debe sustituir intensidades científicas.

## Medir movimiento

Baseline de extracción/asociación antes de IA. Trabajar en esfera/plano tangente con
Astropy; controlar cruce RA 0/360 y polos. Estimar movimiento con fechas reales,
covarianzas, residuos e hipótesis de paralaje/observador. Una diferencia entre píxeles
o una asociación de dos épocas no confirma una trayectoria física.
Comparar contra objetos conocidos usando época y geometría del observador. Registrar
matched/no_match/unavailable/error por separado. No inferir descubrimiento por exclusión.

## Evidencia de entrega

Registrar IDs originales, checksums, versiones, parámetros, commit y entorno junto a
mediciones y errores. Probar límites geométricos y rechazo de productos incompatibles
con fixtures pequeñas etiquetadas; ejecutar integración acotada con datos reales si
se dispone de ellos. Informar qué fue medido, qué fue sintético y qué falta validar.
