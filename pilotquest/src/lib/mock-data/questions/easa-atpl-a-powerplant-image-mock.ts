import type { FullQuestionRecord } from "@/lib/types/full-question-record";

/**
 * MOCK-GAP: the real question bank (pilot-question-bank/data/easa/atpl-a/powerplant/)
 * has no image-bearing questions yet (grep -c '"media"' returns 0 on both
 * EASA batches) — this is the one place Step 1 invents content, purely to
 * exercise the image-viewer UI (pan/zoom/fullscreen/annotations). The
 * question style mirrors the real Powerplant batch's schema/tone
 * (see pilot-question-bank/data/easa/atpl-a/powerplant/en/original_syllabus_aligned_batch1.jsonl,
 * e.g. EASA-ATPLA-PP-000001) but the image and its annotations are
 * placeholder SVGs under public/mock/, not real aviation diagrams.
 * Replace this file's content once the real media pipeline (Step 4) exists.
 */
export const powerplantImageMockQuestion: FullQuestionRecord = {
  questionId: "MOCK-EASA-ATPLA-PP-IMG-001",
  authority: "EASA",
  licence: "ATPL(A)",
  subject: "Aircraft General Knowledge - Powerplant",
  chapterTitle: "Gas-Turbine Introduction",
  learningObjective: "Gas-Turbine Engine Sections",
  questionType: "single_choice",
  questionText:
    "Refer to the labelled diagram. Which numbered section is the combustion chamber, where fuel is added and burned at approximately constant pressure?",
  choices: [
    { label: "A", text: "Section 1 (inlet)." },
    { label: "B", text: "Section 2 (compressor)." },
    { label: "C", text: "Section 3 (combustor)." },
    { label: "D", text: "Section 4 (turbine)." },
  ],
  correctAnswer: "C",
  explanation:
    "Section 3 is the combustor: compressed air is mixed with fuel and burned there at approximately constant pressure before the hot gas expands through the turbine.",
  incorrectAnswerExplanations: {
    A: "Section 1 is the inlet, which delivers airflow to the compressor and adds no heat.",
    B: "Section 2 is the compressor, which raises air pressure but does not burn fuel.",
    D: "Section 4 is the turbine, which extracts work from the hot gas after combustion, not where combustion occurs.",
  },
  handbookReference:
    "FAA Pilot's Handbook of Aeronautical Knowledge (FAA-H-8083-25C) and FAA Aviation Maintenance Technician Handbook - Powerplant; EASA CS-E; Gas-Turbine Introduction",
  difficulty: "intermediate",
  sourceTitle: "FAA Pilot's Handbook of Aeronautical Knowledge / EASA CS-E (topic reference)",
  sourceUrl: "https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak",
  lastVerified: "2026-09-14",
  requiresImage: true,
  image: {
    mediaType: "diagram",
    thumbnailUrl: "/mock/powerplant-diagram-thumb.svg",
    fullResUrl: "/mock/powerplant-diagram-full.svg",
    width: 800,
    height: 400,
    altText:
      "Schematic cross-section of a gas-turbine engine showing four labelled sections along the airflow path from left to right.",
    attribution: "PilotQuest placeholder diagram (Step 1 mock only, not real aviation content)",
    annotations: [
      { id: "sec-1", x: 0.1, y: 0.5, label: "1", revealOnAnswer: false },
      { id: "sec-2", x: 0.35, y: 0.5, label: "2", revealOnAnswer: false },
      { id: "sec-3", x: 0.6, y: 0.5, label: "3", revealOnAnswer: false },
      { id: "sec-4", x: 0.85, y: 0.5, label: "4", revealOnAnswer: false },
      {
        id: "sec-3-reveal",
        x: 0.6,
        y: 0.75,
        label: "Combustor - correct answer",
        revealOnAnswer: true,
      },
    ],
  },
  requiresScratchpad: false,
  mockGapNote:
    "Invented for Step 1 image-viewer UI only; no real bank content or diagram exists for this yet.",
};
