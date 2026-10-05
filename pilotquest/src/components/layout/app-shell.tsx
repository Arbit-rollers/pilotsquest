"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Map, LineChart } from "lucide-react";
import { BrandMark } from "@/components/layout/brand-mark";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/learn", label: "Learn", icon: Map },
  { href: "/progress", label: "Progress", icon: LineChart },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex flex-1 min-h-0">
      {/* Desktop sidebar */}
      <nav
        aria-label="Primary"
        className="hidden md:flex md:w-56 md:flex-col md:border-r md:px-3 md:py-4 md:gap-1"
      >
        <div className="px-2 py-2 mb-2">
          <BrandMark size={28} wordmarkSize="sm" />
        </div>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname?.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive ? "page" : undefined}
              className={cn(
                "relative flex items-center gap-3 rounded-md px-3 py-2 text-sm min-h-11",
                isActive
                  ? "bg-primary/10 text-primary font-medium before:absolute before:inset-y-1.5 before:left-0 before:w-0.5 before:rounded-full before:bg-primary before:shadow-[0_0_8px_var(--color-primary)]"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground",
              )}
            >
              <Icon className="size-4" aria-hidden="true" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="flex flex-1 flex-col min-w-0">
        <main className="flex-1 min-w-0 pb-20 md:pb-0">{children}</main>

        {/* Mobile bottom tab bar */}
        <nav
          aria-label="Primary"
          className="md:hidden fixed bottom-0 inset-x-0 border-t bg-background flex items-stretch z-40"
        >
          {NAV_ITEMS.map((item) => {
            const isActive = pathname?.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "flex-1 flex flex-col items-center justify-center gap-1 py-2 min-h-11 text-xs",
                  isActive ? "text-primary font-medium" : "text-muted-foreground",
                )}
              >
                <Icon className="size-5" aria-hidden="true" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
