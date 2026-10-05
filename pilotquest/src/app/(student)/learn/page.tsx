import Link from "next/link";
import { getAuthorityContext } from "@/lib/data-access/get-authority-context";
import { getLearningMap } from "@/lib/data-access/get-learning-map";
import { AuthorityContextBadge } from "@/components/layout/authority-context-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function LearnPage() {
  const context = getAuthorityContext();
  const subjects = await getLearningMap(context);

  return (
    <div className="px-4 sm:px-6 py-6 max-w-4xl mx-auto flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Learn</h1>
        <AuthorityContextBadge context={context} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {subjects.map((subject) => {
          const completed = subject.levels.filter((l) =>
            ["completed", "mastered"].includes(l.state),
          ).length;
          return (
            <Link key={subject.subjectId} href={`/learn/${subject.subjectId}`}>
              <Card className="hover:border-primary/50 transition-colors">
                <CardHeader>
                  <CardTitle className="text-base">{subject.subjectName}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {completed} / {subject.levels.length} levels completed
                  </p>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
