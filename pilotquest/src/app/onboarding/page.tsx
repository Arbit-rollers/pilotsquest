import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function OnboardingWelcomePage() {
  return (
    <div className="flex flex-col items-center text-center gap-6 py-8">
      <h1 className="text-2xl font-bold">Let&apos;s set up your study context</h1>
      <p className="text-muted-foreground">
        We&apos;ll ask a few questions so PilotQuest only ever shows you content for your selected
        aviation authority and licence — never mixed with other jurisdictions.
      </p>
      <Button render={<Link href="/onboarding/authority">Begin</Link>} size="lg" />
    </div>
  );
}
