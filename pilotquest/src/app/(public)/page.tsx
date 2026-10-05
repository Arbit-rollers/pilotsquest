import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Compass, Gauge, ShieldCheck } from "lucide-react";
import { BrandMark } from "@/components/layout/brand-mark";

const AUTHORITY_BADGES = ["EASA", "FAA", "UK CAA", "Transport Canada"] as const;

const FEATURES = [
  {
    icon: Compass,
    title: "One authority at a time",
    description: "Your syllabus, rules, and progress never mix between jurisdictions.",
  },
  {
    icon: Gauge,
    title: "Readiness you can trust",
    description: "Mastery and engagement are tracked separately — XP is not a substitute for knowledge.",
  },
  {
    icon: ShieldCheck,
    title: "Server-scored, always",
    description: "Correct answers are never sent to your browser until after you submit.",
  },
] as const;

export default function LandingPage() {
  return (
    <div className="flex flex-1 flex-col">
      <header className="flex items-center justify-between px-6 py-4 border-b bg-card/60 backdrop-blur">
        <BrandMark size={32} wordmarkSize="md" />
        <Button render={<Link href="/onboarding">Get started</Link>} size="sm" />
      </header>

      <main className="flex-1">
        <section className="relative overflow-hidden">
          <div
            className="absolute inset-0 -z-10 bg-gradient-to-b from-primary/15 via-primary/5 to-background"
            aria-hidden="true"
          />
          <div
            className="absolute -top-24 -right-24 -z-10 size-96 rounded-full bg-primary/20 blur-3xl"
            aria-hidden="true"
          />
          <div
            className="absolute top-32 -left-24 -z-10 size-72 rounded-full bg-brand-amber/25 blur-3xl"
            aria-hidden="true"
          />

          <div className="flex flex-col items-center text-center gap-6 px-6 py-20 sm:py-28 max-w-2xl mx-auto">
            <div className="flex flex-wrap items-center justify-center gap-2">
              {AUTHORITY_BADGES.map((a) => (
                <Badge key={a} variant="secondary" className="font-normal">
                  {a}
                </Badge>
              ))}
            </div>
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-balance">
              Study for your aviation exam,{" "}
              <span className="text-primary">one authority at a time.</span>
            </h1>
            <p className="text-muted-foreground text-lg text-balance">
              PilotQuest guides you through your selected authority&apos;s syllabus with a structured
              learning path, spaced repetition, realistic diagrams, and clear progress — without ever
              mixing rules between EASA, FAA, UK CAA, and other authorities.
            </p>
            <Button render={<Link href="/onboarding">Start onboarding</Link>} size="lg" className="mt-2" />
          </div>
        </section>

        <section className="px-6 py-16 max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-6">
          {FEATURES.map((f) => (
            <div key={f.title} className="flex flex-col gap-3 rounded-xl border bg-card p-5">
              <span className="flex items-center justify-center size-10 rounded-lg bg-primary/10 text-primary">
                <f.icon className="size-5" aria-hidden="true" />
              </span>
              <h2 className="font-heading font-semibold">{f.title}</h2>
              <p className="text-sm text-muted-foreground">{f.description}</p>
            </div>
          ))}
        </section>

        <p className="text-xs text-muted-foreground max-w-md mx-auto text-center px-6 pb-16">
          PilotQuest provides independent study and practice material. Practice questions are not
          represented as official examination questions unless explicitly stated with a verified
          legal basis. Examination requirements and regulations may change; consult the applicable
          aviation authority and current official publications.
        </p>
      </main>
    </div>
  );
}
