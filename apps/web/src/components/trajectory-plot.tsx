"use client";

import { useEffect, useRef } from "react";
import type { PlotlyHTMLElement } from "plotly.js";

import { buildTrajectoryTrace, type TrajectoryPoint } from "@/lib/trajectory";

export function TrajectoryPlot({ points }: { points: TrajectoryPoint[] }) {
  const host = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = host.current;
    if (!node) {
      return;
    }
    let cancelled = false;
    let plotted: PlotlyHTMLElement | null = null;
    void import("plotly.js-basic-dist").then((module) => {
      if (cancelled || !host.current) {
        return;
      }
      const Plotly = module.default;
      void Plotly.newPlot(
        host.current,
        [buildTrajectoryTrace(points)],
        {
          paper_bgcolor: "#1c241c",
          plot_bgcolor: "#121612",
          font: { color: "#efe7d8", family: "IBM Plex Mono, ui-monospace, monospace" },
          margin: { t: 24, r: 16, b: 48, l: 56 },
          xaxis: { title: { text: "Epoch" } },
          yaxis: { title: { text: "Offset (arcsec)" } },
        },
        { responsive: true, displayModeBar: false },
      ).then((graph) => {
        plotted = graph;
      });
    });
    return () => {
      cancelled = true;
      if (plotted) {
        void import("plotly.js-basic-dist").then((module) => {
          module.default.purge(plotted!);
        });
      }
    };
  }, [points]);

  return <div ref={host} className="h-80 rounded-lg border border-line" role="img" aria-label="Offset versus epoch with uncertainties" />;
}
