export type DisplayFrame = {
  id: string;
  obsId?: string | null;
  isoTime: string | null;
  mjd: number | null;
  timeScale: string | null;
  detector: string | null;
  previewUrl: string | null;
  hdu?: number | null;
  sha256?: string | null;
  flags?: string[];
  synthetic: boolean;
  difference: boolean;
};

export type PlayerState = {
  index: number;
  playing: boolean;
  loop: boolean;
  intervalMs: number;
};

export const SPEEDS_MS = [500, 1000, 2000] as const;

export function epochFrames(frames: DisplayFrame[]): DisplayFrame[] {
  return frames.filter((frame) => !frame.difference);
}

export function initialPlayerState(): PlayerState {
  return { index: 0, playing: false, loop: false, intervalMs: 1000 };
}

export function stepIndex(index: number, count: number, direction: -1 | 1, loop: boolean): number {
  if (count <= 0) {
    return 0;
  }
  const next = index + direction;
  if (next >= count) {
    return loop ? 0 : count - 1;
  }
  if (next < 0) {
    return loop ? count - 1 : 0;
  }
  return next;
}

export function canPlay(frames: DisplayFrame[]): boolean {
  const epochs = epochFrames(frames);
  if (epochs.length < 2) {
    return false;
  }
  const detectors = new Set(epochs.map((frame) => frame.detector));
  return detectors.size <= 1;
}

export function playbackBlockReason(frames: DisplayFrame[]): string | null {
  const epochs = epochFrames(frames);
  if (epochs.length === 0) {
    return "No frames have been returned for this field.";
  }
  if (epochs.length === 1) {
    return "Only one epoch. Temporal playback needs two comparable visits.";
  }
  const detectors = new Set(epochs.map((frame) => frame.detector));
  if (detectors.size > 1) {
    return "These frames use different detectors.";
  }
  return null;
}

export function provenanceFlags(flags: string[] | undefined): string[] {
  return (flags ?? []).filter((flag) => !flag.startsWith("preview-sha256:"));
}

export function flagText(flag: string): string {
  if (flag === "quality-flags-masked-except-source") {
    return "Quality flags are masked except SOURCE.";
  }
  return flag;
}

export function frameCaption(frame: DisplayFrame): string {
  if (frame.isoTime) {
    return frame.timeScale ? `${frame.isoTime} (${frame.timeScale})` : frame.isoTime;
  }
  if (frame.mjd !== null) {
    return frame.timeScale ? `MJD ${frame.mjd} (${frame.timeScale})` : `MJD ${frame.mjd}`;
  }
  return "Time not provided";
}
