/**
 * The exact 8-value enum from PRD §10. Do not invent different state
 * names or add/remove values — lib/utils/level-state.ts and
 * tests/unit/level-state.test.ts both depend on this exact set.
 */
export type LevelState =
  | "locked"
  | "available"
  | "in_progress"
  | "completed"
  | "mastered"
  | "needs_review"
  | "updated"
  | "temporarily_unavailable";

export interface LevelNode {
  readonly id: string;
  readonly title: string;
  readonly state: LevelState;
  readonly checkpointAfter?: boolean;
  readonly lockExplanation?: string;
}

export interface SubjectLearningMap {
  readonly subjectId: string;
  readonly subjectName: string;
  readonly levels: readonly LevelNode[];
}

export interface SubjectMasterySummary {
  readonly subjectId: string;
  readonly subjectName: string;
  readonly masteryScore: number; // 0-100
}

export interface WeakObjective {
  readonly objectiveId: string;
  readonly title: string;
  readonly masteryScore: number;
  readonly subjectName: string;
}

export interface ActivityItem {
  readonly id: string;
  readonly label: string;
  readonly timestampLabel: string; // pre-formatted for mock simplicity
}

export interface DashboardSnapshot {
  readonly continueLearning: {
    readonly subjectId: string;
    readonly subjectName: string;
    readonly levelId: string;
    readonly progressPct: number;
  };
  readonly dailyGoal: { readonly targetMinutes: number; readonly completedMinutes: number };
  readonly streak: { readonly days: number; readonly isActiveToday: boolean };
  readonly xp: { readonly level: number; readonly currentXp: number; readonly xpToNextLevel: number };
  readonly reviewsDueCount: number;
  readonly weakObjectives: readonly WeakObjective[];
  readonly subjectMastery: readonly SubjectMasterySummary[];
  readonly recentActivity: readonly ActivityItem[];
}

export interface AccuracyPoint {
  readonly dateLabel: string;
  readonly accuracyPct: number;
}

export interface ObjectiveBreakdown {
  readonly objectiveId: string;
  readonly title: string;
  readonly masteryScore: number;
  readonly questionsAnswered: number;
}

export interface ProgressOverview {
  readonly subjectMastery: readonly SubjectMasterySummary[];
  readonly accuracyOverTime: readonly AccuracyPoint[];
  readonly objectiveBreakdown: readonly ObjectiveBreakdown[];
}
