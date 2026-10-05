import type { AuthorityContext } from "./authority-context";
import type { NormalizedAnnotation, QuestionImageAsset } from "./media";

/**
 * Trimmed for Step 1 (UI only). The bank's full schema
 * (pilot-question-bank/schemas/question.schema.json) also has
 * multiple_response, true_false, hotspot, text_entry — those get wired up
 * when the real backend (Step 3) exists.
 */
export type QuestionType = "single_choice" | "calculation";

export type Difficulty = "beginner" | "intermediate" | "advanced";

export interface ChoiceOption {
  readonly label: string; // "A" | "B" | "C" | "D"
  readonly text: string;
}

/**
 * ============================================================================
 * THE CORE INVARIANT (PRD §2.3, §29, §203)
 * ============================================================================
 * Two non-overlapping interfaces, never one interface with optional
 * sensitive fields. `StudentQuestionPayload` is everything the browser may
 * hold before an answer is submitted. `QuestionResultPayload` is everything
 * returned only from submitAnswer().
 *
 * DO NOT add `correctAnswer`, `incorrectAnswerExplanations`, or any
 * hotspot-correctness field to StudentQuestionPayload. Ever. This is
 * enforced structurally by omission (there is no optional slot for it to
 * hide in) and verified at runtime by
 * src/tests/unit/dto-separation.test.ts.
 * ============================================================================
 */
export interface StudentQuestionPayload {
  readonly questionId: string;
  readonly authorityContext: AuthorityContext;
  readonly subject: string;
  readonly chapterTitle?: string;
  readonly learningObjective?: string;
  readonly questionType: QuestionType;
  readonly questionText: string;
  readonly choices: readonly ChoiceOption[]; // [] for calculation type
  readonly requiresImage: boolean;
  readonly image?: QuestionImageAsset;
  readonly requiresScratchpad: boolean;
  readonly difficulty: Difficulty;
  readonly questionIndex: number; // 1-based, for "N of total"
  readonly totalQuestions: number;
  readonly bookmarked: boolean;
}

/**
 * Returned ONLY from submitAnswer(). This is the sole place
 * correctness-bearing fields may live on the client, and only after the
 * student has already committed an answer.
 */
export interface QuestionResultPayload {
  readonly questionId: string;
  readonly wasCorrect: boolean;
  readonly submittedAnswer: string | readonly string[];
  readonly correctAnswer: string | readonly string[];
  readonly explanation: string;
  readonly incorrectAnswerExplanations: Readonly<Record<string, string>>;
  readonly regulationReference?: string;
  readonly handbookReference?: string;
  readonly source: { readonly title: string; readonly url?: string };
  readonly lastVerified: string; // ISO date
  readonly jurisdictionNotice: string;
  readonly revealedAnnotations?: readonly NormalizedAnnotation[];
}

export type SubmittedAnswer =
  | { readonly kind: "choice"; readonly choiceLabels: readonly string[] }
  | { readonly kind: "numeric_text"; readonly value: string };

export interface AnswerSubmission {
  readonly questionId: string;
  readonly answer: SubmittedAnswer;
  readonly confidence: 1 | 2 | 3 | 4 | 5;
  readonly elapsedMs: number;
  readonly clientAttemptId: string;
}
