import { notFound } from "next/navigation";
import { getAuthorityContext } from "@/lib/data-access/get-authority-context";
import { getSubjectLevels } from "@/lib/data-access/get-learning-map";
import { AuthorityContextBadge } from "@/components/layout/authority-context-badge";
import { LearningPathMobile } from "@/components/learn/learning-path-mobile";
import { LearningPathDesktop } from "@/components/learn/learning-path-desktop";

export default async function SubjectLearnPage({
  params,
}: {
  params: Promise<{ subjectId: string }>;
}) {
  const { subjectId } = await params;
  const context = getAuthorityContext();
  const subject = await getSubjectLevels(subjectId, context);

  if (!subject) notFound();

  return (
    <div className="px-4 sm:px-6 py-6 max-w-4xl mx-auto flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">{subject.subjectName}</h1>
        <AuthorityContextBadge context={context} />
      </div>

      <LearningPathMobile levels={subject.levels} />
      <LearningPathDesktop levels={subject.levels} />
    </div>
  );
}
