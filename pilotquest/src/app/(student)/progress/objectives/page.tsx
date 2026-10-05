import { getAuthorityContext } from "@/lib/data-access/get-authority-context";
import { getProgressOverview } from "@/lib/data-access/get-progress-overview";
import { AuthorityContextBadge } from "@/components/layout/authority-context-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ObjectiveBreakdownTable } from "@/components/progress/objective-breakdown-table";

export default async function ProgressObjectivesPage() {
  const context = getAuthorityContext();
  const overview = await getProgressOverview(context);

  return (
    <div className="px-4 sm:px-6 py-6 max-w-3xl mx-auto flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Objective breakdown</h1>
        <AuthorityContextBadge context={context} />
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Learning objectives</CardTitle>
        </CardHeader>
        <CardContent>
          <ObjectiveBreakdownTable objectives={overview.objectiveBreakdown} />
        </CardContent>
      </Card>
    </div>
  );
}
