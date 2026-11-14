"use client";

import { useMemo, useState } from "react";

import { FramePlayer } from "@/components/frame-player";
import { absoluteApiUrl, type ExampleResponse, type Observation, type SearchResponse } from "@/lib/api-client";
import { frameCaption, type DisplayFrame } from "@/lib/player";
import { warningText } from "@/lib/warnings";

type SequenceSource = SearchResponse | ExampleResponse;

const EMPTY_OBSERVATIONS: Observation[] = [];

function previewSrc(url: string | null): string | null {
  if (!url) {
    return null;
  }
  if (url.startsWith("/previews/")) {
    return url;
  }
  return absoluteApiUrl(url);
}

function toFrame(observation: Observation): DisplayFrame {
  return {
    id: observation.id,
    obsId: observation.obs_id,
    isoTime: observation.iso_time,
    mjd: observation.mjd,
    timeScale: observation.time_scale,
    detector: observation.detector,
    previewUrl: previewSrc(observation.preview_url),
    hdu: observation.hdu,
    sha256: observation.sha256,
    flags: observation.flags,
    synthetic: false,
    difference: (observation.flags ?? []).includes("display-difference"),
  };
}

export function ObservationSequence({ result }: { result: SequenceSource }) {
  const detectors = result.detectors ?? [];
  const [detector, setDetector] = useState<string | null>(detectors[0] ?? null);
  const observations = result.observations ?? EMPTY_OBSERVATIONS;
  const frames = useMemo(
    () =>
      observations
        .filter((observation) => detector === null || observation.detector === detector)
        .map(toFrame),
    [detector, observations],
  );
  const comparable = "comparable" in result ? result.comparable : null;
  const comparisonNote = "comparison_note" in result ? result.comparison_note : null;
  const coordSource = "coord_source" in result ? result.coord_source : null;
  const coordEpoch = "coord_epoch" in result ? result.coord_epoch : null;
  const notReady = (result.warnings ?? []).includes("manifest-not-ready");

  return (
    <section className="space-y-4">
      <header className="space-y-2">
        <p className="font-mono text-xs text-ember uppercase">
          {result.source === "cache" ? "Cached example" : "Live archive search"}
        </p>
        <p className="text-sm text-muted">Queried at {result.queried_at}</p>
        {(result.warnings ?? []).map((code) => (
          <p key={code} className="text-sm text-muted" role="status">
            {warningText(code)}
          </p>
        ))}
        {comparisonNote && (
          <p className="text-sm text-muted" role="status">
            {comparisonNote} Any change on screen is an apparent change.
          </p>
        )}
      </header>
      <div className="flex flex-wrap gap-2" role="group" aria-label="Detector">
        {detectors.map((value) => (
          <button
            key={value}
            type="button"
            aria-pressed={detector === value}
            className={`rounded-full px-3 py-1.5 text-sm ${detector === value ? "bg-ember text-void" : "bg-panel-2"}`}
            onClick={() => setDetector(value)}
          >
            {value}
          </button>
        ))}
        {detectors.length > 1 && (
          <button
            type="button"
            aria-pressed={detector === null}
            className={`rounded-full px-3 py-1.5 text-sm ${detector === null ? "bg-ember text-void" : "bg-panel-2"}`}
            onClick={() => setDetector(null)}
          >
            All detectors
          </button>
        )}
      </div>
      {notReady || observations.length === 0 ? (
        <p role="status" className="text-sm text-muted">
          {notReady ? "Data not ready yet." : "No observations in this field."}
        </p>
      ) : (
        <FramePlayer
          key={`${detector ?? "all"}:${frames.length}`}
          frames={frames}
          allowPlayback={comparable !== false}
          coordSource={coordSource}
          coordEpoch={coordEpoch}
          queriedAt={result.queried_at}
        />
      )}
      <ul className="max-h-80 space-y-2 overflow-auto">
        {frames.map((frame) => (
          <li key={frame.id} className="rounded-md border border-line px-3 py-2 text-sm">
            <p className="font-mono text-ember">{frameCaption(frame)}</p>
            <p className="text-muted">
              {frame.detector ?? "Detector not provided"}
              {frame.previewUrl ? "" : " · Preview not available"}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
