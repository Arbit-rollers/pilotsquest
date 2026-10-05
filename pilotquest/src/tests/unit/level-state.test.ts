import { describe, it, expect } from "vitest";
import { LEVEL_STATE_VISUALS } from "@/lib/utils/level-state";
import type { LevelState } from "@/lib/types/progress";

const EXPECTED_STATES: readonly LevelState[] = [
  "locked",
  "available",
  "in_progress",
  "completed",
  "mastered",
  "needs_review",
  "updated",
  "temporarily_unavailable",
];

describe("level state visuals (PRD §10 — non-color-only status signaling)", () => {
  it("defines exactly the 8 PRD-specified LevelState values, no more, no fewer", () => {
    const keys = Object.keys(LEVEL_STATE_VISUALS).sort();
    expect(keys).toEqual([...EXPECTED_STATES].sort());
  });

  it("every state maps to a distinct icon component", () => {
    const icons = EXPECTED_STATES.map((s) => LEVEL_STATE_VISUALS[s].icon);
    const uniqueIcons = new Set(icons);
    expect(uniqueIcons.size).toBe(EXPECTED_STATES.length);
  });

  it("every state has a non-empty, distinct label", () => {
    const labels = EXPECTED_STATES.map((s) => LEVEL_STATE_VISUALS[s].label);
    expect(new Set(labels).size).toBe(EXPECTED_STATES.length);
    for (const label of labels) {
      expect(label.length).toBeGreaterThan(0);
    }
  });
});
