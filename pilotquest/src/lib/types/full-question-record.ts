import type { Difficulty, QuestionType, ChoiceOption } from "./question";
import type { QuestionImageAsset } from "./media";

/**
 * The full record, including the answer key — shaped closely after the
 * real question bank's schema
 * (pilot-question-bank/schemas/question.schema.json) so Step 2/3 can swap
 * this module for a real Prisma query with minimal reshaping.
 *
 * IMPORTANT: only files under lib/mock-data/ and lib/data-access/ may
 * import this type. No component, no app/**\/page.tsx may import it —
 * that is exactly the leak this whole DTO split exists to prevent.
 * (Enforced by convention + the grep check in the Step 1 acceptance
 * criteria; a real backend enforces it by the module never being bundled
 * for the client at all.)
 */
export interface FullQuestionRecord {
  readonly questionId: string; // bank's question_id, e.g. "EASA-ATPLA-AL-000001"
  readonly authority: string;
  readonly licence: string;
  readonly subject: string;
  readonly chapterTitle: string;
  readonly learningObjective?: string;
  readonly questionType: QuestionType;
  readonly questionText: string;
  readonly choices: readonly ChoiceOption[];
  readonly correctAnswer: string | readonly string[];
  readonly explanation: string;
  readonly incorrectAnswerExplanations: Readonly<Record<string, string>>;
  readonly regulationReference?: string;
  readonly handbookReference?: string;
  readonly difficulty: Difficulty;
  readonly sourceTitle: string;
  readonly sourceUrl?: string;
  readonly lastVerified: string;
  readonly requiresImage: boolean;
  readonly image?: QuestionImageAsset;
  readonly requiresScratchpad: boolean;
  /** Set only for invented Step-1 content the real bank doesn't have yet. */
  readonly mockGapNote?: string;
}
