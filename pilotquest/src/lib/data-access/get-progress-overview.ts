import type { AuthorityContext } from "@/lib/types/authority-context";
import type { ProgressOverview } from "@/lib/types/progress";
import { getMockProgressOverview } from "@/lib/mock-data/progress";

const SIMULATED_LATENCY_MS = 80;

export async function getProgressOverview(context: AuthorityContext): Promise<ProgressOverview> {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_LATENCY_MS));
  return getMockProgressOverview(context);
}
