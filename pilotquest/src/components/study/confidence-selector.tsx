"use client";

import { cn } from "@/lib/utils";

const LEVELS = [
  { value: 1, label: "Guessing" },
  { value: 2, label: "Unsure" },
  { value: 3, label: "Fairly sure" },
  { value: 4, label: "Confident" },
  { value: 5, label: "Very confident" },
] as const;

export function ConfidenceSelector({
  value,
  onChange,
  disabled,
}: {
  value: number | null;
  onChange: (value: 1 | 2 | 3 | 4 | 5) => void;
  disabled: boolean;
}) {
  return (
    <fieldset disabled={disabled}>
      <legend className="text-sm font-medium mb-2">How confident are you?</legend>
      <div role="radiogroup" className="flex flex-wrap gap-2">
        {LEVELS.map((level) => (
          <button
            key={level.value}
            type="button"
            role="radio"
            aria-checked={value === level.value}
            onClick={() => onChange(level.value)}
            className={cn(
              "min-h-11 rounded-full border px-3 text-xs font-medium transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              value === level.value
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border hover:border-primary/50",
              disabled && "opacity-60 cursor-not-allowed",
            )}
          >
            {level.label}
          </button>
        ))}
      </div>
    </fieldset>
  );
}
