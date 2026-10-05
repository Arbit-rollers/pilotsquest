import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ActivityItem } from "@/lib/types/progress";

export function RecentActivityFeed({ items }: { items: readonly ActivityItem[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Recent activity</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-3 text-sm">
          {items.map((item) => (
            <li key={item.id} className="flex items-center justify-between gap-3">
              <span>{item.label}</span>
              <span className="text-muted-foreground text-xs shrink-0">{item.timestampLabel}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
