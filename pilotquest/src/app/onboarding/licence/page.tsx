"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { SelectableCard } from "@/components/onboarding/selectable-card";
import { Button } from "@/components/ui/button";
import { getLicenceOptions } from "@/lib/data-access/get-onboarding-options";

const AUTHORITY_KEY = "pilotquest.onboarding.authorityId";
const LICENCE_KEY = "pilotquest.onboarding.licenceIds";

export default function OnboardingLicencePage() {
  const router = useRouter();
  const [authorityId] = useState<string | null>(() =>
    typeof window === "undefined" ? null : window.localStorage.getItem(AUTHORITY_KEY),
  );
  // Multiple licences can be selected — progress/mastery stay tracked
  // separately per licence, and the dashboard's active context can switch
  // between them later (a later step; Step 1 studies the first one picked).
  const [selected, setSelected] = useState<readonly string[]>([]);

  useEffect(() => {
    if (!authorityId) {
      router.replace("/onboarding/authority");
    }
  }, [authorityId, router]);

  if (!authorityId) return null;

  const options = getLicenceOptions(authorityId);

  function toggle(id: string) {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((existing) => existing !== id) : [...prev, id],
    );
  }

  function handleContinue() {
    if (selected.length === 0) return;
    window.localStorage.setItem(LICENCE_KEY, JSON.stringify(selected));
    router.push("/onboarding/aircraft-category");
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold">Which licence(s) are you working toward?</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Pick as many as apply — progress and mastery are tracked separately per licence, and
          you can switch which one you&apos;re studying anytime.
        </p>
      </div>
      <div role="group" aria-label="Licences" className="flex flex-col gap-3">
        {options.map((opt) => (
          <SelectableCard
            key={opt.id}
            label={opt.label}
            description={opt.description}
            selected={selected.includes(opt.id)}
            onSelect={() => toggle(opt.id)}
          />
        ))}
      </div>
      <Button onClick={handleContinue} disabled={selected.length === 0} size="lg">
        Continue
      </Button>
    </div>
  );
}
