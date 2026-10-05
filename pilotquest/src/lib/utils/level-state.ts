import {
  Lock,
  CircleDot,
  PlayCircle,
  CheckCircle2,
  Star,
  RotateCcw,
  Sparkles,
  CircleSlash,
  type LucideIcon,
} from "lucide-react";
import type { LevelState } from "@/lib/types/progress";

export interface LevelStateVisual {
  readonly icon: LucideIcon;
  readonly label: string;
  readonly colorClassName: string; // text/border color, never the only signal
  readonly badgeClassName: string;
}

/**
 * Every one of the 8 PRD-defined LevelState values maps to a distinct
 * icon + label, so status is never communicated by color alone (WCAG
 * 2.2 AA). See tests/unit/level-state.test.ts for the regression guard.
 */
export const LEVEL_STATE_VISUALS: Readonly<Record<LevelState, LevelStateVisual>> = {
  locked: {
    icon: Lock,
    label: "Locked",
    colorClassName: "text-muted-foreground",
    badgeClassName: "bg-muted text-muted-foreground border-muted-foreground/30",
  },
  available: {
    icon: CircleDot,
    label: "Available",
    colorClassName: "text-sky-600 dark:text-sky-400",
    badgeClassName: "bg-sky-50 text-sky-700 border-sky-300 dark:bg-sky-950 dark:text-sky-300",
  },
  in_progress: {
    icon: PlayCircle,
    label: "In progress",
    colorClassName: "text-amber-600 dark:text-amber-400",
    badgeClassName: "bg-amber-50 text-amber-700 border-amber-300 dark:bg-amber-950 dark:text-amber-300",
  },
  completed: {
    icon: CheckCircle2,
    label: "Completed",
    colorClassName: "text-emerald-600 dark:text-emerald-400",
    badgeClassName: "bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300",
  },
  mastered: {
    icon: Star,
    label: "Mastered",
    colorClassName: "text-brand-amber",
    badgeClassName: "bg-brand-amber/15 text-brand-amber-foreground border-brand-amber/40",
  },
  needs_review: {
    icon: RotateCcw,
    label: "Needs review",
    colorClassName: "text-orange-600 dark:text-orange-400",
    badgeClassName: "bg-orange-50 text-orange-700 border-orange-300 dark:bg-orange-950 dark:text-orange-300",
  },
  updated: {
    icon: Sparkles,
    label: "Updated",
    colorClassName: "text-blue-600 dark:text-blue-400",
    badgeClassName: "bg-blue-50 text-blue-700 border-blue-300 dark:bg-blue-950 dark:text-blue-300",
  },
  temporarily_unavailable: {
    icon: CircleSlash,
    label: "Temporarily unavailable",
    colorClassName: "text-muted-foreground",
    badgeClassName: "bg-muted text-muted-foreground border-dashed border-muted-foreground/40",
  },
};

export function getLevelStateVisual(state: LevelState): LevelStateVisual {
  return LEVEL_STATE_VISUALS[state];
}
