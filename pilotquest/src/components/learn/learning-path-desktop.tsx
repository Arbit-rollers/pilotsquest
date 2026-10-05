import { LevelNode } from "./level-node";
import { CheckpointMarker } from "./checkpoint-marker";
import type { LevelNode as LevelNodeType } from "@/lib/types/progress";

/**
 * Desktop skill-tree-ish layout — a staggered single-column path (offset
 * alternates left/right) rather than a strict vertical list, giving a
 * map-like feel without needing absolute-positioned coordinates for every
 * node. Always rendered, hidden below md via Tailwind (PRD §144).
 */
export function LearningPathDesktop({ levels }: { levels: readonly LevelNodeType[] }) {
  return (
    <ol className="hidden md:flex md:flex-col md:gap-4 md:max-w-xl">
      {levels.map((level, i) => (
        <li
          key={level.id}
          className={i % 2 === 0 ? "self-start w-3/4" : "self-end w-3/4"}
        >
          <div className="rounded-lg border bg-card p-3">
            <LevelNode level={level} sessionId={level.id} />
          </div>
          {level.checkpointAfter ? <CheckpointMarker /> : null}
        </li>
      ))}
    </ol>
  );
}
