import {expect, test} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';

const input = 'Task or problem';
const start = 'Start run';

test('creates a saved session, executes, inspects results and recovers history after reload', async ({
  page,
}, info) => {
  await connect(page);
  await createSession(page, 'Browser completion');
  await page.getByLabel(input).fill('A private task');
  await page.getByRole('button', {name: start, exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Final result'})).toContainText('Test result');
  await expect(page.getByRole('region', {name: 'Run state'})).toContainText('USD 0.00000239');
  expect(await page.evaluate(() => JSON.stringify(localStorage))).not.toContain('A private task');
  await page.screenshot({path: info.outputPath('execution-result.png'), fullPage: true});
  await page.reload();
  await connect(page, false);
  await page
    .getByRole('navigation', {name: 'Workspace'})
    .getByRole('button', {name: 'Runs', exact: true})
    .click();
  const history = page.getByRole('region', {name: 'Session history'});
  await history.getByRole('button').first().click();
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
});

test('Stop closes a running execution while preserving uncertain spending', async ({page}) => {
  await connect(page);
  await createSession(page, 'Browser stop');
  await page.getByLabel(input).fill('wait');
  await page.getByRole('button', {name: start, exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Running', exact: true})).toBeVisible();
  await page.getByRole('button', {name: 'Stop run', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Cancelled', exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Run state'})).toContainText('USD 0.000003 pending');
  await expect(page.getByRole('region', {name: 'Final result'})).toHaveCount(0);
});
