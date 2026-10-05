import { test, expect } from "@playwright/test";

test("image viewer: zoom, fullscreen dialog with focus trap and Escape close", async ({ page }) => {
  await page.goto("/study/powerplant-images");

  const image = page.getByAltText(/Schematic cross-section of a gas-turbine engine/);
  await expect(image).toBeVisible();

  await page.getByRole("button", { name: "Zoom in" }).click();

  await page.getByRole("button", { name: "View fullscreen" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();

  // Focus trap: Tab should keep focus inside the dialog.
  await page.keyboard.press("Tab");
  const activeInsideDialog = await page.evaluate(() => {
    const dialogEl = document.querySelector('[role="dialog"]');
    return dialogEl?.contains(document.activeElement) ?? false;
  });
  expect(activeInsideDialog).toBe(true);

  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
});
