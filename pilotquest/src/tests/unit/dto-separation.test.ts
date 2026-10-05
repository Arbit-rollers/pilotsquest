import { describe, it, expect } from "vitest";
import { startStudySession } from "@/lib/data-access/start-study-session";
import { submitAnswer } from "@/lib/data-access/submit-answer";
import { DEFAULT_AUTHORITY_CONTEXT } from "@/lib/types/authority-context";

const FORBIDDEN_KEYS = ["correctAnswer", "incorrectAnswerExplanations", "revealedAnnotations"];

describe("DTO separation invariant (PRD §2.3, §29, §203)", () => {
  it("startStudySession never returns correctness-bearing fields on any question", async () => {
    const session = await startStudySession("air-law-atc-services", DEFAULT_AUTHORITY_CONTEXT);
    expect(session.questions.length).toBeGreaterThan(0);

    for (const question of session.questions) {
      const keys = Object.keys(question);
      for (const forbidden of FORBIDDEN_KEYS) {
        expect(keys).not.toContain(forbidden);
      }
      // Only non-answer-bearing annotations may appear pre-answer.
      if (question.image?.annotations) {
        for (const annotation of question.image.annotations) {
          expect(annotation.revealOnAnswer).toBe(false);
        }
      }
    }
  });

  it("submitAnswer is the only place correctAnswer is revealed, and only after submission", async () => {
    const session = await startStudySession("air-law-atc-services", DEFAULT_AUTHORITY_CONTEXT);
    const question = session.questions[0];
    expect(question).toBeDefined();
    if (!question) return;

    const result = await submitAnswer(
      question.questionId,
      { kind: "choice", choiceLabels: [question.choices[0]?.label ?? "A"] },
      DEFAULT_AUTHORITY_CONTEXT,
    );

    expect(result.correctAnswer).toBeDefined();
    expect(result.incorrectAnswerExplanations).toBeDefined();
    expect(typeof result.wasCorrect).toBe("boolean");
  });

  it("the image-required mock question withholds its revealOnAnswer annotation pre-answer", async () => {
    const session = await startStudySession("powerplant-images", DEFAULT_AUTHORITY_CONTEXT);
    const imageQuestion = session.questions.find((q) => q.requiresImage);
    expect(imageQuestion).toBeDefined();
    if (!imageQuestion?.image) return;

    const labels = imageQuestion.image.annotations?.map((a) => a.label) ?? [];
    expect(labels).not.toContain("Combustor - correct answer");

    const result = await submitAnswer(
      imageQuestion.questionId,
      { kind: "choice", choiceLabels: ["C"] },
      DEFAULT_AUTHORITY_CONTEXT,
    );
    expect(result.revealedAnnotations?.length).toBeGreaterThan(0);
  });
});
