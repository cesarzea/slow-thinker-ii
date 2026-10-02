import {expect, test} from '@playwright/test';
import type {Locator, Page} from '@playwright/test';
import {connect} from '../support/browser.ts';

test('shows input/output connectors and horizontal exterior arrows after expansion and dragging', async ({
  page,
}) => {
  const warnings: string[] = [];
  page.on('console', (message) => {
    if (message.text().includes('not initialized')) warnings.push(message.text());
  });
  await connect(page);
  const canvas = page.getByLabel('Agent collaboration canvas');
  await expect(canvas.locator('.agent-card')).toHaveCount(1);
  await expect(canvas.locator('.react-flow__edge')).toHaveCount(2);
  await expect(canvas.locator('.system-markers')).toHaveCount(0);
  await expectConnectors(canvas);
  await expectBoundaryArrows(canvas);
  await page.getByLabel('Show configuration').check();
  await expect(canvas.getByText('Reasoning effort')).toBeVisible();
  await expectBoundaryArrows(canvas);
  await moveAgent(page, canvas);
  await expectBoundaryArrows(canvas);
  await page.getByRole('button', {name: 'Reorganize graph'}).click();
  await expectConnectors(canvas);
  await expectBoundaryArrows(canvas);
  expect(warnings).toEqual([]);
});
async function expectConnectors(canvas: Locator): Promise<void> {
  const connectors = canvas.locator('.agent-connector');
  await expect(connectors).toHaveCount(2);
  for (const connector of await connectors.all()) {
    await expect(connector).toBeVisible();
    await expect(connector).toHaveCSS('opacity', '1');
    await expect(connector).toHaveCSS('background-color', 'rgb(64, 92, 121)');
  }
  await expect(canvas.locator('.react-flow__node-entry')).toHaveAttribute('aria-hidden', 'true');
  await expect(canvas.locator('.react-flow__node-terminal')).toHaveAttribute('aria-hidden', 'true');
}
async function expectBoundaryArrows(canvas: Locator): Promise<void> {
  await expect
    .poll(async () => {
      return await canvas.evaluate((element) => {
        const input = element.querySelector(
          '.react-flow__edge[data-id^="entry:"] path.react-flow__edge-path',
        );
        const output = element.querySelector(
          '.react-flow__edge[data-id^="control:"] path.react-flow__edge-path',
        );
        if (!(input instanceof SVGPathElement) || !(output instanceof SVGPathElement)) return false;
        return [input, output].every((path) => {
          const length = path.getTotalLength();
          const first = path.getPointAtLength(0);
          const last = path.getPointAtLength(length);
          return length > 100 && Math.abs(first.y - last.y) < 0.1 && last.x > first.x;
        });
      });
    })
    .toBe(true);
}
async function moveAgent(page: Page, canvas: Locator): Promise<void> {
  const agent = canvas.locator('.react-flow__node-agent');
  await agent.scrollIntoViewIfNeeded();
  await expect(agent).toBeInViewport();
  const box = await agent.boundingBox();
  if (box === null) throw new Error('Missing agent card');
  const start = {x: box.x + box.width / 2, y: box.y + 20};
  await page.mouse.move(start.x, start.y);
  await page.mouse.down();
  await page.mouse.move(start.x + 40, start.y + 60, {steps: 6});
  await page.mouse.up();
  await expect
    .poll(async () => (await agent.boundingBox())?.y ?? box.y)
    .toBeGreaterThan(box.y + 30);
}
