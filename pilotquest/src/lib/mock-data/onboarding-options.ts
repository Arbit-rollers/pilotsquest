import type { OnboardingOption } from "@/lib/types/session";

export const authorityOptions: readonly OnboardingOption[] = [
  { id: "AUTH-EASA", label: "EASA", description: "European Union Aviation Safety Agency" },
  { id: "AUTH-FAA", label: "FAA", description: "United States Federal Aviation Administration" },
  { id: "AUTH-UKCAA", label: "UK CAA", description: "UK Civil Aviation Authority" },
  { id: "AUTH-TCCA", label: "Transport Canada", description: "Transport Canada Civil Aviation" },
];

export const licenceOptionsByAuthority: Readonly<Record<string, readonly OnboardingOption[]>> = {
  "AUTH-EASA": [
    { id: "LIC-ATPL-A", label: "ATPL(A)", description: "Airline Transport Pilot Licence (Aeroplane)" },
    { id: "LIC-PPL-A", label: "PPL(A)", description: "Private Pilot Licence (Aeroplane)" },
  ],
  "AUTH-FAA": [
    { id: "LIC-PAR", label: "Private Pilot - Airplane", description: "FAA Private Pilot certificate (Airplane)" },
  ],
  "AUTH-UKCAA": [{ id: "LIC-PPL-A-UK", label: "PPL(A)", description: "UK CAA Private Pilot Licence (Aeroplane)" }],
  "AUTH-TCCA": [{ id: "LIC-RPP-A", label: "RPP(A)", description: "Recreational Pilot Permit (Aeroplane)" }],
};

export const aircraftCategoryOptions: readonly OnboardingOption[] = [
  { id: "CAT-AEROPLANE", label: "Aeroplane", description: "Fixed-wing aircraft" },
  { id: "CAT-HELICOPTER", label: "Helicopter", description: "Rotorcraft" },
];

export const studyGoalOptions: readonly OnboardingOption[] = [
  { id: "GOAL-LIGHT", label: "Light", description: "10 minutes / 50 XP per day" },
  { id: "GOAL-STANDARD", label: "Standard", description: "20 minutes / 100 XP per day" },
  { id: "GOAL-INTENSIVE", label: "Intensive", description: "30 minutes / 175 XP per day" },
];
