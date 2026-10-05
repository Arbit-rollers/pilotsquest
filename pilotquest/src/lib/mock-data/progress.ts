import type { ProgressOverview } from "@/lib/types/progress";
import type { AuthorityContext } from "@/lib/types/authority-context";

export function getMockProgressOverview(_context: AuthorityContext): ProgressOverview {
  return {
    subjectMastery: [
      { subjectId: "air-law", subjectName: "Air Law", masteryScore: 68 },
      { subjectId: "powerplant", subjectName: "Powerplant", masteryScore: 41 },
    ],
    accuracyOverTime: [
      { dateLabel: "Mon", accuracyPct: 58 },
      { dateLabel: "Tue", accuracyPct: 63 },
      { dateLabel: "Wed", accuracyPct: 60 },
      { dateLabel: "Thu", accuracyPct: 71 },
      { dateLabel: "Fri", accuracyPct: 69 },
      { dateLabel: "Sat", accuracyPct: 75 },
      { dateLabel: "Sun", accuracyPct: 78 },
    ],
    objectiveBreakdown: [
      { objectiveId: "obj-definitions", title: "Abbreviations and Definitions", masteryScore: 92, questionsAnswered: 24 },
      { objectiveId: "obj-chicago", title: "International Aviation Law and the Chicago Convention", masteryScore: 81, questionsAnswered: 19 },
      { objectiveId: "obj-registration", title: "Aircraft Registration and Markings", masteryScore: 77, questionsAnswered: 15 },
      { objectiveId: "obj-airworthiness", title: "Airworthiness of Aircraft", masteryScore: 58, questionsAnswered: 12 },
      { objectiveId: "obj-altimeter", title: "Altimeter Setting Procedures", masteryScore: 49, questionsAnswered: 9 },
      { objectiveId: "obj-atc-services", title: "Air Traffic Control Services", masteryScore: 54, questionsAnswered: 11 },
      { objectiveId: "obj-radar", title: "Radar and Surveillance in ATC", masteryScore: 61, questionsAnswered: 8 },
      { objectiveId: "obj-alerting", title: "Alerting Service", masteryScore: 48, questionsAnswered: 6 },
    ],
  };
}
