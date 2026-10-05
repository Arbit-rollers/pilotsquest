"use client";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { getLevelStateVisual } from "@/lib/utils/level-state";
import type { LevelNode } from "@/lib/types/progress";

export function LevelNodeTooltipPopover({ level }: { level: LevelNode }) {
  const visual = getLevelStateVisual(level.state);
  const Icon = visual.icon;

  return (
    <Popover>
      <PopoverTrigger
        render={
          <button
            type="button"
            aria-label={`${level.title}: ${visual.label}`}
            className={cn(
              "min-h-11 min-w-11 rounded-full border-2 flex items-center justify-center transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              visual.colorClassName,
              level.state === "locked" || level.state === "temporarily_unavailable"
                ? "border-current/30 bg-muted"
                : "border-current bg-background",
            )}
          >
            <Icon className="size-5" aria-hidden="true" />
          </button>
        }
      />
      <PopoverContent className="w-64 text-sm">
        <p className="font-medium">{level.title}</p>
        <p className={cn("text-xs mt-0.5", visual.colorClassName)}>{visual.label}</p>
        {level.lockExplanation ? (
          <p className="text-muted-foreground mt-2">{level.lockExplanation}</p>
        ) : null}
      </PopoverContent>
    </Popover>
  );
}
