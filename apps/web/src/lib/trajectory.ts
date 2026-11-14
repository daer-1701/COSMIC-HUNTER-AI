export type TrajectoryPoint = {
  epochLabel: string;
  offsetArcsec: number;
  uncertaintyArcsec: number;
  synthetic: boolean;
};

export function buildTrajectoryTrace(points: TrajectoryPoint[]) {
  return {
    type: "scatter" as const,
    mode: "markers" as const,
    name: points.some((point) => point.synthetic) ? "Synthetic test points" : "Measured offsets",
    x: points.map((point) => point.epochLabel),
    y: points.map((point) => point.offsetArcsec),
    error_y: {
      type: "data" as const,
      array: points.map((point) => point.uncertaintyArcsec),
      visible: true,
    },
  };
}
