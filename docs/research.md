# Fuentes, alcance y supuestos

Consulta realizada el 2026-11-14. No se descargaron observaciones científicas.

## Requisitos y verificación pendiente

La [sede Cochabamba](https://spaceappschallenge-cbba.com/#retos) describe una herramienta
web pública de visualización SPHEREx y comparación de posiciones entre fechas.
Su enlace lleva al [reto oficial Planet X and SPHEREx](https://www.spaceappschallenge.org/2026/challenges/planet-x-and-spherex/).
La página oficial devolvió HTTP 502 en dos intentos. Por ello no se consideran
verificados el enunciado completo, recursos obligatorios, entregables ni rúbrica.
Revalidarlos antes de cerrar el alcance para concurso. La sede es una referencia
local y no sustituye la rúbrica oficial. No se atribuyen al reto los 20 entregables
del brief ni sus siete motores.

Ampliaciones del equipo: Autonomous Moving Object Investigator, detección,
clasificación, expedientes, validación por catálogos, Gemini, colaboración y métricas.
La arquitectura incorpora estas propuestas con implementación gradual.

## Selección de datos

[IRSA: releases](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-releases/)
recomienda DR1 y QR3 para trabajo nuevo; sustituyen QR2. Registrar siempre release y
calibración; no mezclar versiones sin un estudio de compatibilidad.

[IRSA: acceso](https://irsa.ipac.caltech.edu/spherex-archive-documentation/spherex-data-access/)
documenta SIA2 en `https://irsa.ipac.caltech.edu/SIA`, con colecciones
`spherex_dr1` y `spherex_qr3`; el constructor inicial limita su soporte a ellas.
La descarga y lectura de respuestas VOTable queda para fase 2.

Decisión del equipo: comenzar con exposiciones individuales para conservar épocas;
usar cubos agregados solo como contexto hasta demostrar que conservan la información
temporal requerida. La disponibilidad de visitas compatibles debe comprobarse por región.
No se asume que una etiqueta de detector equivalga a una banda uniforme por píxel.

## Fuentes técnicas primarias

- [Portal de misión IRSA](https://irsa.ipac.caltech.edu/Missions/spherex.html).
- [Productos SPHEREx](https://github.com/Caltech-IPAC/spherex-archive-documentation/blob/main/documentation/spherex_data_products.md): revisar HDUs y calibraciones antes de implementar lectura.
- [Next.js: instalación](https://nextjs.org/docs/app/getting-started/installation): referencia al crear frontend.
- [Celery: Redis](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html): entregas repetidas y timeouts.

Hipótesis no comprobadas: sensibilidad a movimiento en un intervalo determinado,
cantidad de candidatos, cobertura temporal útil, calidad astrométrica y reducción de
falsos positivos. No se publican cifras antes de realizar experimentos.
