import { test, expect } from "@playwright/test";

test("study session: answer a question, see teaching feedback, advance", async ({ page }) => {
  await page.goto("/study/air-law-atc-services");

  await expect(page.getByText("EASA • ATPL(A)")).toBeVisible();

  // First choice button inside the answer choice list.
  const firstChoice = page.getByRole("radio").first();
  await firstChoice.click();

  await page.getByRole("radio", { name: "Confident", exact: true }).click();

  await page.getByRole("button", { name: "Submit" }).click();

  // Post-answer panel: correctness announced, jurisdiction banner present.
  await expect(page.getByText(/^(Correct|Incorrect)$/)).toBeVisible();
  await expect(page.getByText(/This explanation applies to/)).toBeVisible();

  await page.getByRole("button", { name: "Next", exact: true }).click();

  // Either the next question's progress indicator, or the completion screen.
  await expect(
    page.getByText(/\d+ \/ \d+/).or(page.getByRole("heading", { name: "Session complete" })),
  ).toBeVisible();
});
