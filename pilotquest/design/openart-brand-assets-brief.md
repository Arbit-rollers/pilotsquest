# PilotQuest — Brand Asset Generation Brief (for Claude + OpenArt MCP)

## How to use this document

You are being given this brief inside a Claude session that has the **OpenArt MCP** connected. Your job is to generate a complete set of brand/illustration assets for an app called **PilotQuest** using the OpenArt tools available to you (image generation, model listing, creation management, projects, uploads).

Work through the asset list below **in order**. For each asset:

1. Re-read its brief (purpose, content, style, technical spec, negative constraints).
2. If you're unsure which OpenArt model fits best, check the model list and pick one suited to **flat/semi-flat modern illustration** for illustrations and icons, or a **clean vector/logo-capable** model for the icon/logomark — avoid photorealistic models for anything in this brief.
3. Check the model's cost before generating, and if a single asset would require an unusually expensive model or many credits, pause and confirm with the user before proceeding rather than spending silently.
4. Generate **3–4 variations** per asset so the user has a real choice, not just one result.
5. Group everything under one OpenArt project named **"PilotQuest Brand Assets"** if a project-creation tool is available, so the user can find everything in one place afterward.
6. When you finish each asset (or the whole batch, your judgment), give the user a short summary: what was generated, links/IDs to each result, and which variant you'd personally pick and why.

Do not invent additional assets beyond this list without asking first. Do not skip the negative constraints — several of them exist for legal/trademark reasons specific to this project (see "Hard constraints" below), not just style preference.

---

## 1. Project context

**PilotQuest** is a mobile-first, gamified web app that helps student pilots study for aviation theory exams (EASA, FAA, UK CAA, Transport Canada, and other authorities). It combines a structured syllabus-based learning path with game-style progression (XP, levels, streaks, mastery tracking) — but it is deliberately **not** a cartoonish or juvenile product. Its users are adults training for a professional/technical qualification, so the tone should read as **competent, modern, and trustworthy**, with just enough warmth and game-feel to stay motivating.

Think: the visual register of a well-designed flight-planning or aviation-weather app (ForeFlight, Sky Guru) crossed with the friendliness of a modern learning app (Duolingo's warmth, but far less cartoonish; Notion/Linear's clean geometric illustration style).

## 2. Brand identity reference

### Colors

Use these as the actual palette — don't substitute generic "aviation blue" without matching these:

| Role | Light mode | Dark mode | Notes |
|---|---|---|---|
| Primary (aviation blue) | `#2F6FE0` (vivid sky/cobalt blue) | `#5FA8E8` (brighter, glows on dark) | Main brand color — buttons, links, primary icon fills |
| Accent (brass/amber) | `#E8B84D` (warm gold/amber) | `#DEC06E` (softer gold) | Used **only** for gamification/achievement moments (XP, streaks, "mastered" badges) — don't use it as a general accent |
| Background (light) | `#F7FAFD` (near-white, faint blue tint) | — | |
| Background (dark) | — | `#151E2C` (deep navy, not pure black) | "Night-flight cockpit" feel |
| Foreground/ink | `#1E2A3D` (deep navy-charcoal) | `#F2F5F8` (near-white) | |
| Success | `#10B981` (emerald) | same family | |
| Warning/needs-review | `#D97706` (amber-orange) | same family | |

If a model only accepts a short palette, prioritize: **cobalt blue + warm gold + near-white/deep-navy neutrals**. Avoid introducing unrelated hues (no purple, no pink, no bright red except sparingly for error states) unless a specific asset below calls for chart-style variety.

### Typography (for any asset with text baked in — see constraints, this should be rare)

- Headings: **Space Grotesk** (geometric, modern, slightly technical/engineered feel)
- Body: **Geist Sans**

### Overall style direction

- **Flat or semi-flat modern illustration** — clean geometric shapes, limited gradients used purposefully (e.g. sky gradients), confident linework, generous negative space.
- Reference points: modern SaaS/fintech illustration systems (Linear, Stripe, Notion), aviation instrument/HUD line-art motifs (attitude indicators, compass roses, altimeter dials) used as **abstract graphic elements**, not literal cockpit photos.
- **No photorealism.** No 3D-rendered/glossy "AI app icon" clichés (no glassy orbs, no generic rocket-ship gradients).
- **No text baked into images** unless an asset explicitly says otherwise — all UI text is real HTML/CSS in the app, not part of the image.

## 3. Hard constraints (apply to every asset)

- **No real airline branding.** No recognizable liveries, tail logos, or airline names (no Emirates/Delta/Ryanair/etc. styling).
- **No real aviation authority logos or insignia.** Do not attempt to reproduce the EASA, FAA, UK CAA, Transport Canada, or ICAO logos/seals — even stylized. Generic aviation iconography (compass, wings, altimeter, control tower silhouette) is fine; official trademarked insignia is not.
- **No real aircraft registration numbers or tail numbers** that could resemble an actual in-service aircraft.
- **No identifiable real people's faces.** If a human figure appears (e.g. a pilot silhouette), keep it generic/anonymized — silhouette, back-view, or simplified illustrated figure, not a realistic rendered face.
- **No cockpit instrument readings depicted as if accurate/real data** (e.g. a specific altimeter reading, a specific METAR) — these are decorative/abstract only, never presented as real flight data, to avoid any confusion with the app's actual (accuracy-critical) study content.
- Every asset must work correctly in **both light and dark mode** contexts described above — either provide a version tuned for each, or generate on a transparent background so it composites cleanly onto both.

---

## 4. Asset list

### 4.1 App icon / logomark

**Purpose:** Browser favicon, PWA home-screen icon, and the small brand mark used in the app's navigation bar (currently a placeholder generic airplane icon in a blue rounded square).

**Content direction:** A simple, bold, **single-color-friendly** logomark that reads clearly at 16×16px. Options to explore:
- A stylized paper-airplane or jet silhouette merged subtly with a compass needle or upward flight-path arc.
- A monogram-style "P" or "PQ" integrated with a wing or flight-path swoosh.
- Avoid anything that needs fine detail to read — this must work as a tiny favicon.

**Style:** Flat, geometric, 2–3 colors max (primary blue + white, optionally + amber accent as a small detail). Bold enough silhouette that it still reads correctly as a solid single-color mark.

**Technical spec:**
- Square canvas, generate at **1024×1024**.
- One version with a solid primary-blue rounded-square background (for the app icon / PWA tile).
- One version as the mark alone on a **transparent background** (for use inline in the nav bar at small sizes).
- One "maskable" consideration: keep the core mark within the center ~70% of the canvas (safe zone) so it isn't clipped when the OS applies its own icon mask shape.

**Negative constraints:** No photorealistic metal/glass textures. No drop shadows or bevels — flat design only. No text/letters unless it's a simple monogram per the direction above.

---

### 4.2 Landing page hero illustration

**Purpose:** Sits behind/beside the headline on the marketing landing page ("Study for your aviation exam, one authority at a time."). Currently the page only has a CSS gradient with no illustration — this fills that gap.

**Content direction:** An aircraft (generic single-engine or small jet silhouette, not a specific real model/livery) climbing through a stylized sky, with a subtle abstract overlay of instrument/HUD line-art (a faint compass rose, altitude ticks, or a flight-path arc) — evoking "structured progress" rather than literal cockpit photography. Should feel optimistic and forward-moving (climbing/ascending composition, left-to-right or lower-left-to-upper-right motion).

**Style:** Semi-flat illustration with a soft gradient sky (blue fading toward the page's near-white background) and a warm amber accent used sparingly (e.g. a sunrise glow or a single highlight line) — echoes the CSS gradient blobs already in the page (soft blue + amber glow).

**Technical spec:**
- **Landscape**, roughly **16:9** to **2:1** aspect ratio (this needs to sit in a wide hero band).
- Generate on a **transparent background** if the model supports it, so it can be layered over the existing CSS gradient; if not possible, generate with a background that closely matches `#F7FAFD` fading to transparent-feeling white at the edges so it blends.
- Also generate a **dark-mode variant** (same composition, deep navy `#151E2C` background instead of near-white) for when the site is viewed in dark mode.
- Keep the **left/center area relatively uncluttered** — that's where the headline text sits on desktop; put the strongest visual interest toward the right side or as a full-width background wash.

**Negative constraints:** No visible cockpit interior/dashboard (avoid implying a specific instrument reading is "real" — see hard constraints). No visible airline branding on the aircraft.

---

### 4.3 Onboarding illustration (single welcome image)

**Purpose:** Shown on the onboarding welcome screen ("Let's set up your study context") before the user picks their authority/licence/aircraft category/goal.

**Content direction:** A friendly, simple illustration conveying "choosing your path" — e.g. a compass with multiple flight-path lines branching from it toward different directions, or a simplified world/globe outline with a few small aircraft-path arcs converging toward one highlighted route. Should feel like "many options, but you're picking yours" — supporting the app's core promise that your chosen authority/licence stays isolated and specific to you.

**Style:** Flat illustration, centered composition, works well in a fairly small/contained space (this sits above a headline in a narrow centered column, not full-width).

**Technical spec:**
- Roughly **square to 4:3** aspect ratio, moderate size (this is a supporting image, not a hero).
- Transparent background.
- Provide both a light-mode-friendly version (darker line work) and confirm it also reads fine on dark backgrounds, or provide a light-line dark-mode variant.

**Negative constraints:** No real country flags used to represent authorities (EASA = EU-wide, not a single country) — keep it abstract (compass/paths/globe outline), not flag icons.

---

### 4.4 Empty-state illustrations (set of 4)

**Purpose:** Shown in place of content when there's genuinely nothing to display. Each needs a distinct, appropriately-toned mood — these should feel calm/positive, not like errors.

Generate all four as **one consistent illustration family** (same line weight, same limited palette, same flat style) so they feel like a matched set:

1. **"You're all caught up" (no reviews due)** — Something calm and settled: e.g. a compass at rest, or a small aircraft parked/at ease on a runway under a calm sky. Tone: relaxed, positive, "nothing to do right now, well done."
2. **"Nothing available yet" (no mock exam / no image questions available for this objective)** — Something in a gentle "waiting/paused" state: e.g. a runway with a "hold short" style marking rendered abstractly, or an hourglass-with-wings motif. Tone: neutral, not alarming — this is a normal state, not an error.
3. **"Session complete"** — A small celebratory moment: e.g. a paper airplane or small aircraft completing a loop/banner-pull, or a compass needle landing precisely on a checkmark. Tone: rewarding but understated (not confetti-cannon over-the-top).
4. **404 / page not found** — Something "off course": e.g. a compass needle spinning, or a paper airplane that's veered off a dotted flight path. Tone: light, a little playful, not embarrassing or harsh.

**Style:** Flat illustration, single consistent line weight, primary blue as the main linework color with amber used only in illustration #3 (the celebratory one) as an accent — keep #1, #2, and #4 restrained to blue/neutral tones so amber stays special-feeling.

**Technical spec:**
- Roughly **square (1:1)** each, transparent background.
- Small-to-medium display size in the app (centered in a content area, not full-bleed) — keep compositions simple enough to still read at ~200×200px.

**Negative constraints:** Illustration #4 (404) should feel light and reassuring, not stressful — no crash/wreckage imagery of any kind (this is a safety-sensitive subject matter app; a "plane crash" visual metaphor for a 404 page would be tone-deaf and must be avoided entirely).

---

### 4.5 Achievement badge icon system

**Purpose:** Circular medallion-style icons for the achievements/badges feature (planned, not yet built in the app UI, but needed ahead of that work). Each achievement needs its own icon within one consistent badge "frame" system.

**Step A — establish the badge frame (generate once):** A circular medallion frame/border design — think a clean, modern "challenge coin" outline, NOT an ornate/gaudy trophy-shop medal. Simple ring, primary-blue or amber ring accents, flat design, with an empty center where a subject-specific icon will go.

**Step B — generate the 8 subject icons**, each simple enough to sit inside that same medallion frame, one flat-line icon per achievement:

| Achievement | Icon concept |
|---|---|
| First Flight (complete first level) | A single small aircraft silhouette, simple takeoff angle |
| Circuit Complete (complete first chapter) | A closed-loop flight-path line forming a simple circuit pattern |
| Recall Ready (pass 10 delayed reviews) | A clock/hourglass merged with a checkmark |
| Systems Specialist (master a systems objective set) | A simple gear/cog merged with a small wing |
| Regulation Current (complete all update missions) | A shield or document icon with a checkmark |
| Picture Perfect (50 correct image questions) | A simple framed-picture/viewfinder icon |
| Comeback (recover 5 weak objectives) | An upward-trending arrow or a compass needle correcting direction |
| Exam Endurance (complete a timed subject mock) | A stopwatch/timer icon with a small wing |

**Style:** All 8 icons must share identical line weight, size, and color treatment (primary blue linework, on a light neutral badge-face color) so they look like one family when placed side by side — generate them as a set/batch referencing the same style description, not independently.

**Technical spec:**
- Each badge: **square, 1024×1024**, the circular medallion centered with a small margin, transparent background outside the circle.
- Deliver as 8 separate images (or one contact-sheet image showing all 8 together for review, if that's easier to generate first, followed by the 8 individual final versions).

**Negative constraints:** No literal trophy/gold-cup imagery (too generic/cliché for this brand). No real medal ribbon designs. Keep every icon abstract/simplified — these must read clearly at ~48×48px in the actual app UI.

---

## 5. Delivery checklist

When you're done, confirm you've produced:

- [ ] App icon — solid-background version + transparent mark-only version
- [ ] Landing hero illustration — light-mode + dark-mode variants
- [ ] Onboarding welcome illustration
- [ ] 4 empty-state illustrations (caught-up / nothing-available / session-complete / 404), as one visual family
- [ ] Achievement badge frame + 8 subject icons, as one visual family

For each, give the user: a preview/link, which model you used, and your top-pick variant. Flag anything where you had to deviate from this brief (e.g. a model refused a concept, or a negative constraint couldn't be verified) rather than silently substituting something else.
