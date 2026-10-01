import {expect, test} from '@playwright/test';
import type {Locator, Page} from '@playwright/test';
import {connect} from '../support/browser.ts';

test('fits arriving agent definitions, expanded configuration and separate reciprocal routes', async ({
  page,
}, info) => {
  await delayDefinition(page);
  await connect(page);
  await page
    .getByRole('combobox', {name: 'Experiment', exact: true})
    .selectOption('bounded-review');
  await expect(page.getByText(/Detailed structure unavailable/)).toHaveCount(0);
  const canvas = page.getByLabel('Agent collaboration canvas');
  await expect(canvas.locator('.react-flow__node-agent')).toHaveCount(2);
  await expect(canvas.locator('.react-flow__node[data-id^="component:"]')).toHaveCount(0);
  await expect(canvas.locator('.react-flow__node-terminal')).toHaveAttribute('aria-hidden', 'true');
  await expect.poll(async () => allCardsInside(canvas)).toBe(true);
  await expectSeparatedRoutes(canvas);
  await page.getByLabel('Show configuration').check();
  await expect(canvas.getByText('Reasoning effort')).toHaveCount(2);
  await expect.poll(async () => allCardsInside(canvas)).toBe(true);
  await expectCardsSeparated(canvas);
  await page.getByLabel('Show system elements').check();
  await expect(canvas.locator('.system-markers circle')).toHaveCount(5);
  await page.getByRole('button', {name: /zoom in/i}).click();
  await page.getByRole('button', {name: 'Reorganize graph'}).click();
  await expect.poll(async () => allCardsInside(canvas)).toBe(true);
  await page.screenshot({path: info.outputPath('bounded-review-agent-canvas.png'), fullPage: true});
});
async function delayDefinition(page: Page): Promise<void> {
  await page.route('**/graphs/bounded-review/revisions/*', async (route) => {
    await new Promise((resolve) => {
      setTimeout(resolve, 150);
    });
    await route.continue();
  });
}
test('keeps agent configuration within a narrow viewport after fitting', async ({page}) => {
  await page.setViewportSize({width: 390, height: 844});
  await connect(page);
  await page
    .getByRole('combobox', {name: 'Experiment', exact: true})
    .selectOption('bounded-review');
  const canvas = page.getByLabel('Agent collaboration canvas');
  await expect(canvas.locator('.react-flow__node-agent')).toHaveCount(2);
  await page.getByLabel('Show configuration').check();
  await page.getByRole('button', {name: 'Reorganize graph'}).click();
  await expect.poll(async () => allCardsInside(canvas)).toBe(true);
  await expectCardsSeparated(canvas);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
async function allCardsInside(canvas: Locator): Promise<boolean> {
  return await canvas.evaluate((element) => {
    const bounds = element.getBoundingClientRect();
    return [...element.querySelectorAll('.react-flow__node-agent')].every((node) => {
      const box = node.getBoundingClientRect();
      return (
        box.width > 0 &&
        box.height > 0 &&
        box.left >= bounds.left &&
        box.right <= bounds.right &&
        box.top >= bounds.top &&
        box.bottom <= bounds.bottom
      );
    });
  });
}
async function expectSeparatedRoutes(canvas: Locator): Promise<void> {
  const forward = canvas.locator('.react-flow__edge').filter({hasText: /^next$/});
  const backward = canvas.locator('.react-flow__edge').filter({hasText: /^revise$/});
  const first = await forward.locator('.react-flow__edge-text').boundingBox();
  const second = await backward.locator('.react-flow__edge-text').boundingBox();
  if (first === null || second === null) throw new Error('Missing control labels');
  expect(first.y + first.height).toBeLessThan(second.y);
  expect(await forward.locator('.react-flow__edge-path').getAttribute('d')).not.toBe(
    await backward.locator('.react-flow__edge-path').getAttribute('d'),
  );
}
async function expectCardsSeparated(canvas: Locator): Promise<void> {
  const cards = canvas.locator('.react-flow__node-agent');
  const first = await cards.nth(0).boundingBox();
  const second = await cards.nth(1).boundingBox();
  if (first === null || second === null) throw new Error('Missing agent cards');
  expect(first.x + first.width).toBeLessThan(second.x);
}
