import { getAuthorityContext } from "@/lib/data-access/get-authority-context";
import { startStudySession } from "@/lib/data-access/start-study-session";
import { StudySession } from "@/components/study/study-session";

export default async function StudySessionPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = await params;
  const context = getAuthorityContext();
  const session = await startStudySession(sessionId, context);

  return (
    <div className="px-4 sm:px-6 py-6 max-w-2xl mx-auto">
      <StudySession session={session} context={context} />
    </div>
  );
}
