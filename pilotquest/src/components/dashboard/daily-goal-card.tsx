import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { DashboardSnapshot } from "@/lib/types/progress";

export function DailyGoalCard({ dailyGoal }: { dailyGoal: DashboardSnapshot["dailyGoal"] }) {
  const pct = Math.min(100, Math.round((dailyGoal.completedMinutes / dailyGoal.targetMinutes) * 100));
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Daily goal</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <Progress value={pct} aria-label={`${pct}% of daily goal complete`} />
        <p className="text-sm text-muted-foreground">
          {dailyGoal.completedMinutes} / {dailyGoal.targetMinutes} minutes today
        </p>
      </CardContent>
    </Card>
  );
}
