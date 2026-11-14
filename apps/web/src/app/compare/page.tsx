import { Suspense } from "react";

import { CompareWorkspace } from "@/components/compare-workspace";

export default function ComparePage() {
  return (
    <Suspense fallback={<p className="text-sm text-muted">Loading comparison</p>}>
      <CompareWorkspace />
    </Suspense>
  );
}
