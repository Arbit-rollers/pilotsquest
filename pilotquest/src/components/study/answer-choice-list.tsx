"use client";

import { cn } from "@/lib/utils";
import { CheckCircle2, XCircle } from "lucide-react";
import type { ChoiceOption, QuestionResultPayload } from "@/lib/types/question";

interface AnswerChoiceListProps {
  readonly choices: readonly ChoiceOption[];
  readonly selectedLabel: string | null;
  readonly onSelect: (label: string) => void;
  readonly disabled: boolean;
  readonly result?: QuestionResultPayload;
}

export function AnswerChoiceList({ choices, selectedLabel, onSelect, disabled, result }: AnswerChoiceListProps) {
  const correctLabels = result
    ? Array.isArray(result.correctAnswer)
      ? result.correctAnswer
      : [result.correctAnswer]
    : [];

  return (
    <div role="radiogroup" aria-label="Answer choices" className="flex flex-col gap-2">
      {choices.map((choice) => {
        const isSelected = selectedLabel === choice.label;
        const isCorrectChoice = result ? correctLabels.includes(choice.label) : false;
        const isWrongSelected = result ? isSelected && !isCorrectChoice : false;

        return (
          <button
            key={choice.label}
            type="button"
            role="radio"
            aria-checked={isSelected}
            disabled={disabled}
            onClick={() => onSelect(choice.label)}
            className={cn(
              "min-h-11 w-full text-left rounded-lg border px-4 py-3 flex items-center gap-3 transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              !result && isSelected && "border-primary bg-primary/5 ring-1 ring-primary",
              !result && !isSelected && "border-border hover:border-primary/50 hover:bg-accent/40",
              result && isCorrectChoice && "border-emerald-500 bg-emerald-50 dark:bg-emerald-950",
              result && isWrongSelected && "border-red-500 bg-red-50 dark:bg-red-950",
              result && !isCorrectChoice && !isWrongSelected && "border-border opacity-70",
              disabled && !result && "cursor-not-allowed opacity-60",
            )}
          >
            <span
              className="flex items-center justify-center size-6 rounded-full border text-xs font-medium shrink-0"
              aria-hidden="true"
            >
              {choice.label}
            </span>
            <span className="flex-1">{choice.text}</span>
            {result && isCorrectChoice ? (
              <CheckCircle2 className="size-5 text-emerald-600 dark:text-emerald-400 shrink-0" aria-hidden="true" />
            ) : null}
            {result && isWrongSelected ? (
              <XCircle className="size-5 text-red-600 dark:text-red-400 shrink-0" aria-hidden="true" />
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
