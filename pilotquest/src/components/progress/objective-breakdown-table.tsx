import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { ObjectiveBreakdown } from "@/lib/types/progress";

export function ObjectiveBreakdownTable({ objectives }: { objectives: readonly ObjectiveBreakdown[] }) {
  return (
    <div className="overflow-x-auto">
      <Table>
        <caption className="sr-only">Mastery by learning objective</caption>
        <TableHeader>
          <TableRow>
            <TableHead>Objective</TableHead>
            <TableHead className="text-right">Mastery</TableHead>
            <TableHead className="text-right">Questions answered</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {objectives.map((obj) => (
            <TableRow key={obj.objectiveId}>
              <TableCell className="font-medium">{obj.title}</TableCell>
              <TableCell className="text-right tabular-nums">{obj.masteryScore}%</TableCell>
              <TableCell className="text-right tabular-nums">{obj.questionsAnswered}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
