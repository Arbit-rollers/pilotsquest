"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { OnboardingStepper } from "@/components/onboarding/onboarding-stepper";
import { BrandMark } from "@/components/layout/brand-mark";

export default function OnboardingLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isStepPage = pathname !== "/onboarding";

  return (
    <div className="min-h-full flex flex-col">
      <header className="px-6 py-4 border-b">
        <Link href="/" className="inline-flex">
          <BrandMark size={32} wordmarkSize="md" />
        </Link>
      </header>
      <div className="flex-1 max-w-xl w-full mx-auto px-6 py-10">
        {isStepPage ? <OnboardingStepper currentPath={pathname ?? ""} /> : null}
        {children}
      </div>
    </div>
  );
}
