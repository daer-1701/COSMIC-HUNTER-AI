import { describe, expect, it } from "vitest";

import {
  messageFromPayload,
  toObservationQuery,
  toSearchParams,
  validateObservationQuery,
  type ObservationQueryInput,
} from "@/lib/observation-query";

const VALID: ObservationQueryInput = {
  raDeg: 133.795129,
  decDeg: -7.245147,
  radiusDeg: 0.02,
  collection: "spherex_dr1",
  startMjd: null,
  endMjd: null,
};

describe("validateObservationQuery", () => {
  it("accepts the published WISE 0855 coordinates", () => {
    expect(validateObservationQuery(VALID)).toBeNull();
  });

  it("rejects a declination outside the ICRS range", () => {
    expect(validateObservationQuery({ ...VALID, decDeg: 95 })).toMatch(/Declination/);
  });

  it("requires both MJD bounds", () => {
    expect(validateObservationQuery({ ...VALID, startMjd: 60000, endMjd: null })).toMatch(/both/);
  });

  it("omits empty time bounds from the API body", () => {
    expect(toObservationQuery(VALID)).toEqual({
      ra_deg: 133.795129,
      dec_deg: -7.245147,
      radius_deg: 0.02,
      collection: "spherex_dr1",
    });
  });

  it("keeps a shareable field in the query string", () => {
    expect(toSearchParams(VALID)).toContain("ra=133.795129");
    expect(toSearchParams(VALID)).toContain("collection=spherex_dr1");
  });

  it("maps validation failures to the interface sentence", () => {
    expect(messageFromPayload({ detail: [] }, 422)).toMatch(/outside the allowed range/);
  });
});
