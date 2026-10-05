"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Flag } from "lucide-react";
import { toast } from "sonner";
import { reportQuestion, type ReportCategory } from "@/lib/data-access/interactions";

const CATEGORIES: readonly { value: ReportCategory; label: string }[] = [
  { value: "wrong_answer", label: "Suspected wrong answer" },
  { value: "outdated_regulation", label: "Outdated regulation" },
  { value: "ambiguous_wording", label: "Ambiguous wording" },
  { value: "incorrect_explanation", label: "Incorrect explanation" },
  { value: "image_problem", label: "Image problem" },
  { value: "copyright_concern", label: "Copyright concern" },
  { value: "accessibility_problem", label: "Accessibility problem" },
  { value: "formatting_problem", label: "Formatting problem" },
  { value: "other", label: "Other" },
];

export function ReportQuestionDialog({ questionId }: { questionId: string }) {
  const [open, setOpen] = useState(false);
  const [category, setCategory] = useState<ReportCategory | "">("");
  const [details, setDetails] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit() {
    if (!category) return;
    setSubmitting(true);
    try {
      await reportQuestion(questionId, category, details);
      toast.success("Thanks — this has been reported for review.");
      setOpen(false);
      setCategory("");
      setDetails("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <Button type="button" variant="ghost" size="icon" aria-label="Report this question">
            <Flag className="size-5" aria-hidden="true" />
          </Button>
        }
      />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Report this question</DialogTitle>
          <DialogDescription>Help us keep the question bank accurate and current.</DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-4">
          <div>
            <Label htmlFor="report-category">Category</Label>
            <Select value={category} onValueChange={(v) => setCategory(v as ReportCategory)}>
              <SelectTrigger id="report-category" className="mt-1 w-full">
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map((c) => (
                  <SelectItem key={c.value} value={c.value}>
                    {c.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="report-details">Details (optional)</Label>
            <Textarea
              id="report-details"
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              className="mt-1"
              placeholder="What did you notice?"
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="button" onClick={handleSubmit} disabled={!category || submitting}>
            Submit report
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
