const WARNING_TEXT: Record<string, string> = {
  "time-scale-unverified":
    "The archive did not declare a time scale. Timestamps are shown as published, not as UTC.",
  "no-observations": "No observations in this field.",
  "duplicate-rows-removed": "Duplicate rows were removed.",
  "results-truncated": "The result list was truncated.",
  "columns-unverified": "Some archive columns could not be verified.",
  "unknown-detector": "That detector is not in this result.",
  "manifest-not-ready": "Data not ready yet.",
};

export function warningText(code: string): string {
  return WARNING_TEXT[code] ?? code;
}
