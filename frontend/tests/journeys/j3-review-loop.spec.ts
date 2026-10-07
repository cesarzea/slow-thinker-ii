import {expect, test} from '@playwright/test';
import {buildReviewLoop, setLimits, STORY} from './support/review-graph.ts';
import {expectResult, expectStatus, openActivity, runGraph} from './support/runs.ts';
import {connect, openSection, saved} from './support/session.ts';

test('J3: the review loop ends when the story is accepted', async ({page}) => {
  await connect(page);
  await buildReviewLoop(page, 'Funny story with review');
  await setLimits(page, '10', '0.05');
  await saved(page);
  await runGraph(page, STORY);
  await expectStatus(page, 'Completed');
  await expectResult(page, 'Funny story', 'Simulated reply to:');
  await openActivity(page);
  const timeline = page.getByRole('list', {name: 'Timeline'});
  await expect(timeline).toContainText('LLM call');
  await expect(timeline).toContainText('accepted');
  await expect(timeline).toContainText('Reported by LLM Call');
  await expect(page.getByRole('region', {name: 'Totals'})).toContainText('Proposer');
});

test('J3: a loop that is not accepted in time stops at the activation limit', async ({page}) => {
  await connect(page);
  await buildReviewLoop(page, 'Review with a tight limit');
  await setLimits(page, '3', '0.05');
  await saved(page);
  await runGraph(page, STORY);
  await expectStatus(page, 'Stopped: activation limit reached');
  await expect(page.getByText('The run reached its limit of 3 activations')).toBeVisible();
});

test('J1 and J3: DeepSeek temperature follows the reasoning setting', async ({page}) => {
  await connect(page);
  await buildReviewLoop(page, 'Reasoning settings');
  const dialog = await openSection(page, 'Reviewer', 'Model');
  await dialog.getByRole('combobox', {name: 'Reasoning'}).selectOption({label: 'high'});
  await expect(dialog.getByRole('spinbutton', {name: 'Temperature'})).toBeDisabled();
  await dialog.getByRole('combobox', {name: 'Reasoning'}).selectOption({label: 'none'});
  await expect(dialog.getByRole('spinbutton', {name: 'Temperature'})).toBeEnabled();
  await dialog.getByRole('button', {name: 'Cancel'}).click();
});
