const STEPS = [
  { path: "/onboarding/authority", label: "Authority" },
  { path: "/onboarding/licence", label: "Licence" },
  { path: "/onboarding/aircraft-category", label: "Aircraft category" },
  { path: "/onboarding/goal", label: "Goal" },
] as const;

export function OnboardingStepper({ currentPath }: { currentPath: string }) {
  const currentIndex = STEPS.findIndex((s) => s.path === currentPath);

  return (
    <ol className="flex items-center gap-2 mb-8" aria-label="Onboarding progress">
      {STEPS.map((step, i) => {
        const state = i < currentIndex ? "done" : i === currentIndex ? "current" : "upcoming";
        return (
          <li key={step.path} className="flex items-center gap-2 flex-1">
            <span
              aria-current={state === "current" ? "step" : undefined}
              className={
                "flex items-center justify-center size-7 shrink-0 rounded-full text-xs font-medium border " +
                (state === "done"
                  ? "bg-primary text-primary-foreground border-primary"
                  : state === "current"
                    ? "border-primary text-primary"
                    : "border-muted-foreground/30 text-muted-foreground")
              }
            >
              {i + 1}
            </span>
            <span className="text-xs text-muted-foreground hidden sm:inline">{step.label}</span>
            {i < STEPS.length - 1 ? (
              <span className="flex-1 h-px bg-border" aria-hidden="true" />
            ) : null}
          </li>
        );
      })}
    </ol>
  );
}
