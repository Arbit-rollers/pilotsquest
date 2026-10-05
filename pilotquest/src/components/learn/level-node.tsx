import Link from "next/link";
import { cn } from "@/lib/utils";
import { getLevelStateVisual } from "@/lib/utils/level-state";
import { LevelNodeTooltipPopover } from "./level-node-tooltip-popover";
import type { LevelNode as LevelNodeType } from "@/lib/types/progress";

const NAVIGABLE_STATES = new Set(["available", "in_progress", "completed", "mastered", "needs_review", "updated"]);

export function LevelNode({ level, sessionId }: { level: LevelNodeType; sessionId: string }) {
  const visual = getLevelStateVisual(level.state);
  const isNavigable = NAVIGABLE_STATES.has(level.state);

  if (!isNavigable) {
    return (
      <div className="flex items-center gap-3">
        <LevelNodeTooltipPopover level={level} />
        <span className="text-sm text-muted-foreground">{level.title}</span>
      </div>
    );
  }

  return (
    <Link
      href={`/study/${sessionId}`}
      className={cn(
        "flex items-center gap-3 rounded-md min-h-11 -mx-2 px-2 py-1",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        "hover:bg-accent/50",
      )}
    >
      <span
        className={cn(
          "min-h-11 min-w-11 rounded-full border-2 border-current flex items-center justify-center bg-background",
          visual.colorClassName,
        )}
        aria-hidden="true"
      >
        <visual.icon className="size-5" />
      </span>
      <span className="text-sm font-medium">{level.title}</span>
      <span className={cn("ml-auto text-xs shrink-0", visual.colorClassName)}>{visual.label}</span>
    </Link>
  );
}
