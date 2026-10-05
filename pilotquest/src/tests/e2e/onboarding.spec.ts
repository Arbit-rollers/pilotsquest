import { test, expect } from "@playwright/test";

test("onboarding: authority -> licence -> aircraft category -> goal -> dashboard", async ({ page }) => {
  await page.goto("/onboarding");
  await page.getByRole("button", { name: "Begin" }).click();

  await expect(page).toHaveURL(/\/onboarding\/authority/);
  await page.getByRole("button", { name: /EASA/ }).click();
  await page.getByRole("button", { name: "Continue" }).click();

  await expect(page).toHaveURL(/\/onboarding\/licence/);
  await page.getByRole("button", { name: /ATPL\(A\)/ }).click();
  await page.getByRole("button", { name: "Continue" }).click();

  await expect(page).toHaveURL(/\/onboarding\/aircraft-category/);
  await page.getByRole("button", { name: /Aeroplane/ }).click();
  await page.getByRole("button", { name: "Continue" }).click();

  await expect(page).toHaveURL(/\/onboarding\/goal/);
  await page.getByRole("button", { name: /Standard/ }).click();
  await page.getByRole("button", { name: "Go to dashboard" }).click();

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("EASA • ATPL(A)")).toBeVisible();
});
