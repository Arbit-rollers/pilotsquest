import type { AuthorityContext } from "@/lib/types/authority-context";
import type { DashboardSnapshot } from "@/lib/types/progress";
import { getMockDashboardSnapshot } from "@/lib/mock-data/dashboard";

const SIMULATED_LATENCY_MS = 80;

export async function getDashboardSnapshot(context: AuthorityContext): Promise<DashboardSnapshot> {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_LATENCY_MS));
  return getMockDashboardSnapshot(context);
}
