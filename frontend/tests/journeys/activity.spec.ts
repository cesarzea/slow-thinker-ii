import {expect, test, type Locator, type Page} from '@playwright/test';
import {buildReviewLoop, setLimits, STORY} from './support/review-graph.ts';
import {expectStatus, openActivity, runGraph} from './support/runs.ts';
import {connect, saved} from './support/session.ts';

const END = 'Completed: no message pending and no node running';

async function runAndOpenActivity(page: Page): Promise<Locator> {
  await connect(page);
  await buildReviewLoop(page, 'Funny story with activity');
  await setLimits(page, '10', '0.05');
  await saved(page);
  await runGraph(page, STORY);
  await expectStatus(page, 'Completed');
  await openActivity(page);
  const timeline = page.getByRole('list', {name: 'Timeline'});
  await expect(timeline.getByRole('listitem').last()).toContainText(END);
  return timeline;
}

function rows(timeline: Locator, text: string | RegExp): Locator {
  return timeline.getByRole('listitem').filter({hasText: text});
}

async function expectInOrder(timeline: Locator, texts: readonly RegExp[]): Promise<void> {
  const all = await timeline.getByRole('listitem').allInnerTexts();
  const positions = texts.map((text) => all.findIndex((row) => text.test(row)));
  expect(positions).not.toContain(-1);
  expect(positions).toEqual([...positions].sort((a, b) => a - b));
}

test('Step 1.2: the activity view shows what happened, in order', async ({page}) => {
  const timeline = await runAndOpenActivity(page);
  await expect(timeline.getByRole('listitem').first()).toContainText(`Started with`);
  await expectInOrder(timeline, [
    /Started with/,
    /Activation 1 started/,
    /LLM call/,
    /router\s*"?accepted/,
    /Funny story: /,
    new RegExp(END),
  ]);
  const report = rows(timeline, 'Reported by LLM Call').first();
  await expect(report).toHaveClass(/reported/);
});

test('Step 1.2: a model call expands to its request, reply, usage, cost and rates', async ({
  page,
}) => {
  const timeline = await runAndOpenActivity(page);
  const call = rows(timeline, /LLM call/).first();
  await call.getByRole('button').click();
  const detail = call.getByRole('region');
  await expect(detail).toContainText('system: Rewrite this story so that it is funny.');
  await expect(detail).toContainText(`user: ${STORY}`);
  await expect(detail).toContainText('Simulated reply to:');
  await expect(detail).toContainText('max_completion_tokens');
  await expect(detail).toContainText('USD per million tokens');
  const decision = rows(timeline, /router/)
    .filter({hasText: /accepted/})
    .first();
  await decision.getByRole('button').click();
  await expect(decision.getByRole('region')).toContainText('accepted');
});

test('Step 1.2: filters and totals summarize the run', async ({page}) => {
  const timeline = await runAndOpenActivity(page);
  const show = page.getByRole('radiogroup', {name: 'Show'});
  await show.getByRole('radio', {name: 'Messages', exact: true}).check();
  await expect(rows(timeline, /LLM call/)).toHaveCount(0);
  await expect(rows(timeline, /message/).first()).toBeVisible();
  await show.getByRole('radio', {name: 'Calls', exact: true}).check();
  await expect(rows(timeline, 'Reported by')).toHaveCount(0);
  await expect(rows(timeline, /LLM call/).first()).toBeVisible();
  await show.getByRole('radio', {name: 'All', exact: true}).check();
  await expect(rows(timeline, 'Reported by').first()).toBeVisible();
  const totals = page.getByRole('region', {name: 'Totals'});
  for (const figure of ['Completed', 'Duration', 'Activations', 'Messages', 'LLM calls']) {
    await expect(totals).toContainText(figure);
  }
  await expect(totals).toContainText('Budget used');
  await expect(totals).toContainText('of $0.05');
  const nodes = totals.getByRole('table', {name: 'Activations by node'});
  for (const node of ['Story', 'Proposer', 'Reviewer', 'Funny story']) {
    await expect(nodes.getByRole('row', {name: new RegExp(`^${node}`)})).toBeVisible();
  }
});
