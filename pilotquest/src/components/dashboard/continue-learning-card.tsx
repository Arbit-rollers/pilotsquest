import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import type { DashboardSnapshot } from "@/lib/types/progress";

export function ContinueLearningCard({
  continueLearning,
}: {
  continueLearning: DashboardSnapshot["continueLearning"];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Continue learning</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <p className="font-medium">{continueLearning.subjectName}</p>
        <Progress value={continueLearning.progressPct} aria-label={`${continueLearning.progressPct}% complete`} />
        <p className="text-sm text-muted-foreground">{continueLearning.progressPct}% through current level</p>
        <Button
          render={<Link href={`/study/${continueLearning.levelId}`}>Continue</Link>}
          className="mt-1 w-fit"
        />
      </CardContent>
    </Card>
  );
}
