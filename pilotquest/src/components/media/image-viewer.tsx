"use client";

import { useReducer, useRef, useCallback, useState } from "react";
import Image from "next/image";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { ImageViewerControls } from "./image-viewer-controls";
import { AnnotationOverlay } from "./annotation-overlay";
import { ImageLoadingSkeleton, ImageFailedState } from "./image-loading-state";
import type { QuestionImageAsset, NormalizedAnnotation } from "@/lib/types/media";

interface ImageViewerState {
  status: "loading-thumbnail" | "loading-fullres" | "ready" | "failed";
  scale: number;
  translate: { x: number; y: number };
}

type Action =
  | { type: "fullres-loaded" }
  | { type: "load-failed" }
  | { type: "retry" }
  | { type: "zoom"; delta: number }
  | { type: "pan"; dx: number; dy: number }
  | { type: "reset" };

const MIN_SCALE = 1;
const MAX_SCALE = 4;

function reducer(state: ImageViewerState, action: Action): ImageViewerState {
  switch (action.type) {
    case "fullres-loaded":
      return { ...state, status: "ready" };
    case "load-failed":
      return { ...state, status: "failed" };
    case "retry":
      return { status: "loading-thumbnail", scale: 1, translate: { x: 0, y: 0 } };
    case "zoom": {
      const nextScale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, state.scale + action.delta));
      return { ...state, scale: nextScale, translate: nextScale === 1 ? { x: 0, y: 0 } : state.translate };
    }
    case "pan":
      return { ...state, translate: { x: state.translate.x + action.dx, y: state.translate.y + action.dy } };
    case "reset":
      return { ...state, scale: 1, translate: { x: 0, y: 0 } };
    default:
      return state;
  }
}

function ViewerSurface({
  image,
  revealedAnnotations,
  state,
  dispatch,
  onPointerDown,
}: {
  image: QuestionImageAsset;
  revealedAnnotations: readonly NormalizedAnnotation[];
  state: ImageViewerState;
  dispatch: React.Dispatch<Action>;
  onPointerDown: (e: React.PointerEvent) => void;
}) {
  const allAnnotations = [...(image.annotations ?? []), ...revealedAnnotations];

  return (
    <div className="relative w-full aspect-video overflow-hidden rounded-lg border bg-muted touch-pinch-zoom">
      {state.status === "loading-thumbnail" ? (
        <>
          {/* thumbnail shown immediately while full-res loads in the background */}
          <Image
            src={image.thumbnailUrl}
            alt=""
            fill
            className="object-contain blur-sm"
            aria-hidden="true"
            unoptimized
          />
          <Image
            src={image.fullResUrl}
            alt={image.altText}
            fill
            className="object-contain opacity-0"
            unoptimized
            onLoad={() => dispatch({ type: "fullres-loaded" })}
            onError={() => dispatch({ type: "load-failed" })}
          />
        </>
      ) : state.status === "failed" ? (
        <ImageFailedState altText={image.altText} onRetry={() => dispatch({ type: "retry" })} />
      ) : (
        <div
          className="relative w-full h-full motion-safe:transition-transform"
          style={{
            transform: `scale(${state.scale}) translate(${state.translate.x}px, ${state.translate.y}px)`,
          }}
          onPointerDown={onPointerDown}
        >
          <Image src={image.fullResUrl} alt={image.altText} fill className="object-contain" unoptimized />
          <AnnotationOverlay annotations={allAnnotations} />
        </div>
      )}
    </div>
  );
}

export function ImageViewer({
  image,
  revealedAnnotations = [],
}: {
  image: QuestionImageAsset;
  revealedAnnotations?: readonly NormalizedAnnotation[];
}) {
  const [state, dispatch] = useReducer(reducer, {
    status: "loading-thumbnail",
    scale: 1,
    translate: { x: 0, y: 0 },
  });
  const [fullscreenOpen, setFullscreenOpen] = useState(false);
  const dragOrigin = useRef<{ x: number; y: number } | null>(null);

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    dragOrigin.current = { x: e.clientX, y: e.clientY };
    const target = e.currentTarget as HTMLElement;

    function handleMove(moveEvent: PointerEvent) {
      if (!dragOrigin.current) return;
      const dx = moveEvent.clientX - dragOrigin.current.x;
      const dy = moveEvent.clientY - dragOrigin.current.y;
      dragOrigin.current = { x: moveEvent.clientX, y: moveEvent.clientY };
      dispatch({ type: "pan", dx, dy });
    }
    function handleUp() {
      dragOrigin.current = null;
      window.removeEventListener("pointermove", handleMove);
      window.removeEventListener("pointerup", handleUp);
    }
    window.addEventListener("pointermove", handleMove);
    window.addEventListener("pointerup", handleUp);
    void target;
  }, []);

  return (
    <div className="flex flex-col gap-2">
      <ViewerSurface
        image={image}
        revealedAnnotations={revealedAnnotations}
        state={state}
        dispatch={dispatch}
        onPointerDown={handlePointerDown}
      />
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">{image.altText}</p>
        <ImageViewerControls
          onZoomIn={() => dispatch({ type: "zoom", delta: 0.5 })}
          onZoomOut={() => dispatch({ type: "zoom", delta: -0.5 })}
          onReset={() => dispatch({ type: "reset" })}
          onFullscreen={() => setFullscreenOpen(true)}
        />
      </div>

      <Dialog open={fullscreenOpen} onOpenChange={setFullscreenOpen}>
        <DialogContent className="max-w-5xl w-[95vw] h-[90vh] flex flex-col">
          <DialogTitle className="sr-only">{image.altText}</DialogTitle>
          <div className="flex-1 min-h-0">
            <ViewerSurface
              image={image}
              revealedAnnotations={revealedAnnotations}
              state={state}
              dispatch={dispatch}
              onPointerDown={handlePointerDown}
            />
          </div>
          <ImageViewerControls
            onZoomIn={() => dispatch({ type: "zoom", delta: 0.5 })}
            onZoomOut={() => dispatch({ type: "zoom", delta: -0.5 })}
            onReset={() => dispatch({ type: "reset" })}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}

export { ImageLoadingSkeleton };
