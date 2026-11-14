---
name: cosmic-spherex-pipeline
description: Implement or review Cosmic Hunter AI IRSA SPHEREx ingestion, FITS reading, WCS, compatibility across epochs, and apparent-motion measurements. Use for scientific astronomy or detection code.
---

# Verifiable SPHEREx pipeline

Work from the repository root. Read docs/research.md, docs/science.md, and the affected
module. Check implemented behavior before extending it. Write explanations and outputs
in English while preserving original scientific metadata.

## Select inputs

Check current IRSA collection, version, and HDU documentation before implementing new
access. The recorded starting point is DR1/QR3; do not assume it remains current without
checking. Building a SIA2 URL is not downloading or interpreting a VOTable response.
Inspect service errors/OVERFLOW and query limits. Preserve query, response, date, and
product version.

For downloads, validate hosts/redirects, maximum size, and timeouts. Write temporary
files and publish only after file/checksum validation. Do not disable TLS verification.
Keep files outside Git and large arrays outside PostgreSQL.

## Inspect and compare

Do not assume HDU 0 contains the image or hardcode extension names without inspection.
Identify image, uncertainty, mask, WCS, and spectral response according to the product.
Preserve original headers and units. Verify WCS through round-trip transformations,
pixel convention, and a known-position check. Make epoch/time scale and observer explicit;
do not confuse MJD with JD or degrees with radians.

Before differencing/alignment, assess overlap, per-pixel effective wavelength,
calibration, PSF, saturation, and flags. Document exclusion reasons. Reproject with
masks and propagate errors; interpolation creates correlations. Do not treat reprojected
noise as independent. Preserve originals; display normalization must not replace
scientific intensities.

## Measure motion

Establish source extraction/association baselines before AI. Use spherical geometry or
a tangent plane with Astropy; handle RA 0/360 wraparound and poles. Estimate motion with
actual dates, covariances, residuals, and parallax/observer hypotheses. A pixel difference
or a two-epoch association does not confirm a physical trajectory. Compare with known
objects at the correct epoch and observer geometry. Record matched/no_match/unavailable/error
separately. Do not infer discovery by exclusion.

## Deliver evidence

Record original IDs, checksums, versions, parameters, commit, and environment alongside
measurements and errors. Test geometry boundaries and rejection of incompatible products
with small labeled fixtures. Run bounded integration against real data when available.
State what was measured, what was synthetic, and what still needs validation.
