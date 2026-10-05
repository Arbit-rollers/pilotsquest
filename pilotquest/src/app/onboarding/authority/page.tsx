"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { SelectableCard } from "@/components/onboarding/selectable-card";
import { Button } from "@/components/ui/button";
import { getAuthorityOptions } from "@/lib/data-access/get-onboarding-options";

const STORAGE_KEY = "pilotquest.onboarding.authorityId";

export default function OnboardingAuthorityPage() {
  const router = useRouter();
  const options = getAuthorityOptions();
  const [selected, setSelected] = useState<string | null>(null);

  function handleContinue() {
    if (!selected) return;
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, selected);
    }
    router.push("/onboarding/licence");
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold">Which aviation authority?</h1>
        <p className="text-sm text-muted-foreground mt-1">
          This determines which syllabus, regulations, and question bank you&apos;ll study.
        </p>
      </div>
      <div role="radiogroup" aria-label="Aviation authority" className="flex flex-col gap-3">
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
      <Button onClick={handleContinue} disabled={!selected} size="lg">
        Continue
      </Button>
    </div>
  );
}
