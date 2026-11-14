import type { ExampleResponse } from "@/lib/api-client";

/**
 * The two published WISE 0855 previews committed with the app.
 * Used only when the API cannot be reached. Values match data/manifests/wise-0855.json.
 */
export const WISE_0855_BACKUP: ExampleResponse = {
  source: "cache",
  queried_at: "2026-11-14T16:17:29.256661+00:00",
  query: {
    ra_deg: 133.795129,
    dec_deg: -7.245147,
    radius_deg: 0.02,
    collection: "spherex_dr1",
  },
  warnings: [
    "Previews use a shared linear stretch from 0.216867 to 0.33087 MJy/sr. Quality flags are masked except SOURCE.",
  ],
  detectors: ["SPHEREx-D2"],
  slug: "wise-0855",
  name: "WISE 0855",
  coord_source: "NASA Space Apps challenge statement via .documentation/07-MATEO-DATOS.md",
  coord_epoch: null,
  comparable: true,
  comparison_note:
    "The two DR1 D2 exposures sample approximately 1.516 micrometers at the specified position, and two field reference centroids agree to within 0.39 arcseconds on the shared WCS grid. The previews use a common linear stretch for visual comparison. Target motion and flux changes were not measured.",
  observations: [
    {
      id: "wise-0855-1",
      obs_id: "2025W19_1B_0181_1",
      mjd: 60801.106596412,
      time_scale: "UTC",
      iso_time: "2025-05-06T02:33:29.930Z",
      collection: "spherex_dr1",
      detector: "SPHEREx-D2",
      band: null,
      hdu: 1,
      flags: [
        "quality-flags-masked-except-source",
        "preview-sha256:6499f415e4fdb125d9d924c5a8cfe29c3e208a76f83370757b9a890fe57d84a9",
      ],
      preview_url: "/previews/wise-0855-1.png",
      sha256: "962896ad59adf241c3f788e9f2c043cfc66e6e7973d1b810b98f99c614c7968f",
    },
    {
      id: "wise-0855-2",
      obs_id: "2026W20_1A_0728_1",
      mjd: 61173.064066007,
      time_scale: "UTC",
      iso_time: "2026-05-13T01:32:15.303Z",
      collection: "spherex_dr1",
      detector: "SPHEREx-D2",
      band: null,
      hdu: 1,
      flags: [
        "quality-flags-masked-except-source",
        "preview-sha256:5548d2cf461dbae5dddd64584d6ad85b026217dac068290a010059e89679c55b",
      ],
      preview_url: "/previews/wise-0855-2.png",
      sha256: "ca03de7830b74905134eace2726f7b29f5d963becf26c43ab67f9ab02eefc04f",
    },
  ],
};

export const CHALLENGE_TARGETS: { slug: ExampleResponse["slug"]; name: string }[] = [
  { slug: "barnards-star", name: "Barnard's Star" },
  { slug: "epsilon-indi-b", name: "Epsilon Indi B" },
  { slug: "wise-0855", name: "WISE 0855" },
  { slug: "rw-aurigae", name: "RW Aurigae" },
  { slug: "r-draconis", name: "R Draconis" },
];
