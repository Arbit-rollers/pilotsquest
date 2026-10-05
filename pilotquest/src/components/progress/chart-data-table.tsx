"use client";

import { useId, useState } from "react";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

/**
 * Generic accessible companion for any chart (PRD §151, §161): every
 * Recharts visualization on the progress pages must be paired with this so
 * the same data is available to screen readers / when JS chart rendering
 * fails, not only visually.
 */
export function ChartDataTable<T extends Record<string, string | number>>({
  caption,
  columns,
  rows,
}: {
  caption: string;
  columns: readonly { key: keyof T; label: string }[];
  rows: readonly T[];
}) {
  const [visible, setVisible] = useState(false);
  const id = useId();

  return (
    <div>
      <Button type="button" variant="link" size="sm" className="px-0" onClick={() => setVisible((v) => !v)} aria-expanded={visible} aria-controls={id}>
        {visible ? "Hide data table" : "View as table"}
      </Button>
      <div id={id} hidden={!visible} className="overflow-x-auto mt-2">
        <Table>
          <caption className="sr-only">{caption}</caption>
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead key={String(col.key)}>{col.label}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row, i) => (
              <TableRow key={i}>
                {columns.map((col) => (
                  <TableCell key={String(col.key)}>{row[col.key]}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
