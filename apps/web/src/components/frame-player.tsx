"use client";

import { useEffect, useState } from "react";

import {
  canPlay,
  epochFrames,
  flagText,
  frameCaption,
  initialPlayerState,
  playbackBlockReason,
  provenanceFlags,
  SPEEDS_MS,
  stepIndex,
  type DisplayFrame,
  type PlayerState,
} from "@/lib/player";

export function FramePlayer({
  frames,
  allowPlayback = true,
  coordSource = null,
  coordEpoch = null,
  queriedAt = null,
}: {
  frames: DisplayFrame[];
  allowPlayback?: boolean;
  coordSource?: string | null;
  coordEpoch?: string | null;
  queriedAt?: string | null;
}) {
  const epochs = epochFrames(frames);
  const difference = frames.find((frame) => frame.difference) ?? null;
  const [state, setState] = useState<PlayerState>(() => ({
    ...initialPlayerState(),
    loop: epochs.length === 2,
  }));
  const [showDifference, setShowDifference] = useState(false);
  const blocked = allowPlayback
    ? playbackBlockReason(frames)
    : "These visits are not comparable.";
  const current = epochs[state.index] ?? null;
  const synthetic = frames.some((frame) => frame.synthetic);

  useEffect(() => {
    if (!state.playing) {
      return;
    }
    const timer = window.setInterval(() => {
      setState((previous) => {
        const next = stepIndex(previous.index, epochs.length, 1, previous.loop);
        const finished = next === previous.index && !previous.loop;
        return { ...previous, index: next, playing: finished ? false : previous.playing };
      });
    }, state.intervalMs);
    return () => window.clearInterval(timer);
  }, [epochs.length, state.intervalMs, state.playing]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      const target = event.target;
      if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
        return;
      }
      if (event.key === "ArrowRight") {
        setState((previous) => ({
          ...previous,
          playing: false,
          index: stepIndex(previous.index, epochs.length, 1, previous.loop),
        }));
      }
      if (event.key === "ArrowLeft") {
        setState((previous) => ({
          ...previous,
          playing: false,
          index: stepIndex(previous.index, epochs.length, -1, previous.loop),
        }));
      }
      if (event.key === " ") {
        event.preventDefault();
        if (!allowPlayback || !canPlay(frames)) {
          return;
        }
        setState((previous) => ({ ...previous, playing: !previous.playing }));
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [allowPlayback, epochs.length, frames]);

  const shown = showDifference && difference ? difference : current;

  return (
    <section aria-label="Temporal player" className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h2 className="font-serif text-2xl">Time sequence</h2>
        <p className="font-mono text-sm text-ember" aria-live="polite">
          {shown ? `Frame ${state.index + 1} of ${epochs.length}: ${frameCaption(shown)}` : "No epoch"}
        </p>
      </div>
      {synthetic && (
        <p className="rounded-md border border-ember/50 bg-ember/10 px-3 py-2 text-sm" role="status">
          Synthetic frame. Not an observation.
        </p>
      )}
      {blocked && (
        <p className="text-sm text-muted" role="status">
          {blocked}
        </p>
      )}
      {shown?.previewUrl ? (
        // Previews are archive derivatives addressed by our API, not remote arbitrary URLs.
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={shown.previewUrl}
          alt={shown.difference ? "Display difference preview" : `Epoch ${frameCaption(shown)}`}
          className="max-h-[480px] w-full rounded-lg border border-line object-contain"
        />
      ) : (
        <p className="text-sm text-muted">Preview not available</p>
      )}
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          className="rounded-full bg-ember px-4 py-2 text-sm font-medium text-void disabled:opacity-40"
          disabled={!allowPlayback || !canPlay(frames)}
          onClick={() => setState((previous) => ({ ...previous, playing: !previous.playing }))}
        >
          {state.playing ? "Pause" : "Play"}
        </button>
        {epochs.length === 2 && (
          <button
            type="button"
            className="rounded-full bg-panel-2 px-4 py-2 text-sm disabled:opacity-40"
            disabled={!allowPlayback || !canPlay(frames)}
            onClick={() =>
              setState((previous) => ({ ...previous, playing: true, loop: true, intervalMs: 500 }))
            }
          >
            Blink
          </button>
        )}
        <button
          type="button"
          className="rounded-full bg-panel-2 px-4 py-2 text-sm disabled:opacity-40"
          disabled={epochs.length === 0}
          onClick={() =>
            setState((previous) => ({
              ...previous,
              playing: false,
              index: stepIndex(previous.index, epochs.length, -1, previous.loop),
            }))
          }
        >
          Previous frame
        </button>
        <button
          type="button"
          className="rounded-full bg-panel-2 px-4 py-2 text-sm disabled:opacity-40"
          disabled={epochs.length === 0}
          onClick={() =>
            setState((previous) => ({
              ...previous,
              playing: false,
              index: stepIndex(previous.index, epochs.length, 1, previous.loop),
            }))
          }
        >
          Next frame
        </button>
        <label className="ml-auto flex items-center gap-2 text-sm text-muted">
          Speed
          <select
            className="rounded-md border border-line bg-void px-2 py-1"
            value={state.intervalMs}
            onChange={(event) =>
              setState((previous) => ({ ...previous, intervalMs: Number(event.target.value) }))
            }
          >
            {SPEEDS_MS.map((ms) => (
              <option key={ms} value={ms}>
                {ms / 1000} s
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm text-muted">
          <input
            type="checkbox"
            checked={state.loop}
            onChange={(event) =>
              setState((previous) => ({ ...previous, loop: event.target.checked }))
            }
          />
          Loop
        </label>
      </div>
      <button
        type="button"
        className="rounded-full border border-line px-4 py-2 text-sm disabled:opacity-40"
        disabled={!difference}
        onClick={() => setShowDifference((value) => !value)}
      >
        {showDifference ? "Hide display difference" : "Show display difference"}
      </button>
      {showDifference && difference && (
        <p className="text-sm text-muted">
          Stretched preview difference. Not a photometric measurement.
        </p>
      )}
      {shown && <Provenance frame={shown} coordSource={coordSource} coordEpoch={coordEpoch} queriedAt={queriedAt} />}
    </section>
  );
}

function Provenance({
  frame,
  coordSource,
  coordEpoch,
  queriedAt,
}: {
  frame: DisplayFrame;
  coordSource: string | null;
  coordEpoch: string | null;
  queriedAt: string | null;
}) {
  const rows: [string, string][] = [
    ["obs_id", frame.obsId ?? "Not provided"],
    ["detector", frame.detector ?? "Not provided"],
    ["mjd", frame.mjd === null ? "Not provided" : String(frame.mjd)],
    ["iso_time", frame.isoTime ?? "Not provided"],
    ["time_scale", frame.timeScale ?? "Not declared"],
    ["hdu", frame.hdu === null || frame.hdu === undefined ? "Not provided" : String(frame.hdu)],
    ["sha256", frame.sha256 ?? "Not provided"],
    ["coord_source", coordSource ?? "Not provided"],
    ["coord_epoch", coordEpoch ?? "Not provided"],
    ["queried_at", queriedAt ?? "Not provided"],
  ];
  const flags = provenanceFlags(frame.flags);

  return (
    <section className="space-y-2" aria-label="Provenance">
      <h3 className="font-serif text-xl">Provenance</h3>
      <dl className="grid gap-2 sm:grid-cols-2">
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt className="text-xs text-muted">{label}</dt>
            <dd className="font-mono text-xs break-all">{value}</dd>
          </div>
        ))}
      </dl>
      {flags.map((flag) => (
        <p key={flag} className="text-sm text-muted">
          {flagText(flag)}
        </p>
      ))}
    </section>
  );
}
