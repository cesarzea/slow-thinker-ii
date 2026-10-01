import {expect, test} from '@playwright/test';
import type {Locator, Page} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';

test('preserves dragged agent position and viewport across actual execution polling', async ({
  page,
}) => {
  await connect(page);
  await page
    .getByRole('combobox', {name: 'Experiment', exact: true})
    .selectOption('bounded-review');
  await createSession(page, 'Graph polling');
  await page.getByLabel('Task or problem').fill('accept');
  await page.getByRole('button', {name: 'Start run', exact: true}).click();
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
  const live = page.getByRole('region', {name: 'Selected run graph'});
  const canvas = live.getByLabel('Agent collaboration canvas');
  const node = canvas.locator('.react-flow__node[data-id="node:propose"]');
  await expect(node).toBeVisible();
  await dragAgent(page, node);
  await live.getByRole('button', {name: /zoom in/i}).click();
  const position = await node.getAttribute('style');
  const viewport = await canvas.locator('.react-flow__viewport').getAttribute('style');
  await page.waitForResponse((response) => response.url().includes('/execution') && response.ok());
  await expect(node).toHaveAttribute('style', position ?? '');
  await expect(canvas.locator('.react-flow__viewport')).toHaveAttribute('style', viewport ?? '');
  await live.getByRole('button', {name: 'Reorganize graph'}).click();
  await expect(node).not.toHaveAttribute('style', position ?? '');
});
async function dragAgent(page: Page, node: Locator): Promise<void> {
  const bounds = await node.boundingBox();
  if (bounds === null) throw new Error('Agent card missing');
  await page.mouse.move(bounds.x + bounds.width / 2, bounds.y + 20);
  await page.mouse.down();
  await page.mouse.move(bounds.x + bounds.width / 2 + 35, bounds.y + 55, {steps: 6});
  await page.mouse.up();
}
