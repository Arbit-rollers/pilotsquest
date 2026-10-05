import type { FullQuestionRecord } from "@/lib/types/full-question-record";
import { easaAtplAirLawQuestions } from "./easa-atpl-a-air-law";
import { powerplantImageMockQuestion } from "./easa-atpl-a-powerplant-image-mock";
import { massAndBalanceCalculationMockQuestion } from "./easa-atpl-a-calculation-mock";

/**
 * Only lib/data-access/*.ts may import from this module. It is the sole
 * place the answer key exists alongside question text in this codebase.
 */
export function getAllMockQuestions(): readonly FullQuestionRecord[] {
  return [
    ...easaAtplAirLawQuestions,
    powerplantImageMockQuestion,
    massAndBalanceCalculationMockQuestion,
  ];
}

export function getMockQuestionById(questionId: string): FullQuestionRecord | undefined {
  return getAllMockQuestions().find((q) => q.questionId === questionId);
}
