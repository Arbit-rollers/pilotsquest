import type { FullQuestionRecord } from "@/lib/types/full-question-record";

/**
 * MOCK-GAP: the sampled bank batch has no `calculation`-type records
 * (both EASA batches used this session are single_choice only). This is
 * an invented mass-and-balance-style question written purely to exercise
 * the scratchpad + free-text-numeric-answer UI path. Replace with a real
 * calculation-type record once one is added to the bank.
 */
export const massAndBalanceCalculationMockQuestion: FullQuestionRecord = {
  questionId: "MOCK-EASA-ATPLA-MB-CALC-001",
  authority: "EASA",
  licence: "ATPL(A)",
  subject: "Mass and Balance",
  chapterTitle: "Basic Mass and Balance Calculations",
  learningObjective: "Total Moment and Centre of Gravity",
  questionType: "calculation",
  questionText:
    "An aeroplane has a basic empty mass of 4,200 kg with a basic index of 84,000 kg·mm (forward of datum, i.e. positive). A pilot and passenger totalling 160 kg are loaded at an arm of 250 mm aft of datum. What is the total moment, in kg·mm, contributed by the pilot and passenger alone (mass x arm)?",
  choices: [],
  correctAnswer: "40000",
  explanation:
    "Moment = mass x arm = 160 kg x 250 mm = 40,000 kg·mm. (This mock question only asks for the pilot/passenger moment, not the full loaded index — a full mass-and-balance problem would also add this to the basic index and divide by total mass to find the new CG.)",
  incorrectAnswerExplanations: {},
  difficulty: "intermediate",
  sourceTitle: "PilotQuest Step 1 mock content (not sourced from the question bank)",
  lastVerified: "2026-09-14",
  requiresImage: false,
  requiresScratchpad: true,
  mockGapNote:
    "Invented for Step 1 scratchpad/calculation UI only; the sampled bank batch has no calculation-type records to draw from.",
};
