const SIMULATED_LATENCY_MS = 100;

export async function toggleBookmark(questionId: string, nextState: boolean): Promise<boolean> {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_LATENCY_MS));
  // Mock: always succeeds. Step 2/3 persists this against the user/question.
  return nextState;
}

export type ReportCategory =
  | "wrong_answer"
  | "outdated_regulation"
  | "ambiguous_wording"
  | "incorrect_explanation"
  | "image_problem"
  | "copyright_concern"
  | "accessibility_problem"
  | "formatting_problem"
  | "other";

export async function reportQuestion(
  _questionId: string,
  _category: ReportCategory,
  _details: string,
): Promise<{ ok: true }> {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_LATENCY_MS));
  // Mock: always succeeds. Step 2/3 persists this as a QuestionReport row.
  return { ok: true };
}
