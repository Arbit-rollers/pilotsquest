import { Button } from "@/components/ui/button";

export function StudySessionFooter({
  mode,
  canSubmit,
  onSubmit,
  onNext,
  submitting,
}: {
  mode: "answering" | "answered";
  canSubmit: boolean;
  onSubmit: () => void;
  onNext: () => void;
  submitting: boolean;
}) {
  return (
    <div className="sticky bottom-0 inset-x-0 border-t bg-background/95 backdrop-blur px-4 py-3 sm:static sm:border-0 sm:bg-transparent sm:px-0 sm:py-0">
      {mode === "answering" ? (
        <Button className="w-full min-h-11" disabled={!canSubmit || submitting} onClick={onSubmit}>
          {submitting ? "Submitting..." : "Submit"}
        </Button>
      ) : (
        <Button className="w-full min-h-11" onClick={onNext}>
          Next
        </Button>
      )}
    </div>
  );
}
