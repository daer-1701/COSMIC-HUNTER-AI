---
name: cosmic-reproducible-experiments
description: Design and run Cosmic Hunter AI notebooks, benchmarks, or detection and temporal-association evaluations with traceability, data separation, and reproducible scientific metrics.
---

# Reproducible experiments

Read docs/science.md and the evaluated code. Establish the hypothesis, baseline,
population, matching criterion, and available resources from the task. Do not invent
results when data is missing. Distinguish experiment goals from product functionality.
Write notebook explanations, plot labels, and reports in English.

## Prepare

Record the product/checksum manifest, release/calibration, region, epochs, quality
criteria, seed, configuration, commit, and locked environment. Use nbformat/nbclient
for notebooks when available; justify new dependencies in the project environment.
Move reusable logic into services/ and avoid hidden state.

Separate training, threshold tuning, and test by objects/regions/epochs according to
the scientific question. Avoid reprocessed exposures or correlated cutouts across
splits. Fix thresholds and tolerances without inspecting test results.

## Evaluate

Use known objects with ephemerides and static controls. Keep injections labeled
synthetic and document PSF, flux, noise, trajectory, and masks. Report the gap between
synthetic recovery and sensitivity demonstrated with real objects.

Use one-to-one matching with declared astrometric tolerance. Measure precision, recall,
false positives per area/epoch, angular error, association failures, and time/memory by
stage; stratify by SNR and magnitude only when calibration supports it. Show denominators,
exclusions, and confidence intervals. A zero denominator is undefined, not an invented
zero. A heuristic score is not a calibrated probability.

Compare AI with the baseline on the same held-out set. Report gains and regressions,
not just favorable examples. Do not claim improvement without evidence.

## Execute and hand off

Run notebooks top-to-bottom in a clean kernel; old outputs are not validation. Verify
that tables, plots, and conclusions come from the same run. Provide the reproduction
command, manifest, configuration, results, and limitations. If execution was not possible,
specify the missing data/dependencies/access. Keep outputs bounded and do not version
large files, secrets, or personal data.
