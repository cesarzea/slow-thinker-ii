import {expect, test} from '@playwright/test';
import type {Locator, Page, TestInfo} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';
import {openProposerCall} from '../support/saved-run-canvas.ts';

test('inspects retained events, call arguments and responses through the actual backend', async ({
  page,
}, info) => {
  await connect(page);
  await createSession(page, 'Browser inspection');
  await page.getByLabel('Task or problem').fill('Inspect this run');
  await page.getByRole('button', {name: 'Start run', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
  await page.getByRole('button', {name: 'Inspect run'}).click();
  const row = await openProposerCall(page);
  const call = page.getByRole('region', {name: 'Call details'});
  await expect(call).toContainText('USD 0.00000239');
  await checkNavigation(page, row);
  await call.getByRole('button', {name: 'View arguments'}).click();
  await expect(page.getByRole('region', {name: 'Retained content'})).toContainText(
    'Inspect this run',
  );
  await call.getByRole('button', {name: 'View response', exact: true}).click();
  await expect(page.getByRole('region', {name: 'Retained content'})).toContainText('Test result');
  await page.screenshot({path: info.outputPath('inspection.png'), fullPage: true});
  await inspectActivation(page, info);
  await page.getByRole('button', {name: 'Close inspector'}).click();
  await expect(page.getByRole('region', {name: 'Run inspector'})).toHaveCount(0);
});

async function inspectActivation(page: Page, info: TestInfo): Promise<void> {
  await page.getByRole('button', {name: 'View activation', exact: true}).click();
  const activation = page.getByRole('region', {name: 'Activation details'});
  await expect(activation).toContainText('Agent: proposer · Node: draft');
  await expect(activation.getByRole('heading', {level: 3})).toBeFocused();
  await expect(activation.getByRole('heading', {level: 3})).toBeInViewport();
  await activation.getByRole('button', {name: 'View published output'}).click();
  await expect(page.getByRole('region', {name: 'Retained content'})).toContainText('Test result');
  await page.screenshot({path: info.outputPath('activation.png'), fullPage: true});
}

async function checkNavigation(page: Page, row: Locator): Promise<void> {
  const call = page.getByRole('region', {name: 'Call details'});
  await expect(call.getByRole('heading', {level: 3})).toBeFocused();
  await expect(call.getByRole('heading', {level: 3})).toBeInViewport();
  await row.getByRole('button', {name: /View call/}).click();
  await expect(call.getByRole('heading', {level: 3})).toBeFocused();
  await expect(call.getByRole('heading', {level: 3})).toBeInViewport();
  for (const attempt of [1, 2]) {
    await test.step(`Open event content ${String(attempt)}`, async () => {
      await row.getByRole('button', {name: /View content/}).click();
      const heading = page.getByRole('heading', {name: 'Retained content'});
      await expect(heading).toBeFocused();
      await expect(heading).toBeInViewport();
    });
  }
}
