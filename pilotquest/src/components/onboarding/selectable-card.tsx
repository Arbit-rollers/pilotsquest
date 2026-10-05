"use client";

import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

interface SelectableCardProps {
  readonly label: string;
  readonly description: string;
  readonly selected: boolean;
  readonly onSelect: () => void;
}

/** Min 44x44 touch target, keyboard-operable, aria-pressed (PRD §159-161). */
export function SelectableCard({ label, description, selected, onSelect }: SelectableCardProps) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
      className={cn(
        "w-full min-h-11 text-left rounded-lg border p-4 flex items-start justify-between gap-3 transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        selected
          ? "border-primary bg-primary/5 ring-1 ring-primary"
          : "border-border hover:border-primary/50 hover:bg-accent/40",
      )}
    >
      <span>
        <span className="block font-medium">{label}</span>
        <span className="block text-sm text-muted-foreground">{description}</span>
      </span>
      {selected ? <Check className="size-5 text-primary shrink-0" aria-hidden="true" /> : null}
    </button>
  );
}
