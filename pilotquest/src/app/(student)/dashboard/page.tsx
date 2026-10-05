import { getAuthorityContext } from "@/lib/data-access/get-authority-context";
import { getDashboardSnapshot } from "@/lib/data-access/get-dashboard-snapshot";
import { AuthorityContextBadge } from "@/components/layout/authority-context-badge";
import { ContinueLearningCard } from "@/components/dashboard/continue-learning-card";
import { DailyGoalCard } from "@/components/dashboard/daily-goal-card";
import { StreakCard } from "@/components/dashboard/streak-card";
import { XpLevelCard } from "@/components/dashboard/xp-level-card";
import { ReviewsDueCard } from "@/components/dashboard/reviews-due-card";
import { WeakObjectivesList } from "@/components/dashboard/weak-objectives-list";
import { SubjectMasteryOverview } from "@/components/dashboard/subject-mastery-overview";
import { RecentActivityFeed } from "@/components/dashboard/recent-activity-feed";

export default async function DashboardPage() {
  const context = getAuthorityContext();
  const snapshot = await getDashboardSnapshot(context);

  return (
    <div className="px-4 sm:px-6 py-6 max-w-4xl mx-auto flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Dashboard</h1>
        <AuthorityContextBadge context={context} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <ContinueLearningCard continueLearning={snapshot.continueLearning} />
        <DailyGoalCard dailyGoal={snapshot.dailyGoal} />
        <StreakCard streak={snapshot.streak} />
        <XpLevelCard xp={snapshot.xp} />
        <ReviewsDueCard reviewsDueCount={snapshot.reviewsDueCount} />
      </div>

      <WeakObjectivesList objectives={snapshot.weakObjectives} />
      <SubjectMasteryOverview subjects={snapshot.subjectMastery} />
      <RecentActivityFeed items={snapshot.recentActivity} />
    </div>
  );
}
