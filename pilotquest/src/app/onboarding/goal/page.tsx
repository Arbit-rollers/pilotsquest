"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { SelectableCard } from "@/components/onboarding/selectable-card";
import { Button } from "@/components/ui/button";
import { getStudyGoalOptions } from "@/lib/data-access/get-onboarding-options";
import { saveAuthorityContextToLocalStorage } from "@/lib/data-access/get-authority-context";
import { DEFAULT_AUTHORITY_CONTEXT } from "@/lib/types/authority-context";

export default function OnboardingGoalPage() {
  const router = useRouter();
  const options = getStudyGoalOptions();
  const [selected, setSelected] = useState<string | null>(null);

  function handleFinish() {
    if (!selected) return;
    // Step 1 mock: server-rendered pages always use DEFAULT_AUTHORITY_CONTEXT
    // (see lib/data-access/get-authority-context.ts) — this write demonstrates
    // the persistence pattern Step 2/3 completes with a real session.
    saveAuthorityContextToLocalStorage(DEFAULT_AUTHORITY_CONTEXT);
    router.push("/dashboard");
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold">What&apos;s your daily study goal?</h1>
        <p className="text-sm text-muted-foreground mt-1">You can change this later in settings.</p>
      </div>
      <div role="radiogroup" aria-label="Daily study goal" className="flex flex-col gap-3">
        {options.map((opt) => (
          <SelectableCard
            key={opt.id}
            label={opt.label}
            description={opt.description}
            selected={selected === opt.id}
            onSelect={() => setSelected(opt.id)}
          />
        ))}
      </div>
      <Button onClick={handleFinish} disabled={!selected} size="lg">
        Go to dashboard
      </Button>
    </div>
  );
}
