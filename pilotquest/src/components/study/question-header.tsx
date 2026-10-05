import { AuthorityContextBadge } from "@/components/layout/authority-context-badge";
import type { AuthorityContext } from "@/lib/types/authority-context";

export function QuestionHeader({
  context,
  questionIndex,
  totalQuestions,
  subject,
}: {
  context: AuthorityContext;
  questionIndex: number;
  totalQuestions: number;
  subject: string;
}) {
  const pct = Math.round((questionIndex / totalQuestions) * 100);
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <AuthorityContextBadge context={context} />
        <span className="text-xs text-muted-foreground">{subject}</span>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
          <div
            className="h-full bg-primary motion-safe:transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="text-xs text-muted-foreground shrink-0 tabular-nums">
          {questionIndex} / {totalQuestions}
        </span>
      </div>
    </div>
  );
}
