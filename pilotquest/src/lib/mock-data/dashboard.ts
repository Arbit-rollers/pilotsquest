import type { DashboardSnapshot } from "@/lib/types/progress";
import type { AuthorityContext } from "@/lib/types/authority-context";

/**
 * Returns a mock dashboard snapshot. In Step 2/3 this becomes a real query
 * scoped by the user's AuthorityContext (PRD §7) — the function signature
 * is deliberately already shaped that way.
 */
export function getMockDashboardSnapshot(_context: AuthorityContext): DashboardSnapshot {
  return {
    continueLearning: {
      subjectId: "air-law",
      subjectName: "Air Law",
      levelId: "air-law-atc-services",
      progressPct: 62,
    },
    dailyGoal: { targetMinutes: 20, completedMinutes: 8 },
    streak: { days: 4, isActiveToday: false },
    xp: { level: 7, currentXp: 340, xpToNextLevel: 520 },
    reviewsDueCount: 5,
    weakObjectives: [
      { objectiveId: "obj-atc-services", title: "Air Traffic Control Services", masteryScore: 54, subjectName: "Air Law" },
      { objectiveId: "obj-radar", title: "Radar and Surveillance in ATC", masteryScore: 61, subjectName: "Air Law" },
      { objectiveId: "obj-alerting", title: "Alerting Service", masteryScore: 48, subjectName: "Air Law" },
    ],
    subjectMastery: [
      { subjectId: "air-law", subjectName: "Air Law", masteryScore: 68 },
      { subjectId: "powerplant", subjectName: "Powerplant", masteryScore: 41 },
    ],
    recentActivity: [
      { id: "act-1", label: "Completed level: Altimeter Setting Procedures", timestampLabel: "Yesterday" },
      { id: "act-2", label: "Passed 3 overdue reviews", timestampLabel: "Yesterday" },
      { id: "act-3", label: "Started: Air Traffic Control Services", timestampLabel: "2 days ago" },
    ],
  };
}
