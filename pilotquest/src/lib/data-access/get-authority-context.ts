import { DEFAULT_AUTHORITY_CONTEXT, type AuthorityContext } from "@/lib/types/authority-context";

const STORAGE_KEY = "pilotquest.authorityContext";

/**
 * Server-safe read of the active authority context. Step 1 has no real
 * session/auth, so Server Components always get the default context — this
 * is the exact seam Step 2/3 replaces with a real per-user session read
 * (cookie/DB), which is why every dashboard/learn/progress/study
 * Server Component calls this function rather than reading a module-level
 * constant directly.
 */
export function getAuthorityContext(): AuthorityContext {
  return DEFAULT_AUTHORITY_CONTEXT;
}

/**
 * Client-only: reads the onboarding selection saved to localStorage.
 * Used to demonstrate the selection UI/persistence pattern during
 * onboarding; does not yet flow back into server-rendered pages in Step 1
 * (see getAuthorityContext() above) since Server Components cannot read
 * localStorage. A real backend (Step 2/3) removes this asymmetry.
 */
export function readAuthorityContextFromLocalStorage(): AuthorityContext {
  if (typeof window === "undefined") return DEFAULT_AUTHORITY_CONTEXT;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_AUTHORITY_CONTEXT;
    return JSON.parse(raw) as AuthorityContext;
  } catch {
    return DEFAULT_AUTHORITY_CONTEXT;
  }
}

export function saveAuthorityContextToLocalStorage(context: AuthorityContext): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(context));
}
