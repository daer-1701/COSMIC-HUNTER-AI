# Planned scientific protocol

There is no detector or measured evaluation result at this stage.

Baseline: source extraction with background/noise/masks, WCS transformation,
association with explicit velocity bounds, and motion fitting on a tangent plane or
sphere. Preserve covariances, residuals, epochs, and calibration. Compare photometry
only with compatible spectral response; reprojection does not match PSFs. Require a
third epoch or additional evidence to strengthen associations; consider parallax,
observer geometry, source confusion, and variability as alternative explanations.

Validation: separate regions, epochs, and objects across training, tuning, and evaluation;
avoid reprocessed versions of the same exposure across splits. Fix seeds, dataset
checksums, commit, environment, thresholds, and experiment configuration.

Set A: known objects with ephemerides and observer position. Set B: injections labeled
**synthetic** into real images, with appropriate PSF/noise. Set C: static controls and
artifacts. Never present injections as discoveries.

Planned metrics: precision=TP/(TP+FP), recall=TP/(TP+FN), false positives per area/epoch,
angular astrometric error, association error/rate, fit residuals, performance by SNR
and calibrated magnitude, and processing time/memory by stage. Define tolerances and
one-to-one matching before evaluation; include confidence intervals, coverage, and
excluded cases. Report zero denominators as undefined.

An explainable heuristic score is not a calibrated probability. Compare AI against the
baseline on a separate test set before claiming improvements. A catalog non-match,
service outage, and failed query are distinct outcomes; none confirms a planet. Each
dossier includes original sources, versions, parameters, uncertainties, external results,
limitations, and human review status. Gemini only explains that dossier. Write reports
and plot labels in English while preserving original evidence metadata.
