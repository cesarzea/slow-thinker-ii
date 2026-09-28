import {expect, test} from '@playwright/test';
import {connect} from '../support/browser.ts';

test('the four bundled graphs render through the actual backend', async ({page}, testInfo) => {
  await connect(page);
  const selector = page.getByRole('combobox', {name: 'Experimento', exact: true});
  await expect(selector.locator('option')).toHaveCount(4);
  const examples = [
    ['single-agent', 1],
    ['handoff', 2],
    ['proposal-review', 3],
    ['repeated-review', 5],
  ] as const;
  for (const [id, count] of examples) {
    await selector.selectOption(id);
    await expect(
      page.getByRole('list', {name: 'Orden de ejecución'}).getByRole('listitem'),
    ).toHaveCount(count);
    await expect(page.locator('.react-flow__node')).toHaveCount(count);
    await expect(page.locator('.react-flow__edge')).toHaveCount(count - 1);
  }
  await selector.selectOption('proposal-review');
  await expect(page.getByText('2 agentes · 3 activaciones', {exact: false})).toBeVisible();
  await page.screenshot({path: testInfo.outputPath('graph-view.png'), fullPage: true});
  await page.reload();
  await connect(page, false);
  await expect(selector.locator('option')).toHaveCount(4);
});
