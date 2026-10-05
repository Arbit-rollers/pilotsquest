import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Flame } from "lucide-react";
import type { DashboardSnapshot } from "@/lib/types/progress";

export function StreakCard({ streak }: { streak: DashboardSnapshot["streak"] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Streak</CardTitle>
      </CardHeader>
      <CardContent className="flex items-center gap-3">
        <Flame
          className={streak.isActiveToday ? "size-8 text-orange-500" : "size-8 text-muted-foreground"}
          aria-hidden="true"
        />
        <div>
          <p className="text-2xl font-bold leading-none">{streak.days}</p>
          <p className="text-sm text-muted-foreground">
            {streak.isActiveToday ? "Active today" : "Study today to keep it going"}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
