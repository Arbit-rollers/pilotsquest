import {
  authorityOptions,
  licenceOptionsByAuthority,
  aircraftCategoryOptions,
  studyGoalOptions,
} from "@/lib/mock-data/onboarding-options";
import type { OnboardingOption } from "@/lib/types/session";

export function getAuthorityOptions(): readonly OnboardingOption[] {
  return authorityOptions;
}

export function getLicenceOptions(authorityId: string): readonly OnboardingOption[] {
  return licenceOptionsByAuthority[authorityId] ?? [];
}

export function getAircraftCategoryOptions(): readonly OnboardingOption[] {
  return aircraftCategoryOptions;
}

export function getStudyGoalOptions(): readonly OnboardingOption[] {
  return studyGoalOptions;
}
