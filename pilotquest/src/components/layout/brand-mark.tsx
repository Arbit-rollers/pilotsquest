import Image from "next/image";
import { cn } from "@/lib/utils";

const WORDMARK_SIZE = {
  sm: "text-sm",
  md: "text-lg",
  lg: "text-2xl sm:text-3xl",
} as const;

export function BrandMark({
  size = 32,
  withWordmark = true,
  wordmarkSize = "md",
  glow = true,
  className,
}: {
  /** Badge diameter in px. */
  size?: number;
  withWordmark?: boolean;
  wordmarkSize?: keyof typeof WORDMARK_SIZE;
  /** Neon rim-light behind the badge, matching the logo's glow. */
  glow?: boolean;
  className?: string;
}) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <Image
        src="/brand/logo.png"
        alt="PilotsQuest"
        width={size}
        height={size}
        priority
        className={cn("shrink-0 rounded-full", glow && "glow-primary")}
      />
      {withWordmark ? (
        <span
          className={cn(
            "font-display leading-none tracking-wide text-foreground",
            WORDMARK_SIZE[wordmarkSize],
          )}
        >
          PILOTS<span className="text-primary">QUEST</span>
        </span>
      ) : null}
    </span>
  );
}
