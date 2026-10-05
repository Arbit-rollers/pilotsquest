import { Flag } from "lucide-react";

export function CheckpointMarker() {
  return (
    <div className="flex items-center gap-2 my-1 text-xs text-muted-foreground" role="separator">
      <Flag className="size-3.5" aria-hidden="true" />
      Checkpoint
      <span className="flex-1 h-px bg-border" aria-hidden="true" />
    </div>
  );
}
