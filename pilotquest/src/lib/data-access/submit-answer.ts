import type { AuthorityContext } from "@/lib/types/authority-context";
import { formatAuthorityContext } from "@/lib/types/authority-context";
import type { QuestionResultPayload, SubmittedAnswer } from "@/lib/types/question";
import { getMockQuestionById } from "@/lib/mock-data/questions";

const SIMULATED_LATENCY_MS = 150;

function isCorrect(record: { correctAnswer: string | readonly string[] }, answer: SubmittedAnswer): boolean {
  if (answer.kind === "numeric_text") {
    const correct = Array.isArray(record.correctAnswer) ? record.correctAnswer[0] : record.correctAnswer;
    return String(correct).trim() === answer.value.trim();
  }
  const correctLabels = Array.isArray(record.correctAnswer) ? record.correctAnswer : [record.correctAnswer];
  const submitted = [...answer.choiceLabels].sort();
  const correct = [...correctLabels].sort();
  return submitted.length === correct.length && submitted.every((l, i) => l === correct[i]);
}

/**
 * The only function that reveals correctness-bearing data to the caller.
 * This simulates a server round-trip (POST .../answer per PRD §30) — in
 * Step 2/3 this becomes a real Route Handler, and this file's shape barely
 * changes.
 */
export async function submitAnswer(
  questionId: string,
  answer: SubmittedAnswer,
  context: AuthorityContext,
): Promise<QuestionResultPayload> {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_LATENCY_MS));

  const record = getMockQuestionById(questionId);
  if (!record) {
    throw new Error(`Unknown question: ${questionId}`);
  }

  const wasCorrect = isCorrect(record, answer);
  const submittedAnswer: string | readonly string[] =
    answer.kind === "numeric_text" ? answer.value : answer.choiceLabels;

  const result: QuestionResultPayload = {
    questionId: record.questionId,
    wasCorrect,
    submittedAnswer,
    correctAnswer: record.correctAnswer,
    explanation: record.explanation,
    incorrectAnswerExplanations: record.incorrectAnswerExplanations,
    source: { title: record.sourceTitle, ...(record.sourceUrl !== undefined ? { url: record.sourceUrl } : {}) },
    lastVerified: record.lastVerified,
    jurisdictionNotice: formatAuthorityContext(context),
  };
  return {
    ...result,
    ...(record.regulationReference !== undefined ? { regulationReference: record.regulationReference } : {}),
    ...(record.handbookReference !== undefined ? { handbookReference: record.handbookReference } : {}),
    ...(record.image?.annotations
      ? { revealedAnnotations: record.image.annotations.filter((a) => a.revealOnAnswer) }
      : {}),
  };
}
