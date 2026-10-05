/**
 * The student's active regulatory context. Persisted (mock: localStorage,
 * real backend later: user profile / session), never inferred from the
 * currently-rendered UI. Every study-related record in the real system will
 * carry this context (PRD §7) — in Step 1 it just travels alongside mock
 * data reads.
 */
export interface AuthorityContext {
  readonly authorityId: string;
  readonly authorityName: string; // "EASA"
  readonly licenceId: string;
  readonly licenceName: string; // "ATPL(A)"
  readonly aircraftCategoryId: string;
  readonly aircraftCategoryName: string; // "Aeroplane"
  readonly syllabusLabel: string; // "2026 syllabus"
}

/** Short display form used on badges/banners: "EASA • ATPL(A) • 2026 syllabus" */
export function formatAuthorityContext(context: AuthorityContext): string {
  return `${context.authorityName} • ${context.licenceName} • ${context.syllabusLabel}`;
}

export const DEFAULT_AUTHORITY_CONTEXT: AuthorityContext = {
  authorityId: "AUTH-EASA",
  authorityName: "EASA",
  licenceId: "LIC-ATPL-A",
  licenceName: "ATPL(A)",
  aircraftCategoryId: "CAT-AEROPLANE",
  aircraftCategoryName: "Aeroplane",
  syllabusLabel: "2026 syllabus",
};
