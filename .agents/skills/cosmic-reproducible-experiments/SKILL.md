---
name: cosmic-reproducible-experiments
description: Diseñar y ejecutar notebooks, benchmarks o evaluaciones de detección y asociación temporal de Cosmic Hunter AI con trazabilidad, separación de datos y métricas científicas reproducibles.
---

# Experimentos reproducibles

Lee docs/science.md y el código evaluado. Acordar mediante la tarea la hipótesis,
baseline, población, criterio de correspondencia y recursos disponibles. No inventar
resultados cuando falten datos. Separar objetivo del experimento y funcionalidad del producto.

## Preparar

Registrar manifiesto de productos/checksums, release/calibración, región, épocas,
criterios de calidad, semilla, configuración, commit y entorno bloqueado. En notebooks,
usar nbformat/nbclient si están disponibles; dependencias nuevas justificadas en el
entorno del proyecto. Extraer lógica reutilizable a services/, sin estado oculto.

Separar entrenamiento, ajuste de umbral y test por objetos/regiones/épocas según la
pregunta científica. Evitar exposiciones reprocesadas o recortes correlacionados entre
particiones. Umbrales y tolerancias se fijan sin consultar el resultado del test.

## Evaluar

Usar conocidos con efemérides y controles estáticos. Las inyecciones deben conservar
etiqueta synthetic y documentar PSF, flujo, ruido, trayectoria y máscara. Informar la
brecha entre recuperación sintética y sensibilidad comprobada con objetos reales.

Correspondencias uno a uno con tolerancia astrométrica declarada. Medir precision,
recall, FP por área/época, error angular, fallos de asociación y tiempo/memoria por
etapa; estratificar por SNR y magnitud solo si la calibración lo permite. Mostrar
denominadores, exclusiones e intervalos de confianza. Denominador cero: indefinido,
no cero inventado. Una puntuación heurística no es una probabilidad calibrada.

Comparar IA con baseline sobre el mismo conjunto retenido; reportar ganancias y
regresiones, no solo ejemplos favorables. No promover una mejora sin evidencia.

## Ejecutar y entregar

Ejecutar notebook desde kernel limpio de arriba abajo; no usar salidas viejas como
validación. Comprobar que tablas, gráficos y conclusiones salen de la misma ejecución.
Entregar comando de reproducción, manifiesto, configuración, resultados y límites.
Si no pudo ejecutarse, declarar exactamente datos/dependencias/acceso faltantes.
Mantener outputs acotados y no versionar archivos grandes, secretos ni datos personales.
