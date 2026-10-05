import type { Metadata } from "next";
import { Geist, Geist_Mono, Saira_Condensed, Anton } from "next/font/google";
import "./globals.css";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Condensed, technical display face for headings — matches the badge logo's
// instrument-panel/HUD character across a full weight range so it stays
// readable at repeated UI sizes (card titles, section headers, nav labels).
const sairaCondensed = Saira_Condensed({
  variable: "--font-heading",
  subsets: ["latin"],
  weight: ["600", "700", "800"],
});

// Ultra-bold single-weight badge face reserved for the literal wordmark and
// rare hero moments (onboarding welcome, landing headline, level-up) — the
// closest free match to the logo's "PILOTS QUEST" lettering. Not used for
// repeated UI text; it's too heavy at small sizes.
const anton = Anton({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "PilotQuest",
  description: "Gamified, authority-specific aviation examination study platform.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // Dark ("Night Cockpit") is the brand's true expression, matching the
    // badge logo — hardcoded for now rather than wired through next-themes:
    // there's no toggle UI yet, and next-themes' flash-prevention script
    // relies on an inline <script> that this React 19 / Next 16 combo
    // deliberately no-ops for any script rendered by a component instead of
    // the raw SSR'd HTML (verified in react-dom's bundled source — it swaps
    // the node for an inert one unless it's an async/`src` resource script).
    // Revisit with a real light/dark toggle: either next-themes ships a fix,
    // or reimplement flash-prevention via next/script (strategy=
    // "beforeInteractive"), which Next.js exempts from this restriction.
    <html
      lang="en"
      data-scroll-behavior="smooth"
      className={`dark ${geistSans.variable} ${geistMono.variable} ${sairaCondensed.variable} ${anton.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <TooltipProvider>{children}</TooltipProvider>
        <Toaster theme="dark" />
      </body>
    </html>
  );
}
