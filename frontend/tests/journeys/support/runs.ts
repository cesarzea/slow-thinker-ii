import {expect, type Locator, type Page} from '@playwright/test';

export function runPanel(page: Page): Locator {
  return page.getByRole('complementary', {name: 'Run'});
}

/** Run mode, then Execute with the message: the run shows in place, in the same editor. */
export async function runGraph(page: Page, message: string): Promise<void> {
  await page.getByRole('button', {name: 'Run', exact: true}).click();
  await expect(page.getByRole('navigation', {name: 'Observation points'})).toBeVisible();
  await runPanel(page).getByRole('textbox', {name: 'Message'}).fill(message);
  await runPanel(page).getByRole('button', {name: 'Execute'}).click();
  await expect(page).toHaveURL(/#\/graphs\/[^/]+\/runs\/[^/]+$/u);
}

export async function expectStatus(page: Page, status: string | RegExp): Promise<void> {
  await expect(runPanel(page).getByText(status).first()).toBeVisible({timeout: 30_000});
}

/** The message that reached an Output, among the observed connections' messages. */
export async function expectResult(page: Page, output: string, text: string): Promise<void> {
  const delivered = runPanel(page)
    .getByRole('listitem')
    .filter({hasText: `→ ${output}`});
  await expect(delivered.first()).toContainText(text);
}

/** The run's activity, opened from its address. */
export async function openActivity(page: Page): Promise<void> {
  await page.goto(`${page.url()}/activity`);
  await expect(page.getByRole('heading', {name: 'Activity'})).toBeVisible();
}
