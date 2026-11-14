"use client";

import dynamic from "next/dynamic";

import type { TrajectoryPoint } from "@/lib/trajectory";

const TrajectoryPlot = dynamic(
  () => import("@/components/trajectory-plot").then((module) => module.TrajectoryPlot),
  { ssr: false, loading: () => <p className="text-sm text-muted">Loading plot</p> },
);

export function TrajectoryChart({ points }: { points: TrajectoryPoint[] }) {
  if (points.length === 0) {
    return (
      <section className="rounded-lg border border-dashed border-line p-5">
        <h2 className="font-serif text-2xl">Apparent displacement</h2>
        <p className="mt-3 text-sm leading-6 text-muted">
          No measurement points are available. Plotly stays unloaded until the API returns offsets
          and uncertainties. This view does not invent a trajectory.
        </p>
      </section>
    );
  }

  return (
    <section className="space-y-3">
      <h2 className="font-serif text-2xl">Apparent displacement</h2>
      {points.some((point) => point.synthetic) && (
        <p className="rounded-md border border-ember/50 bg-ember/10 px-3 py-2 text-sm" role="status">
          Synthetic test points. Not an observation.
        </p>
      )}
      <TrajectoryPlot points={points} />
    </section>
  );
}
