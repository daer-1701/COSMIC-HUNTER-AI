import { createElement } from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { FramePlayer } from "@/components/frame-player";
import { TrajectoryChart } from "@/components/trajectory-chart";
import type { DisplayFrame } from "@/lib/player";

afterEach(() => {
  cleanup();
});

const syntheticPair: DisplayFrame[] = [
  {
    id: "s1",
    isoTime: null,
    mjd: 1,
    timeScale: "UTC",
    detector: "A",
    previewUrl: null,
    synthetic: true,
    difference: false,
  },
  {
    id: "s2",
    isoTime: null,
    mjd: 2,
    timeScale: "UTC",
    detector: "A",
    previewUrl: null,
    synthetic: true,
    difference: false,
  },
];

describe("FramePlayer", () => {
  it("shows the empty epoch state and disables playback", () => {
    render(createElement(FramePlayer, { frames: [] }));
    expect(screen.getByText("No frames have been returned for this field.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Play" }).hasAttribute("disabled")).toBe(true);
    expect(screen.getByText("Preview not available")).toBeTruthy();
  });

  it("marks synthetic frames instead of treating them as observations", () => {
    render(createElement(FramePlayer, { frames: syntheticPair }));
    expect(screen.getByText("Synthetic frame. Not an observation.")).toBeTruthy();
  });
});

describe("TrajectoryChart", () => {
  it("does not draw a trajectory when no measurements exist", () => {
    render(createElement(TrajectoryChart, { points: [] }));
    expect(screen.getByText(/does not invent a trajectory/)).toBeTruthy();
  });
});
