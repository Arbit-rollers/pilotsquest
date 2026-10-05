import type { AuthorityContext } from "@/lib/types/authority-context";
import type { SubjectLearningMap } from "@/lib/types/progress";
import { getMockLearningMap, getMockSubjectLevels } from "@/lib/mock-data/learning-map";

const SIMULATED_LATENCY_MS = 80;

export async function getLearningMap(context: AuthorityContext): Promise<readonly SubjectLearningMap[]> {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_LATENCY_MS));
  return getMockLearningMap(context);
}

export async function getSubjectLevels(
  subjectId: string,
  context: AuthorityContext,
): Promise<SubjectLearningMap | undefined> {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_LATENCY_MS));
  return getMockSubjectLevels(subjectId, context);
}
