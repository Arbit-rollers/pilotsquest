"use client";

import { useState } from "react";
import Link from "next/link";
import { CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { QuestionHeader } from "./question-header";
import { AnswerChoiceList } from "./answer-choice-list";
import { ScratchpadPanel } from "./scratchpad-panel";
import { ConfidenceSelector } from "./confidence-selector";
import { BookmarkToggle } from "./bookmark-toggle";
import { ReportQuestionDialog } from "./report-question-dialog";
import { StudySessionFooter } from "./study-session-footer";
import { PostAnswerPanel } from "./post-answer-panel";
import { ImageViewer } from "@/components/media/image-viewer";
import { submitAnswer } from "@/lib/data-access/submit-answer";
import type { AuthorityContext } from "@/lib/types/authority-context";
import type { StudentQuestionPayload, QuestionResultPayload, SubmittedAnswer } from "@/lib/types/question";
import type { StudySession as StudySessionType } from "@/lib/types/session";

function QuestionRunner({
  question,
  context,
  onNext,
  isLast,
}: {
  question: StudentQuestionPayload;
  context: AuthorityContext;
  onNext: () => void;
  isLast: boolean;
}) {
  const [selectedChoice, setSelectedChoice] = useState<string | null>(null);
  const [scratchpad, setScratchpad] = useState("");
  const [numericAnswer, setNumericAnswer] = useState("");
  const [confidence, setConfidence] = useState<1 | 2 | 3 | 4 | 5 | null>(null);
  const [result, setResult] = useState<QuestionResultPayload | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const isCalculation = question.questionType === "calculation";
  const canSubmit = isCalculation
    ? numericAnswer.trim().length > 0 && confidence !== null
    : selectedChoice !== null && confidence !== null;

  async function handleSubmit() {
    if (!canSubmit || confidence === null) return;
    setSubmitting(true);
    const answer: SubmittedAnswer = isCalculation
      ? { kind: "numeric_text", value: numericAnswer.trim() }
      : { kind: "choice", choiceLabels: [selectedChoice as string] };

    try {
      const r = await submitAnswer(question.questionId, answer, context);
      setResult(r);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <QuestionHeader
        context={context}
        questionIndex={question.questionIndex}
        totalQuestions={question.totalQuestions}
        subject={question.subject}
      />

      <div className="flex items-start justify-between gap-3">
        <h1 className="text-lg font-medium">{question.questionText}</h1>
        <div className="flex items-center shrink-0">
          <BookmarkToggle questionId={question.questionId} initialBookmarked={question.bookmarked} />
          <ReportQuestionDialog questionId={question.questionId} />
        </div>
      </div>

      {question.requiresImage && question.image ? (
        <ImageViewer
          image={question.image}
          {...(result?.revealedAnnotations ? { revealedAnnotations: result.revealedAnnotations } : {})}
        />
      ) : null}

      {isCalculation ? (
        <ScratchpadPanel
          scratchpad={scratchpad}
          onScratchpadChange={setScratchpad}
          answer={numericAnswer}
          onAnswerChange={setNumericAnswer}
          disabled={result !== null}
        />
      ) : (
        <AnswerChoiceList
          choices={question.choices}
          selectedLabel={selectedChoice}
          onSelect={setSelectedChoice}
          disabled={result !== null}
          {...(result ? { result } : {})}
        />
      )}

      <ConfidenceSelector value={confidence} onChange={setConfidence} disabled={result !== null} />

      {result ? <PostAnswerPanel result={result} question={question} /> : null}

      <StudySessionFooter
        mode={result ? "answered" : "answering"}
        canSubmit={canSubmit}
        submitting={submitting}
        onSubmit={handleSubmit}
        onNext={onNext}
      />
      {isLast && result ? (
        <p className="text-xs text-muted-foreground text-center">
          That was the last question — Next will finish this session.
        </p>
      ) : null}
    </div>
  );
}

export function StudySession({ session, context }: { session: StudySessionType; context: AuthorityContext }) {
  const [index, setIndex] = useState(0);
  const [complete, setComplete] = useState(false);

  if (session.questions.length === 0) {
    return (
      <div className="flex flex-col items-center gap-4 py-16 text-center">
        <p className="text-muted-foreground">
          No approved questions are currently available for this session.
        </p>
        <Button render={<Link href="/learn">Back to Learn</Link>} variant="secondary" />
      </div>
    );
  }

  if (complete) {
    return (
      <div className="flex flex-col items-center gap-4 py-16 text-center">
        <CheckCircle2 className="size-10 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
        <h1 className="text-lg font-medium">Session complete</h1>
        <p className="text-muted-foreground text-sm">
          You answered all {session.questions.length} questions in {session.subjectName}.
        </p>
        <div className="flex gap-2">
          <Button render={<Link href="/dashboard">Dashboard</Link>} variant="secondary" />
          <Button render={<Link href="/learn">Back to Learn</Link>} />
        </div>
      </div>
    );
  }

  const question = session.questions[index];
  if (!question) return null;

  return (
    <QuestionRunner
      key={question.questionId}
      question={question}
      context={context}
      isLast={index === session.questions.length - 1}
      onNext={() => {
        if (index === session.questions.length - 1) {
          setComplete(true);
        } else {
          setIndex((i) => i + 1);
        }
      }}
    />
  );
}
