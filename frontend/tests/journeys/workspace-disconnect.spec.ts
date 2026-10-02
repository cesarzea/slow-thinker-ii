import {expect, test} from '@playwright/test';
import type {Page} from '@playwright/test';
import {connect} from '../support/browser.ts';
import {editableSource, editor} from '../support/browser-authoring.ts';
import {workspacePage} from '../support/browser-workspace.ts';
test('clears protected drafts/settings and rejects late discovery on disconnect', async ({
  page,
}) => {
  await connect(page);
  const initial = await editableSource(page);
  await editor(page).fill(initial.replace('Propose a solution', 'Private Ω source'));
  await workspacePage(page, 'Settings');
  const run = page.getByRole('textbox', {name: /Run deadline \(seconds\)/u});
  const initialLimit = await run.inputValue();
  await run.fill('25');
  const release = await deferDiscovery(page);
  await page.getByRole('button', {name: 'Refresh configuration'}).click();
  await expect(page.getByText('Loading trusted configuration…')).toBeVisible();
  await page.getByRole('button', {name: 'Disconnect operator access'}).click();
  await page.unrouteAll({behavior: 'ignoreErrors'});
  release();
  await expect(page.getByLabel('Access key')).toHaveValue('');
  await expect(page.getByRole('region', {name: 'Experiment definition editor'})).toHaveCount(0);
  await workspacePage(page, 'Settings');
  await expect(page.getByText('Connect operator access to edit settings.')).toBeVisible();
  expect(await page.evaluate(() => JSON.stringify(localStorage))).not.toContain('Private Ω source');
  await connect(page, false);
  expect(await editableSource(page)).toBe(initial);
  await workspacePage(page, 'Settings');
  await expect(page.getByRole('textbox', {name: /Run deadline \(seconds\)/u})).toHaveValue(
    initialLimit,
  );
});
async function deferDiscovery(page: Page): Promise<() => undefined> {
  const gate = Promise.withResolvers<undefined>();
  await page.route('**/api/v1/configuration/catalog', async (route) => {
    const response = await route.fetch();
    await gate.promise;
    await route.fulfill({response});
  });
  return () => {
    gate.resolve(undefined);
    return undefined;
  };
}
