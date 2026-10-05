import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ImageOff } from "lucide-react";

export function ImageLoadingSkeleton() {
  return <Skeleton className="w-full aspect-video rounded-lg" aria-hidden="true" />;
}

export function ImageFailedState({ altText, onRetry }: { altText: string; onRetry: () => void }) {
  return (
    <div className="w-full aspect-video rounded-lg border border-dashed flex flex-col items-center justify-center gap-3 p-4 text-center">
      <ImageOff className="size-8 text-muted-foreground" aria-hidden="true" />
      <p className="text-sm text-muted-foreground max-w-sm">
        The required diagram could not be loaded. Your answer has not been scored yet.
      </p>
      <p className="sr-only">{altText}</p>
      <Button size="sm" variant="secondary" onClick={onRetry}>
        Retry
      </Button>
    </div>
  );
}
