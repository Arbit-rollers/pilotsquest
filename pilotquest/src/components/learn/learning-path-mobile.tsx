import { LevelNode } from "./level-node";
import { CheckpointMarker } from "./checkpoint-marker";
import type { LevelNode as LevelNodeType } from "@/lib/types/progress";

/** Vertical path — always rendered, hidden on md+ via Tailwind (PRD §144). */
export function LearningPathMobile({ levels }: { levels: readonly LevelNodeType[] }) {
  return (
    <ol className="md:hidden flex flex-col gap-3">
      {levels.map((level) => (
        <li key={level.id}>
          <LevelNode level={level} sessionId={level.id} />
          {level.checkpointAfter ? <CheckpointMarker /> : null}
        </li>
      ))}
    </ol>
  );
}
