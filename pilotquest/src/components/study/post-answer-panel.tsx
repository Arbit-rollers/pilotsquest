import { CheckCircle2, XCircle } from "lucide-react";
import { JurisdictionBanner } from "./jurisdiction-banner";
import type { QuestionResultPayload, StudentQuestionPayload } from "@/lib/types/question";

export function PostAnswerPanel({
  result,
  question,
}: {
  result: QuestionResultPayload;
  question: StudentQuestionPayload;
}) {
  const distractorLabels = question.choices
    .map((c) => c.label)
    .filter((label) => {
      const correct = Array.isArray(result.correctAnswer) ? result.correctAnswer : [result.correctAnswer];
      return !correct.includes(label);
    });

  return (
    <div className="flex flex-col gap-4 rounded-lg border p-4">
      {/* Announced without requiring focus movement (WCAG). */}
      <div aria-live="polite" className="flex items-center gap-2 font-medium">
        {result.wasCorrect ? (
          <>
            <CheckCircle2 className="size-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
            <span>Correct</span>
          </>
        ) : (
          <>
            <XCircle className="size-5 text-red-600 dark:text-red-400" aria-hidden="true" />
            <span>Incorrect</span>
          </>
        )}
      </div>

      <p className="text-sm">{result.explanation}</p>

      {distractorLabels.length > 0 ? (
        <div className="flex flex-col gap-1.5">
          {distractorLabels.map((label) => {
            const text = result.incorrectAnswerExplanations[label];
            if (!text) return null;
            return (
              <p key={label} className="text-xs text-muted-foreground">
                <span className="font-medium">{label}.</span> {text}
              </p>
            );
          })}
        </div>
      ) : null}

      {result.regulationReference || result.handbookReference ? (
        <div className="text-xs text-muted-foreground border-t pt-3 flex flex-col gap-0.5">
          {result.regulationReference ? <p>Regulation: {result.regulationReference}</p> : null}
          {result.handbookReference ? <p>Handbook: {result.handbookReference}</p> : null}
          <p>
            Source: {result.source.title}
            {result.source.url ? (
              <>
                {" "}
                (
                <a href={result.source.url} target="_blank" rel="noreferrer" className="underline underline-offset-2">
                  link
                </a>
                )
              </>
            ) : null}
          </p>
          <p>Last verified: {result.lastVerified}</p>
        </div>
      ) : null}

      <JurisdictionBanner notice={result.jurisdictionNotice} />
    </div>
  );
}
