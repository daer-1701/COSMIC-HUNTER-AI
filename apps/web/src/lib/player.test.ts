import { describe, expect, it } from "vitest";

import {
  canPlay,
  epochFrames,
  flagText,
  frameCaption,
  playbackBlockReason,
  provenanceFlags,
  stepIndex,
  type DisplayFrame,
} from "@/lib/player";
import { buildTrajectoryTrace } from "@/lib/trajectory";

function frame(partial: Partial<DisplayFrame>): DisplayFrame {
  return {
    id: "frame",
    isoTime: "2025-06-01T00:00:00Z",
    mjd: 60800,
    timeScale: "UTC",
    detector: "A",
    previewUrl: null,
    synthetic: false,
    difference: false,
    ...partial,
  };
}

describe("player", () => {
  it("refuses to play a single epoch", () => {
    const frames = [frame({ id: "a" })];
    expect(canPlay(frames)).toBe(false);
    expect(playbackBlockReason(frames)).toMatch(/Only one epoch/);
  });

  it("refuses to play mixed detectors", () => {
    const frames = [frame({ id: "a", detector: "A" }), frame({ id: "b", detector: "B" })];
    expect(playbackBlockReason(frames)).toMatch(/different detectors/);
  });

  it("keeps a display difference out of the epoch sequence", () => {
    const frames = [frame({ id: "a" }), frame({ id: "diff", difference: true })];
    expect(epochFrames(frames).map((item) => item.id)).toEqual(["a"]);
  });

  it("does not call an unverified timestamp UTC", () => {
    expect(
      frameCaption(
        frame({ isoTime: "2025-06-01T00:00:00", timeScale: null, mjd: 60800 }),
      ),
    ).toBe("2025-06-01T00:00:00");
  });

  it("keeps a declared UTC scale on a cached timestamp", () => {
    expect(frameCaption(frame({ isoTime: "2025-05-06T02:33:29.930Z", timeScale: "UTC" }))).toBe(
      "2025-05-06T02:33:29.930Z (UTC)",
    );
  });

  it("hides a preview checksum and keeps the quality flag", () => {
    expect(
      provenanceFlags([
        "quality-flags-masked-except-source",
        "preview-sha256:abc",
      ]).map(flagText),
    ).toEqual(["Quality flags are masked except SOURCE."]);
  });

  it("stops at the last frame unless looping", () => {
    expect(stepIndex(1, 2, 1, false)).toBe(1);
    expect(stepIndex(1, 2, 1, true)).toBe(0);
  });
});

describe("trajectory", () => {
  it("labels synthetic points and keeps the uncertainty array", () => {
    const trace = buildTrajectoryTrace([
      { epochLabel: "t1", offsetArcsec: 0.2, uncertaintyArcsec: 0.05, synthetic: true },
    ]);
    expect(trace.name).toMatch(/Synthetic/);
    expect(trace.error_y.array).toEqual([0.05]);
  });
});
