import {expect, test} from '@playwright/test';
import type {Locator, Page} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';

test('preserves dragged agent position and viewport across actual execution polling', async ({
  page,
}) => {
  const live = await openSavedRunGraph(page);
  const canvas = live.getByLabel('Agent collaboration canvas');
  const node = canvas.locator('.react-flow__node[data-id="node:propose"]');
  await expect(node).toBeVisible();
  await node.scrollIntoViewIfNeeded();
  const initialPosition = await transform(node);
  await dragAgent(page, node);
  await expect(node).not.toHaveCSS('transform', initialPosition);
  await live.getByRole('button', {name: /zoom in/i}).click();
  const position = await transform(node);
  const viewport = canvas.locator('.react-flow__viewport');
  const camera = await transform(viewport);
  await page.waitForResponse((response) => response.url().includes('/execution') && response.ok());
  await expect(node).toHaveCSS('transform', position);
  await expect(viewport).toHaveCSS('transform', camera);
  await live.getByRole('button', {name: 'Reorganize graph'}).click();
  await expect(node).toHaveCSS('transform', initialPosition);
});
async function openSavedRunGraph(page: Page): Promise<Locator> {
  await connect(page);
  await page
    .getByRole('combobox', {name: 'Experiment', exact: true})
    .selectOption('bounded-review');
  await createSession(page, 'Graph polling');
  await page.getByLabel('Task or problem').fill('accept');
  await page.getByRole('button', {name: 'Start run', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
  return page.getByRole('region', {name: 'Selected run graph'});
}
async function transform(locator: Locator): Promise<string> {
  return await locator.evaluate((element) => getComputedStyle(element).transform);
}
async function dragAgent(page: Page, node: Locator): Promise<void> {
  const bounds = await node.boundingBox();
  if (bounds === null) throw new Error('Agent card missing');
  await page.mouse.move(bounds.x + bounds.width / 2, bounds.y + 20);
  await page.mouse.down();
  await page.mouse.move(bounds.x + bounds.width / 2 + 35, bounds.y + 55, {steps: 6});
  await page.mouse.up();
}
