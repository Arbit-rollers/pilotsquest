import { Info } from "lucide-react";

export function JurisdictionBanner({ notice }: { notice: string }) {
  return (
    <div className="flex items-start gap-2 rounded-md border bg-muted/50 px-3 py-2 text-xs text-muted-foreground">
      <Info className="size-4 shrink-0 mt-0.5" aria-hidden="true" />
      <p>
        This explanation applies to <strong>{notice}</strong> content. Rules in other authorities
        may differ.
      </p>
    </div>
  );
}
