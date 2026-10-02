import {expect, test} from '@playwright/test';
import type {Page} from '@playwright/test';
import {connect} from '../support/browser.ts';
import {editableSource, editor, saveRevision} from '../support/browser-authoring.ts';

test('recovers a committed save after a lost reply by replaying identical source', async ({
  page,
}) => {
  await connect(page);
  const source = (await editableSource(page)).replace(
    '"revision":"example-2"',
    '"revision":"recovery-identical"',
  );
  const bodies = await loseFirstSaveReply(page);
  await editor(page).fill(`\n${source}\n`);
  await page.getByRole('button', {name: 'Validate definition', exact: true}).click();
  await page.getByRole('button', {name: 'Save definition', exact: true}).click();
  await expect(page.getByText(/Save unconfirmed/u)).toBeVisible();
  await expect(editor(page)).not.toBeEditable();
  await expect(page.getByRole('button', {name: 'Validate definition', exact: true})).toBeDisabled();
  await page.getByRole('button', {name: 'Retry same save', exact: true}).click();
  await expect(page.getByRole('combobox', {name: 'Experiment', exact: true})).toHaveValue(
    JSON.stringify(['single-agent', 'recovery-identical']),
  );
  expect(bodies).toEqual([`\n${source}\n`, `\n${source}\n`]);
  await expect(editor(page)).toBeEditable();
});

async function loseFirstSaveReply(page: Page): Promise<(string | null)[]> {
  const bodies: (string | null)[] = [];
  await page.route('**/api/v1/definitions', async (route) => {
    if (route.request().method() !== 'POST') {
      await route.continue();
      return;
    }
    bodies.push(route.request().postData());
    const response = await route.fetch();
    if (bodies.length === 1) await route.abort('failed');
    else await route.fulfill({response});
  });
  return bodies;
}

test('retains confirmed Save and the original baseline until a failed library read recovers', async ({
  page,
}) => {
  await connect(page);
  const source = (await editableSource(page)).replace(
    '"revision":"example-2"',
    '"revision":"recovery-listing"',
  );
  await editor(page).fill(source);
  await page.getByRole('button', {name: 'Validate definition', exact: true}).click();
  await page.route('**/api/v1/definitions?*', (route) => route.abort('failed'));
  await page.getByRole('button', {name: 'Save definition', exact: true}).click();
  await expect(
    page.getByText('Confirmed saved definition: single-agent · recovery-listing'),
  ).toBeVisible();
  await expect(page.getByText(/its library refresh failed/u)).toBeVisible();
  await expect(editor(page)).toHaveValue(/"revision":"example-2"/u);
  await expect(page.getByText('No unsaved changes.')).toBeVisible();
  await expect(page.getByText(/Definition validation passed/u)).toHaveCount(0);
  await page.unroute('**/api/v1/definitions?*');
  await page.getByRole('button', {name: 'Retry saved definition selection'}).click();
  await expect(page.getByRole('combobox', {name: 'Experiment', exact: true})).toHaveValue(
    JSON.stringify(['single-agent', 'recovery-listing']),
  );
  await expect(editor(page)).toBeEditable();
  await saveRevision(page, 'recovery-listing');
});
