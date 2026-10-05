/**
 * Normalized-coordinate annotation over an image, per PRD §18.
 * Coordinates are 0-1, relative to the rendered image, so they survive
 * pan/zoom transforms.
 *
 * `revealOnAnswer: true` marks an annotation whose meaning is correctness-
 * bearing (PRD's "hidden_answer_marker" concept) — the pre-answer payload
 * must never include one of these; only QuestionResultPayload may.
 */
export interface NormalizedAnnotation {
  readonly id: string;
  readonly x: number; // 0-1
  readonly y: number; // 0-1
  readonly width?: number; // 0-1
  readonly height?: number; // 0-1
  readonly label?: string;
  readonly revealOnAnswer: boolean;
}

export interface QuestionImageAsset {
  readonly mediaType: "image" | "diagram" | "chart";
  readonly thumbnailUrl: string;
  readonly fullResUrl: string;
  readonly width: number;
  readonly height: number;
  readonly altText: string;
  readonly attribution?: string;
  /**
   * Annotations present here are always safe to show before an answer is
   * submitted (revealOnAnswer === false). Annotations with
   * revealOnAnswer === true live only on the full record and are copied
   * into QuestionResultPayload.revealedAnnotations after submission —
   * see lib/data-access/submit-answer.ts.
   */
  readonly annotations?: readonly NormalizedAnnotation[];
}
