import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RotateCcw } from "lucide-react";

export function ReviewsDueCard({ reviewsDueCount }: { reviewsDueCount: number }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <RotateCcw className="size-4" aria-hidden="true" />
          Reviews due
        </CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-between">
        <p className="text-2xl font-bold">{reviewsDueCount}</p>
        {reviewsDueCount > 0 ? (
          <Button
            render={<Link href="/study/air-law-review">Review now</Link>}
            variant="secondary"
            size="sm"
          />
        ) : (
          <p className="text-sm text-muted-foreground">You&apos;re current.</p>
        )}
      </CardContent>
    </Card>
  );
}
