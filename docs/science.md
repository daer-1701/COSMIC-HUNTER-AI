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

## WISE 0855 DR1 pilot

On 2026-11-14 the IRSA SIA2 query at ICRS (133.795129°, −7.245147°) with
a 0.02° radius returned 260 product rows across 131 distinct start MJDs.
The inventory notebook checks the saved response and generates two individual
previews from 120-arcsecond D2 cutouts. Both IMAGE headers declare UTC, and
their MJD-BEG values agree with the SIA start MJDs to the published precision.
This check applies to the two inspected products.

The initial pair is unsuitable for a temporal comparison. The WCS-WAVE tables give
central wavelengths of 1.516 and 1.591 µm at the target coordinates, with
local bandwidths of approximately 0.038 µm. The previews use the same sky grid
and stretch. Registration against a reference source and motion measurements
were not performed on that pair.

The selected display pair is `2025W19_1B_0181_1` and `2026W20_1A_0728_1`,
both DR1 D2. The 180-arcsecond cutouts give target wavelengths of 1.516452
and 1.516419 µm and local bandwidths near 0.03756 µm. The supplied median
PSF FWHM is 7.46 arcseconds in both headers. The pipeline retains pixels marked
only with the SOURCE bit and masks pixels with other quality flags. Two field
source centroids differ by 0.39 and 0.11 arcseconds, below half of the
6-arcsecond display pixel. Shared finite coverage on the north-up grid is 80.2%.
These checks support visual comparison. No target motion or flux was measured.
