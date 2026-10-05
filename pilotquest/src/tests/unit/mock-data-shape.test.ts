import { describe, it, expect } from "vitest";
import { getAllMockQuestions } from "@/lib/mock-data/questions";

describe("mock question data shape", () => {
  const records = getAllMockQuestions();

  it("has at least 15 real EASA Air Law questions plus the 2 invented mock-gap questions", () => {
    const airLaw = records.filter((r) => r.subject === "Air Law");
    expect(airLaw.length).toBeGreaterThanOrEqual(15);
    expect(records.length).toBeGreaterThanOrEqual(17);
  });

  it("every record has non-empty question text and a valid question type", () => {
    for (const r of records) {
      expect(r.questionText.length).toBeGreaterThan(0);
      expect(["single_choice", "calculation"]).toContain(r.questionType);
    }
  });

  it("single_choice records have at least 2 choices and a correct answer among the labels", () => {
    for (const r of records.filter((r) => r.questionType === "single_choice")) {
      expect(r.choices.length).toBeGreaterThanOrEqual(2);
      const labels = r.choices.map((c) => c.label);
      const correct = Array.isArray(r.correctAnswer) ? r.correctAnswer : [r.correctAnswer];
      for (const c of correct) {
        expect(labels).toContain(c);
      }
    }
  });

  it("calculation records have empty choices and requiresScratchpad true", () => {
    for (const r of records.filter((r) => r.questionType === "calculation")) {
      expect(r.choices.length).toBe(0);
      expect(r.requiresScratchpad).toBe(true);
    }
  });

  it("requiresImage records always carry a full image asset", () => {
    for (const r of records.filter((r) => r.requiresImage)) {
      expect(r.image).toBeDefined();
      expect(r.image?.thumbnailUrl).toBeTruthy();
      expect(r.image?.fullResUrl).toBeTruthy();
      expect(r.image?.altText.length).toBeGreaterThan(0);
    }
  });

  it("real bank questions (non mock-gap) have a traceable question_id format and no mockGapNote", () => {
    for (const r of records.filter((r) => !r.mockGapNote)) {
      expect(r.questionId).toMatch(/^[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-\d{6}$/);
    }
  });
});
