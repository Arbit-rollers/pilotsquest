import { Button } from "@/components/ui/button";
import { ZoomIn, ZoomOut, RotateCcw, Maximize2 } from "lucide-react";

interface ImageViewerControlsProps {
  readonly onZoomIn: () => void;
  readonly onZoomOut: () => void;
  readonly onReset: () => void;
  readonly onFullscreen?: () => void;
}

/** Explicit keyboard/touch-operable controls — never wheel/pinch-only (WCAG). */
export function ImageViewerControls({ onZoomIn, onZoomOut, onReset, onFullscreen }: ImageViewerControlsProps) {
  return (
    <div className="flex items-center gap-1">
      <Button type="button" variant="secondary" size="icon" onClick={onZoomOut} aria-label="Zoom out">
        <ZoomOut className="size-4" />
      </Button>
      <Button type="button" variant="secondary" size="icon" onClick={onZoomIn} aria-label="Zoom in">
        <ZoomIn className="size-4" />
      </Button>
      <Button type="button" variant="secondary" size="icon" onClick={onReset} aria-label="Reset zoom">
        <RotateCcw className="size-4" />
      </Button>
      {onFullscreen ? (
        <Button type="button" variant="secondary" size="icon" onClick={onFullscreen} aria-label="View fullscreen">
          <Maximize2 className="size-4" />
        </Button>
      ) : null}
    </div>
  );
}
