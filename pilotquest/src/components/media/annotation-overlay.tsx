import type { NormalizedAnnotation } from "@/lib/types/media";

/**
 * Renders annotations absolutely-positioned inside the same transformed
 * container as the image, using normalized (0-1) coordinates, so they
 * pan/zoom together with it (PRD §18).
 *
 * IMPORTANT: only pass annotations that are safe to show given the
 * current answer state. Callers must not pass revealOnAnswer annotations
 * before a QuestionResultPayload exists — see image-viewer.tsx.
 */
export function AnnotationOverlay({ annotations }: { annotations: readonly NormalizedAnnotation[] }) {
  return (
    <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
      {annotations.map((a) => (
        <div
          key={a.id}
          className="absolute -translate-x-1/2 -translate-y-1/2 flex items-center justify-center rounded-full bg-black/70 text-white text-xs font-semibold size-6 border border-white/60 shadow"
          style={{ left: `${a.x * 100}%`, top: `${a.y * 100}%` }}
        >
          {a.label}
        </div>
      ))}
    </div>
  );
}
