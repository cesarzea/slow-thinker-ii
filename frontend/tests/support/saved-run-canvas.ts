import {expect} from '@playwright/test';
import type {Locator, Page} from '@playwright/test';

export async function expectSavedRunCanvas(
  page: Page,
  graphId: string,
  revision: string,
): Promise<void> {
  const live = page.getByRole('region', {name: 'Selected run graph'});
  await expect(live).toContainText(`Saved definition: ${graphId} · ${revision}`);
  const canvas = live.getByLabel('Agent collaboration canvas');
  await expect(canvas).toBeVisible();
  const proposer = canvas.locator('.react-flow__node[data-id="node:draft"]');
  await expect(proposer).toBeVisible();
  await expect(proposer.getByText('Proposer', {exact: true})).toBeVisible();
  await expect(proposer).toContainText('completed · 1 recorded activation');
  await expect(live.getByRole('status')).toHaveCount(0);
  await expect(live.getByText('Waiting for the saved definition.', {exact: true})).toHaveCount(0);
}

export async function openProposerCall(page: Page): Promise<Locator> {
  const events = page.getByRole('region', {name: 'Recorded events'});
  const rows = events.getByRole('row').filter({hasText: 'call.requested'});
  await expect(rows.first()).toBeVisible();
  for (const row of await rows.all()) {
    await row.getByRole('button', {name: /View call/u}).click();
    const call = page.getByRole('region', {name: 'Call details'});
    await expect(call.getByRole('button', {name: 'View arguments'})).toBeVisible();
    if ((await call.textContent())?.includes('proposer.generate') === true) return row;
  }
  throw new Error('No declared proposer.generate call was recorded.');
}
