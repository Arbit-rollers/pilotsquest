"use client";

import { useState, useTransition } from "react";
import { Button } from "@/components/ui/button";
import { Bookmark } from "lucide-react";
import { toast } from "sonner";
import { toggleBookmark } from "@/lib/data-access/interactions";

export function BookmarkToggle({ questionId, initialBookmarked }: { questionId: string; initialBookmarked: boolean }) {
  const [bookmarked, setBookmarked] = useState(initialBookmarked);
  const [, startTransition] = useTransition();

  function handleClick() {
    const next = !bookmarked;
    setBookmarked(next); // optimistic
    startTransition(async () => {
      try {
        await toggleBookmark(questionId, next);
      } catch {
        setBookmarked(!next); // revert
        toast.error("Couldn't update bookmark. Try again.");
      }
    });
  }

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      aria-pressed={bookmarked}
      aria-label={bookmarked ? "Remove bookmark" : "Bookmark this question"}
      onClick={handleClick}
    >
      <Bookmark className={bookmarked ? "size-5 fill-current" : "size-5"} aria-hidden="true" />
    </Button>
  );
}
