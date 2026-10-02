import {expect, test} from '@playwright/test';
import {connect} from '../support/browser.ts';

const examples = [
  ['single-agent', 'example-2', 1],
  ['handoff', 'example-2', 2],
  ['proposal-review', 'example-2', 3],
  ['repeated-review', 'example-2', 5],
  ['bounded-review', 'example-1', 2],
] as const;

test('the five bundled graphs render through the actual backend', async ({page}, testInfo) => {
  await connect(page);
  const selector = page.getByRole('combobox', {name: 'Experiment', exact: true});
  await expect(selector.locator('option')).toHaveCount(5);
  for (const [id, revision, count] of examples) {
    await selector.selectOption(JSON.stringify([id, revision]));
    await expect(
      page.getByRole('list', {name: 'Experiment nodes'}).getByRole('listitem'),
    ).toHaveCount(count);
    await expect(page.locator('.agent-card')).toHaveCount(count);
    await expect(page.getByText(/Detailed structure unavailable/)).toHaveCount(0);
    await expect(page.locator('.react-flow__edge')).toHaveCount(
      id === 'bounded-review' ? 4 : count + 1,
    );
  }
  await selector.selectOption(JSON.stringify(['proposal-review', 'example-2']));
  await expect(page.getByText('2 agents · 3 declared nodes', {exact: false})).toBeVisible();
  await expect(page.getByText(/Detailed structure unavailable/)).toHaveCount(0);
  await expect(page.locator('.react-flow__edge')).toHaveCount(4);
  await page.screenshot({path: testInfo.outputPath('graph-view.png'), fullPage: true});
  await page.reload();
  await connect(page, false);
  await expect(selector.locator('option')).toHaveCount(5);
});
