import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { WeakObjective } from "@/lib/types/progress";

export function WeakObjectivesList({ objectives }: { objectives: readonly WeakObjective[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Weak objectives</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-3">
          {objectives.map((obj) => (
            <li key={obj.objectiveId} className="flex items-center justify-between gap-3 text-sm">
              <div>
                <p className="font-medium">{obj.title}</p>
                <p className="text-muted-foreground text-xs">{obj.subjectName}</p>
              </div>
              <span className="font-mono text-xs tabular-nums text-amber-600 dark:text-amber-400">
                {obj.masteryScore}%
              </span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
