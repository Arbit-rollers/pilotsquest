import type { AuthorityContext } from "@/lib/types/authority-context";
import type { StudentQuestionPayload } from "@/lib/types/question";
import type { StudySession } from "@/lib/types/session";
import type { FullQuestionRecord } from "@/lib/types/full-question-record";
import { getAllMockQuestions } from "@/lib/mock-data/questions";

const SIMULATED_LATENCY_MS = 120;

/**
 * The only place a full record (with answer key) is turned into the
 * safe pre-answer payload. Never spread `...record` here — every field is
 * named explicitly so a future field added to FullQuestionRecord can't
 * leak through by accident.
 */
function toStudentPayload(
  record: FullQuestionRecord,
  context: AuthorityContext,
  questionIndex: number,
  totalQuestions: number,
  bookmarked: boolean,
): StudentQuestionPayload {
  const payload: StudentQuestionPayload = {
    questionId: record.questionId,
    authorityContext: context,
    subject: record.subject,
    questionType: record.questionType,
    questionText: record.questionText,
    choices: record.choices,
    requiresImage: record.requiresImage,
    requiresScratchpad: record.requiresScratchpad,
    difficulty: record.difficulty,
    questionIndex,
    totalQuestions,
    bookmarked,
  };
  return {
    ...payload,
    ...(record.chapterTitle !== undefined ? { chapterTitle: record.chapterTitle } : {}),
    ...(record.learningObjective !== undefined ? { learningObjective: record.learningObjective } : {}),
    ...(record.image !== undefined
      ? {
          image: {
            mediaType: record.image.mediaType,
            thumbnailUrl: record.image.thumbnailUrl,
            fullResUrl: record.image.fullResUrl,
            width: record.image.width,
            height: record.image.height,
            altText: record.image.altText,
            ...(record.image.attribution !== undefined ? { attribution: record.image.attribution } : {}),
            // Only non-answer-bearing annotations are visible before submission.
            annotations: (record.image.annotations ?? []).filter((a) => !a.revealOnAnswer),
          },
        }
      : {}),
  };
}

function selectRecordsForSession(sessionId: string): readonly FullQuestionRecord[] {
  const all = getAllMockQuestions();
  if (sessionId.startsWith("powerplant")) {
    return all.filter((q) => q.subject.startsWith("Aircraft General Knowledge") || q.subject === "Mass and Balance");
  }
  // Default / air-law-* sessions: the real, verbatim bank content.
  return all.filter((q) => q.subject === "Air Law");
}

export async function startStudySession(
  sessionId: string,
  context: AuthorityContext,
): Promise<StudySession> {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_LATENCY_MS));

  const records = selectRecordsForSession(sessionId);
  const total = records.length;
  const questions = records.map((record, i) => toStudentPayload(record, context, i + 1, total, false));

  return {
    sessionId,
    subjectName: records[0]?.subject ?? "Study Session",
    totalQuestions: total,
    questions,
  };
}
