import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { SubjectMasterySummary } from "@/lib/types/progress";

export function SubjectMasteryOverview({ subjects }: { subjects: readonly SubjectMasterySummary[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Subject mastery</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {subjects.map((s) => (
          <div key={s.subjectId} className="flex flex-col gap-1">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">{s.subjectName}</span>
              <span className="font-mono tabular-nums">{s.masteryScore}%</span>
            </div>
            <Progress value={s.masteryScore} aria-label={`${s.subjectName} mastery ${s.masteryScore}%`} />
          </div>
        ))}
        <Link href="/progress/subjects" className="text-sm text-primary underline underline-offset-2 w-fit">
          View full breakdown
        </Link>
      </CardContent>
    </Card>
  );
}
