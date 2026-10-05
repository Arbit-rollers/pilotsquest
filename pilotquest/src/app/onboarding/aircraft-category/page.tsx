"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { SelectableCard } from "@/components/onboarding/selectable-card";
import { Button } from "@/components/ui/button";
import { getAircraftCategoryOptions } from "@/lib/data-access/get-onboarding-options";

const CATEGORY_KEY = "pilotquest.onboarding.aircraftCategoryId";

export default function OnboardingAircraftCategoryPage() {
  const router = useRouter();
  const options = getAircraftCategoryOptions();
  const [selected, setSelected] = useState<string | null>(null);

  function handleContinue() {
    if (!selected) return;
    window.localStorage.setItem(CATEGORY_KEY, selected);
    router.push("/onboarding/goal");
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold">Which aircraft category?</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Some licences cover more than one category — pick the one you&apos;re studying now.
        </p>
      </div>
      <div role="radiogroup" aria-label="Aircraft category" className="flex flex-col gap-3">
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
