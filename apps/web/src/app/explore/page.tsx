import { Suspense } from "react";

import { ExploreWorkspace } from "@/components/explore-workspace";

export default function ExplorePage() {
  return (
    <Suspense fallback={<p className="text-sm text-muted">Loading observations</p>}>
      <ExploreWorkspace />
    </Suspense>
  );
}
