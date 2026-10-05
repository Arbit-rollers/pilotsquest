import Link from "next/link";
import { getAuthorityContext } from "@/lib/data-access/get-authority-context";
import { getProgressOverview } from "@/lib/data-access/get-progress-overview";
import { AuthorityContextBadge } from "@/components/layout/authority-context-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SubjectMasteryBar } from "@/components/progress/subject-mastery-bar";
import { AccuracyOverTimeChart } from "@/components/progress/accuracy-over-time-chart";

export default async function ProgressPage() {
  const context = getAuthorityContext();
  const overview = await getProgressOverview(context);

  return (
    <div className="px-4 sm:px-6 py-6 max-w-3xl mx-auto flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Progress</h1>
        <AuthorityContextBadge context={context} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Subject mastery</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {overview.subjectMastery.map((s) => (
            <SubjectMasteryBar key={s.subjectId} subject={s} />
          ))}
          <Link href="/progress/subjects" className="text-sm text-primary underline underline-offset-2 w-fit">
            View full breakdown
          </Link>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Accuracy, last 7 days</CardTitle>
        </CardHeader>
        <CardContent>
          <AccuracyOverTimeChart points={overview.accuracyOverTime} />
        </CardContent>
      </Card>

      <Link href="/progress/objectives" className="text-sm text-primary underline underline-offset-2 w-fit">
        View objective-level breakdown
      </Link>
    </div>
  );
}
