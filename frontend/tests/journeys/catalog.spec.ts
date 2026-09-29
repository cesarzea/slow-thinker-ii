import {expect, test} from '@playwright/test';
import {connect} from '../support/browser.ts';

const examples = [
  ['single-agent', 1],
  ['handoff', 2],
  ['proposal-review', 3],
  ['repeated-review', 5],
  ['bounded-review', 2],
] as const;

test('the five bundled graphs render through the actual backend', async ({page}, testInfo) => {
  await connect(page);
  const selector = page.getByRole('combobox', {name: 'Experimento', exact: true});
  await expect(selector.locator('option')).toHaveCount(5);
  for (const [id, count] of examples) {
    await selector.selectOption(id);
    await expect(
      page.getByRole('list', {name: 'Nodos del experimento'}).getByRole('listitem'),
    ).toHaveCount(count);
    await expect(page.locator('.react-flow__node').filter({hasText: 'Nodo:'})).toHaveCount(count);
    await expect(page.getByText(/Estructura detallada no disponible/)).toHaveCount(0);
    await expect(page.locator('.react-flow__edge')).toHaveCount(
      id === 'bounded-review' ? 3 : count,
    );
  }
  await selector.selectOption('proposal-review');
  await expect(page.getByText('2 agentes · 3 nodos declarados', {exact: false})).toBeVisible();
  await expect(page.getByText(/Estructura detallada no disponible/)).toHaveCount(0);
  await expect(page.locator('.react-flow__edge')).toHaveCount(3);
  await page.screenshot({path: testInfo.outputPath('graph-view.png'), fullPage: true});
  await page.reload();
  await connect(page, false);
  await expect(selector.locator('option')).toHaveCount(5);
});
