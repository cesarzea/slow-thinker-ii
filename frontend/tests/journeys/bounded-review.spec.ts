import {expect, test} from '@playwright/test';
import type {Page, Locator} from '@playwright/test';
import {connect, createSession} from '../support/browser.ts';

async function start(page: Page, problem: string): Promise<void> {
  await connect(page);
  await page
    .getByRole('combobox', {name: 'Experiment', exact: true})
    .selectOption(JSON.stringify(['bounded-review', 'example-1']));
  await createSession(page, `Bounded ${problem}`);
  await page.getByLabel('Task or problem').fill(problem);
  await page.getByRole('button', {name: 'Start run', exact: true}).click();
}
async function openLiveList(page: Page): Promise<ReturnType<Page['getByRole']>> {
  const live = page.getByRole('region', {name: 'Selected run graph'});
  await live.getByText('Explore graph and evidence').click();
  return live;
}
test('retains feedback and repeated identities through rejection then acceptance', async ({
  page,
}, info) => {
  await start(page, 'accept');
  await expect(page.getByRole('heading', {name: 'Completed', exact: true})).toBeVisible();
  const live = await openLiveList(page);
  await expect(
    live.getByRole('list', {name: 'Recorded activations'}).getByRole('listitem'),
  ).toHaveCount(4);
  await expect(live.getByRole('list', {name: 'Recorded activations'})).toContainText('revise');
  await expect(live.getByRole('list', {name: 'Recorded activations'})).toContainText('accept');
  await page.screenshot({path: info.outputPath('bounded-review-loaded.png'), fullPage: true});
  await inspectAcceptedFeedback(page, live);
  await expect(page.getByRole('region', {name: 'Final result'})).toContainText('accepted');
});
test('shows bounded exhaustion with preserved reviews and no accepted result', async ({page}) => {
  await start(page, 'exhaust');
  await expect(page.getByRole('heading', {name: 'Failed', exact: true})).toBeVisible();
  await expect(page.getByRole('region', {name: 'Run state'})).toContainText(
    'activation_limit_reached',
  );
  const live = await openLiveList(page);
  await expect(
    live.getByRole('list', {name: 'Recorded activations'}).getByRole('listitem'),
  ).toHaveCount(6);
  await live.getByRole('button', {name: 'Activation #6: review', exact: true}).click();
  const activation = page.getByRole('region', {name: 'Activation details'});
  await expect(activation.getByRole('heading', {level: 3})).toBeInViewport();
  await activation.getByRole('button', {name: 'View published output'}).click();
  await expect(page.getByRole('region', {name: 'Retained content'})).toContainText('findings');
  await expect(page.getByRole('region', {name: 'Final result'})).toHaveCount(0);
});

async function inspectAcceptedFeedback(page: Page, live: Locator): Promise<void> {
  await page.setViewportSize({width: 390, height: 844});
  await verifyRolesAndContainment(live);
  const chosen = live.getByRole('button', {name: 'Activation #3: propose', exact: true});
  await chosen.focus();
  await chosen.press('Enter');
  const activation = page.getByRole('region', {name: 'Activation details'});
  await expect(activation.getByRole('heading', {level: 3})).toBeFocused();
  await expect(activation.getByRole('heading', {level: 3})).toBeInViewport();
  await activation.getByRole('button', {name: 'View effective input'}).click();
  await expect(page.getByRole('region', {name: 'Retained content'})).toContainText('findings');
  await activation.getByRole('button', {name: 'View input provenance'}).click();
  await expect(page.getByRole('region', {name: 'Retained content'})).toContainText('review');
}
async function verifyRolesAndContainment(live: Locator): Promise<void> {
  const canvas = live.getByLabel('Agent collaboration canvas');
  await expect(canvas.getByRole('img', {name: 'AI agent'})).toHaveCount(2);
  await expect(canvas.getByText('Proposer', {exact: true})).toHaveCount(1);
  await expect(canvas.getByText('Reviewer', {exact: true})).toHaveCount(1);
  await expect(canvas.locator('.react-flow__node[data-id^="activation:"]')).toHaveCount(0);
  await expect(canvas.locator('.react-flow__node[data-id^="component:"]')).toHaveCount(0);
  await expect(live.getByRole('region', {name: 'Resources'}).getByRole('button')).toHaveText([
    'proposer-model',
    'review-router',
    'reviewer-model',
  ]);
  await expect(
    live.getByRole('button', {name: 'Component review-worker', exact: true}),
  ).toBeVisible();
}
