"use client";

import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

/**
 * Scratchpad contents are never submitted as the answer (PRD §64) — only
 * the separate numeric answer field below is sent via onAnswerChange.
 */
export function ScratchpadPanel({
  scratchpad,
  onScratchpadChange,
  answer,
  onAnswerChange,
  disabled,
}: {
  scratchpad: string;
  onScratchpadChange: (value: string) => void;
  answer: string;
  onAnswerChange: (value: string) => void;
  disabled: boolean;
}) {
  return (
    <div className="flex flex-col gap-4">
      <div>
        <div className="flex items-center justify-between mb-1">
          <Label htmlFor="scratchpad">Scratchpad</Label>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onScratchpadChange("")}
            disabled={disabled}
          >
            Clear
          </Button>
        </div>
        <Textarea
          id="scratchpad"
          value={scratchpad}
          onChange={(e) => onScratchpadChange(e.target.value)}
          disabled={disabled}
          placeholder="Work through the calculation here..."
          className="font-mono min-h-32"
          inputMode="decimal"
        />
      </div>
      <div>
        <Label htmlFor="numeric-answer">Your answer</Label>
        <Input
          id="numeric-answer"
          value={answer}
          onChange={(e) => onAnswerChange(e.target.value)}
          disabled={disabled}
          inputMode="decimal"
          placeholder="Enter your final numeric answer"
          className="mt-1"
        />
      </div>
    </div>
  );
}
