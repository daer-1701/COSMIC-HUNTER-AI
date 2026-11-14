import type { components } from "@/lib/schema";

export type ObservationQuery = components["schemas"]["ObservationQuery"];
export type QueryPlan = components["schemas"]["QueryPlan"];
export type Collection = NonNullable<ObservationQuery["collection"]>;

export type ObservationQueryInput = {
  raDeg: number;
  decDeg: number;
  radiusDeg: number;
  collection: Collection;
  startMjd: number | null;
  endMjd: number | null;
};

export const COLLECTIONS = ["spherex_dr1", "spherex_qr3"] as const;

/** Coordinate preset published by the challenge statement. It fills the form only. */
export const WISE_0855_PRESET = {
  id: "wise-0855",
  name: "WISE 0855",
  raDeg: 133.795129,
  decDeg: -7.245147,
  source:
    "NASA Space Apps challenge statement: 08h55m10.831s, -7d14m42.53s. Converted to degrees. Not an observation.",
} as const;

export const TARGETS_AWAITING_POSITIONS = [
  "Barnard's Star",
  "Epsilon Indi B",
  "RW Aurigae",
  "R Draconis",
] as const;

export function validateObservationQuery(input: ObservationQueryInput): string | null {
  if (!Number.isFinite(input.raDeg) || input.raDeg < 0 || input.raDeg >= 360) {
    return "Right ascension must be in [0, 360) degrees.";
  }
  if (!Number.isFinite(input.decDeg) || input.decDeg < -90 || input.decDeg > 90) {
    return "Declination must be in [-90, 90] degrees.";
  }
  if (!Number.isFinite(input.radiusDeg) || input.radiusDeg <= 0 || input.radiusDeg > 0.5) {
    return "Radius must be in (0, 0.5] degrees.";
  }
  if (!COLLECTIONS.includes(input.collection)) {
    return "Collection must be spherex_dr1 or spherex_qr3.";
  }
  const hasStart = input.startMjd !== null;
  const hasEnd = input.endMjd !== null;
  if (hasStart !== hasEnd) {
    return "Provide both MJD bounds, or leave both empty.";
  }
  if (
    input.startMjd !== null &&
    input.endMjd !== null &&
    (!Number.isFinite(input.startMjd) ||
      !Number.isFinite(input.endMjd) ||
      input.startMjd < 0 ||
      input.endMjd < input.startMjd)
  ) {
    return "The MJD interval is invalid.";
  }
  return null;
}

export function toObservationQuery(input: ObservationQueryInput): ObservationQuery {
  const query: ObservationQuery = {
    ra_deg: input.raDeg,
    dec_deg: input.decDeg,
    radius_deg: input.radiusDeg,
    collection: input.collection,
  };
  if (input.startMjd !== null && input.endMjd !== null) {
    query.start_mjd = input.startMjd;
    query.end_mjd = input.endMjd;
  }
  return query;
}

export function toSearchParams(input: ObservationQueryInput): string {
  const params = new URLSearchParams({
    ra: String(input.raDeg),
    dec: String(input.decDeg),
    radius: String(input.radiusDeg),
    collection: input.collection,
  });
  if (input.startMjd !== null && input.endMjd !== null) {
    params.set("start_mjd", String(input.startMjd));
    params.set("end_mjd", String(input.endMjd));
  }
  return params.toString();
}

function readNumber(value: string | null): number | null {
  if (value === null || value.trim() === "") {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function fromSearchParams(params: URLSearchParams): ObservationQueryInput | null {
  const raDeg = readNumber(params.get("ra"));
  const decDeg = readNumber(params.get("dec"));
  const radiusDeg = readNumber(params.get("radius"));
  const collection = params.get("collection") ?? "spherex_dr1";
  if (raDeg === null || decDeg === null || radiusDeg === null) {
    return null;
  }
  if (collection !== "spherex_dr1" && collection !== "spherex_qr3") {
    return null;
  }
  const input: ObservationQueryInput = {
    raDeg,
    decDeg,
    radiusDeg,
    collection,
    startMjd: readNumber(params.get("start_mjd")),
    endMjd: readNumber(params.get("end_mjd")),
  };
  return validateObservationQuery(input) === null ? input : null;
}

export function messageFromPayload(payload: unknown, status: number): string {
  if (status === 422) {
    return "Those coordinates are outside the allowed range.";
  }
  if (status === 503) {
    return "The API process is not reachable.";
  }
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = payload.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }
  return "The archive request could not be prepared.";
}
