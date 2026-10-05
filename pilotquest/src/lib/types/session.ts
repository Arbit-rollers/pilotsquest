import type { StudentQuestionPayload } from "./question";

export interface StudySession {
  readonly sessionId: string;
  readonly subjectName: string;
  readonly totalQuestions: number;
  readonly questions: readonly StudentQuestionPayload[];
}

export interface OnboardingOption {
  readonly id: string;
  readonly label: string;
  readonly description: string;
}
