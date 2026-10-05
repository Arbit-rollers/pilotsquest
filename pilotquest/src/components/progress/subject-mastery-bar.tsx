import { Progress } from "@/components/ui/progress";
import type { SubjectMasterySummary } from "@/lib/types/progress";

export function SubjectMasteryBar({ subject }: { subject: SubjectMasterySummary }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">{subject.subjectName}</span>
        <span className="font-mono tabular-nums">{subject.masteryScore}%</span>
      </div>
      <Progress value={subject.masteryScore} aria-label={`${subject.subjectName} mastery ${subject.masteryScore}%`} />
    </div>
  );
}
