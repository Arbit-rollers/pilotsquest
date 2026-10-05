"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { ChartDataTable } from "./chart-data-table";
import type { AccuracyPoint } from "@/lib/types/progress";

export function AccuracyOverTimeChart({ points }: { points: readonly AccuracyPoint[] }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="h-56 w-full" role="img" aria-label="Accuracy over the last 7 days, chart">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points as AccuracyPoint[]} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="dateLabel" fontSize={12} tickLine={false} />
            <YAxis domain={[0, 100]} fontSize={12} tickLine={false} width={36} />
            <Tooltip />
            <Line type="monotone" dataKey="accuracyPct" stroke="var(--primary)" strokeWidth={2} dot />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <ChartDataTable
        caption="Accuracy over the last 7 days"
        columns={[
          { key: "dateLabel", label: "Day" },
          { key: "accuracyPct", label: "Accuracy (%)" },
        ]}
        rows={points as unknown as Record<string, string | number>[]}
      />
    </div>
  );
}
