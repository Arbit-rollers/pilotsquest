import type { SubjectLearningMap, LevelNode } from "@/lib/types/progress";
import type { AuthorityContext } from "@/lib/types/authority-context";

const airLawLevels: readonly LevelNode[] = [
  { id: "air-law-definitions", title: "Abbreviations and Definitions", state: "mastered" },
  { id: "air-law-chicago", title: "International Aviation Law and the Chicago Convention", state: "completed" },
  { id: "air-law-registration", title: "Aircraft Registration and Markings", state: "completed", checkpointAfter: true },
  { id: "air-law-airworthiness", title: "Airworthiness of Aircraft", state: "needs_review" },
  { id: "air-law-altimeter", title: "Altimeter Setting Procedures", state: "in_progress" },
  { id: "air-law-ais", title: "Aeronautical Information Service", state: "available" },
  { id: "air-law-ats-airspace", title: "Air Traffic Services and Airspace", state: "available" },
  {
    id: "air-law-atc-services",
    title: "Air Traffic Control Services",
    state: "updated",
    lockExplanation: "A regulatory update affects this level. Complete the update mission to restore full readiness.",
  },
  {
    id: "air-law-aerodrome-control",
    title: "Aerodrome Control Service",
    state: "locked",
    checkpointAfter: true,
    lockExplanation: "Complete Air Traffic Control Services (≥70%) to unlock.",
  },
  {
    id: "air-law-area-control",
    title: "Area Control Service",
    state: "locked",
    lockExplanation: "Complete Aerodrome Control Service to unlock.",
  },
  {
    id: "air-law-radar",
    title: "Radar and Surveillance in Air Traffic Control",
    state: "locked",
    lockExplanation: "Complete Area Control Service to unlock.",
  },
  {
    id: "air-law-ssr",
    title: "Secondary Surveillance Radar",
    state: "temporarily_unavailable",
    lockExplanation: "Not enough approved questions are currently published for this objective.",
  },
  {
    id: "air-law-alerting",
    title: "Alerting Service",
    state: "locked",
    lockExplanation: "Complete Secondary Surveillance Radar to unlock.",
  },
  {
    id: "air-law-aerodromes",
    title: "Aerodromes",
    state: "locked",
    checkpointAfter: true,
    lockExplanation: "Complete Alerting Service to unlock.",
  },
  {
    id: "air-law-security",
    title: "Aviation Security",
    state: "locked",
    lockExplanation: "Complete Aerodromes to unlock.",
  },
];

const powerplantLevels: readonly LevelNode[] = [
  { id: "powerplant-gas-turbine-intro", title: "Gas-Turbine Introduction", state: "in_progress" },
  {
    id: "powerplant-mass-balance",
    title: "Basic Mass and Balance Calculations",
    state: "available",
  },
  {
    id: "powerplant-compressors",
    title: "Compressors",
    state: "locked",
    lockExplanation: "Complete Gas-Turbine Introduction (≥70%) to unlock.",
  },
];

export function getMockLearningMap(_context: AuthorityContext): readonly SubjectLearningMap[] {
  return [
    { subjectId: "air-law", subjectName: "Air Law", levels: airLawLevels },
    { subjectId: "powerplant", subjectName: "Powerplant", levels: powerplantLevels },
  ];
}

export function getMockSubjectLevels(subjectId: string, context: AuthorityContext): SubjectLearningMap | undefined {
  return getMockLearningMap(context).find((s) => s.subjectId === subjectId);
}
