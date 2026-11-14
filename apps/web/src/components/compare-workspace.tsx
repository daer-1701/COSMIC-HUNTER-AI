"use client";

import { useSearchParams } from "next/navigation";

import { FramePlayer } from "@/components/frame-player";
import { TrajectoryChart } from "@/components/trajectory-chart";
import { fromSearchParams } from "@/lib/observation-query";
import type { DisplayFrame } from "@/lib/player";
import type { TrajectoryPoint } from "@/lib/trajectory";

const NO_FRAMES: DisplayFrame[] = [];
const NO_POINTS: TrajectoryPoint[] = [];

export function CompareWorkspace() {
  const params = useSearchParams();
  const field = fromSearchParams(params);

  return (
    <div className="space-y-8">
      <header className="max-w-3xl">
        <h1 className="font-serif text-4xl tracking-tight">Compare</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          Blink and difference stay disabled until two comparable visits arrive from the API. Playback
          starts paused. Arrow keys move between frames when frames exist.
        </p>
        <p className="mt-2 font-mono text-xs text-muted">
          {field
            ? `Field ${field.raDeg}°, ${field.decDeg}°, radius ${field.radiusDeg}°, ${field.collection}`
            : "No field selected. Open Explore and search a position."}
        </p>
      </header>
      <FramePlayer frames={NO_FRAMES} />
      <TrajectoryChart points={NO_POINTS} />
    </div>
  );
}
