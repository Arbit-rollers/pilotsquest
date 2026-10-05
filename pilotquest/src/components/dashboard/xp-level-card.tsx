import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Sparkles } from "lucide-react";
import type { DashboardSnapshot } from "@/lib/types/progress";

export function XpLevelCard({ xp }: { xp: DashboardSnapshot["xp"] }) {
  const pct = Math.min(100, Math.round((xp.currentXp / xp.xpToNextLevel) * 100));
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Sparkles className="size-4 text-brand-amber" aria-hidden="true" />
          Pilot Level {xp.level}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <Progress
          value={pct}
          aria-label={`${xp.currentXp} of ${xp.xpToNextLevel} XP to next level`}
          className="[&_[data-slot=progress-indicator]]:bg-brand-amber"
        />
        <p className="text-sm text-muted-foreground">
          {xp.currentXp} / {xp.xpToNextLevel} XP to level {xp.level + 1}
        </p>
      </CardContent>
    </Card>
  );
}
