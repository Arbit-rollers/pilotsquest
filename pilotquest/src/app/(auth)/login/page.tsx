import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BrandMark } from "@/components/layout/brand-mark";

/**
 * Step 1 has no real auth (PRD §163 is a later step). This stub lets the
 * core flows be exercised end-to-end without a login form.
 */
export default function AuthStubPage() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-8 px-6 py-16">
      <BrandMark size={48} wordmarkSize="lg" />
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Sign in</CardTitle>
          <CardDescription>
            Step 1 has no real authentication yet — continue as a demo student.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            render={<Link href="/onboarding">Continue as demo student</Link>}
            className="w-full"
          />
        </CardContent>
      </Card>
    </div>
  );
}
