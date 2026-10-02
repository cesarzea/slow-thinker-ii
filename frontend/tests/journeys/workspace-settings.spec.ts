import {expect, test} from '@playwright/test';
import type {Page} from '@playwright/test';
import {z} from 'zod';
import {connect, operatorRequest} from '../support/browser.ts';
import {workspacePage} from '../support/browser-workspace.ts';
test('enforces server ceilings and recovers a committed settings command with identical bytes', async ({
  page,
}) => {
  await connect(page);
  await workspacePage(page, 'Settings');
  const run = page.getByRole('textbox', {name: /Run deadline \(seconds\)/u});
  await run.fill('31');
  await apply(page);
  await expect(page.getByText(/invalid_limits/u)).toBeVisible();
  await expect(page.getByRole('button', {name: 'Replay unchanged settings command'})).toHaveCount(
    0,
  );
  const bodies = await lostSettingsReply(page);
  await run.fill('22.5');
  await apply(page);
  await expect(page.getByText(/Configuration update unconfirmed/u)).toBeVisible();
  await expect(run).toBeDisabled();
  await workspacePage(page, 'Experiments');
  await workspacePage(page, 'Settings');
  await expect(run).toBeDisabled();
  await page.getByRole('button', {name: 'Replay unchanged settings command'}).click();
  await expect(page.getByText(/Settings confirmed under revision/u)).toBeVisible();
  expect(bodies).toHaveLength(2);
  expect(bodies[0]).toBe(bodies[1]);
  await expect(run).toHaveValue('22.5');
  await expect(page.getByText(/Existing spending is retained/u)).toBeVisible();
});
test('rejects stale configuration and deliberately loads the latest revision', async ({page}) => {
  await connect(page);
  await workspacePage(page, 'Settings');
  const response = await operatorRequest(page, 'configuration/catalog');
  const {configuration_revision} = z
    .object({configuration_revision: z.string()})
    .parse((await response.json()) as unknown);
  const update = await operatorRequest(
    page,
    'configuration/limits',
    JSON.stringify({
      command_id: 'c'.repeat(32),
      expected_revision: configuration_revision,
      limits: {call_seconds: 15},
    }),
  );
  expect(update.ok()).toBe(true);
  await page.getByRole('textbox', {name: /Run deadline \(seconds\)/u}).fill('22');
  await apply(page);
  await expect(page.getByText(/configuration_conflict/u)).toBeVisible();
  await page.getByRole('button', {name: 'Refresh configuration'}).click();
  await expect(page.getByText(/The discovered revision differs/u)).toBeVisible();
  await page.getByRole('button', {name: 'Use latest server limits'}).click();
  await expect(page.getByRole('textbox', {name: /Call deadline \(seconds\)/u})).toHaveValue('15');
  await page.getByRole('textbox', {name: /Run deadline \(seconds\)/u}).fill('22');
  await apply(page);
  await expect(page.getByText(/Settings confirmed under revision/u)).toBeVisible();
});
async function apply(page: Page): Promise<void> {
  await page.getByRole('button', {name: 'Apply settings', exact: true}).click();
}
async function lostSettingsReply(page: Page): Promise<(string | null)[]> {
  const bodies: (string | null)[] = [];
  await page.route('**/api/v1/configuration/limits', async (route) => {
    bodies.push(route.request().postData());
    const response = await route.fetch();
    expect(response.ok()).toBe(true);
    if (bodies.length === 1) await route.abort('failed');
    else await route.fulfill({response});
  });
  return bodies;
}
