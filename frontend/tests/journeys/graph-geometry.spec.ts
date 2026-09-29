import {expect, test} from '@playwright/test';
import type {Locator} from '@playwright/test';
import {connect} from '../support/browser.ts';

test('fits exact collapsed structure and keeps reciprocal control labels separate', async ({
  page,
}, info) => {
  await page.route('**/graphs/bounded-review/revisions/*', async (route) => {
    await new Promise((resolve) => {
      setTimeout(resolve, 150);
    });
    await route.continue();
  });
  await connect(page);
  await page
    .getByRole('combobox', {name: 'Experimento', exact: true})
    .selectOption('bounded-review');
  await expect(page.getByText(/Estructura detallada no disponible/)).toHaveCount(0);
  const canvas = page.getByLabel('Lienzo de relaciones');
  await expect(canvas.locator('.react-flow__node[data-id^="component:"]')).toHaveCount(5);
  await expect(canvas.locator('.react-flow__node[data-id^="terminal:"]')).toHaveCount(1);
  await expect.poll(async () => allNodesInside(canvas)).toBe(true);
  await expectSeparatedRoutes(canvas);
  await page.getByRole('button', {name: /zoom in/i}).click();
  await page.getByRole('button', {name: 'Reorganizar grafo'}).click();
  await expect.poll(async () => allNodesInside(canvas)).toBe(true);
  await page.screenshot({
    path: info.outputPath('bounded-review-structure-fitted.png'),
    fullPage: true,
  });
});
async function allNodesInside(canvas: Locator): Promise<boolean> {
  return await canvas.evaluate((element) => {
    const bounds = element.getBoundingClientRect();
    return [...element.querySelectorAll('.react-flow__node')].every((node) => {
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
  const forward = canvas.locator('.react-flow__edge').filter({hasText: 'control: next'});
  const backward = canvas.locator('.react-flow__edge').filter({hasText: 'control: revise'});
  const first = await forward.locator('.react-flow__edge-text').boundingBox();
  const second = await backward.locator('.react-flow__edge-text').boundingBox();
  expect(first).not.toBeNull();
  expect(second).not.toBeNull();
  if (first === null || second === null) throw new Error('Missing control labels');
  expect(first.y + first.height).toBeLessThan(second.y);
  expect(await forward.locator('.react-flow__edge-path').getAttribute('d')).not.toBe(
    await backward.locator('.react-flow__edge-path').getAttribute('d'),
  );
}
