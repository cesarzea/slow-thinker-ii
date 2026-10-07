import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {OperatorClient} from '../src/api/index.ts';
import {ActivityPage} from '../src/features/activity/index.ts';
import {activityApi as api, graphId} from './support/activity-api.ts';
import {j3Events} from './support/j3-events.ts';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

async function renderPage(): Promise<HTMLElement> {
  render(
    <ActivityPage
      client={new OperatorClient('credential')}
      graphId={graphId}
      runId="run-1"
      runHref="#/run"
    />,
  );
  expect(screen.getByRole('heading', {name: 'Activity'})).toBeTruthy();
  const timeline = screen.getByRole('list', {name: 'Timeline'});
  await within(timeline).findByText(/Reported by LLM Call/u);
  return timeline;
}

it('lists every recorded event in order with node, kind and summary', async () => {
  api();
  const timeline = await renderPage();
  const rows = within(timeline).getAllByRole('button');
  expect(rows).toHaveLength(j3Events.length);
  expect(rows[0]?.textContent).toBe('0.00RunstartStarted with A cat tried to learn to fly.');
  expect(rows[7]?.textContent).toBe(
    '1.40ProposerreportReported by LLM Call: Messages built, one call.',
  );
  expect(rows[8]?.textContent).toContain(
    'OpenAI · GPT-6 Luna · Simulated reply to: A cat tried to learn to fly.38/71 · $0.000031 · 1.3 s',
  );
  expect(rows[14]?.textContent).toContain('routerrevise · Simulated reply to');
  expect(rows[23]?.textContent).toContain('routeraccepted · Simulated reply');
  expect(rows[24]?.textContent).toContain('accepted → Funny story · in');
  expect(rows.at(-1)?.textContent).toBe(
    '5.80RunendCompleted: no message pending and no node running6.0 s',
  );
  expect(screen.getByRole('link', {name: 'Back to the run'}).getAttribute('href')).toBe('#/run');
});

it('expands a model call to its request, reply, usage, cost and rates', async () => {
  api();
  const timeline = await renderPage();
  const call = within(timeline).getAllByRole('button')[8];
  if (call === undefined) throw new Error('Missing call row');
  await userEvent.click(call);
  expect(call.getAttribute('aria-expanded')).toBe('true');
  const detail = screen.getByRole('region', {name: 'Details of event 9'});
  expect(detail.textContent).toContain('system: Rewrite this story so that it is funny.');
  expect(detail.textContent).toContain('user: A cat tried to learn to fly.');
  expect(detail.textContent).toContain('max_completion_tokens300');
  expect(within(detail).getByText('Simulated reply to: A cat tried to learn to fly.')).toBeTruthy();
  expect(detail.textContent).toContain('$0.0002');
  expect(detail.textContent).toContain('input 0.10 USD per million tokens');
  await userEvent.click(call);
  expect(screen.queryByRole('region', {name: 'Details of event 9'})).toBeNull();
});

it('expands a Router decision and a report to their recorded content', async () => {
  api();
  const timeline = await renderPage();
  const rows = within(timeline).getAllByRole('button');
  await userEvent.click(rows[14] ?? timeline);
  const decision = screen.getByRole('region', {name: 'Details of event 15'});
  expect(decision.textContent).toContain('select_output');
  expect(decision.textContent).toContain('score5');
  await userEvent.click(rows[7] ?? timeline);
  expect(screen.getByRole('region', {name: 'Details of event 8'}).textContent).toContain(
    'Reported by the component',
  );
});

it('filters messages and calls', async () => {
  api();
  const timeline = await renderPage();
  await userEvent.click(
    within(screen.getByRole('radiogroup', {name: 'Show'})).getByRole('radio', {name: 'Messages'}),
  );
  const messages = within(timeline).getAllByRole('button');
  expect(messages.every((row) => row.textContent.includes('message'))).toBe(true);
  expect(messages).toHaveLength(5);
  await userEvent.click(screen.getByRole('radio', {name: 'Calls'}));
  expect(within(timeline).getAllByRole('button')).toHaveLength(7);
  await userEvent.click(screen.getByRole('radio', {name: 'All'}));
  expect(within(timeline).getAllByRole('button')).toHaveLength(j3Events.length);
});

it('shows run totals and activations and cost per node', async () => {
  api();
  await renderPage();
  const totals = screen.getByRole('region', {name: 'Totals'});
  expect(within(totals).getByText('Completed')).toBeTruthy();
  expect(within(totals).getByText('412 / 173')).toBeTruthy();
  expect(within(totals).getByText('LLM calls').nextElementSibling?.textContent).toBe('4');
  expect(within(totals).getByText('0.2% of $0.05')).toBeTruthy();
  const table = within(totals).getByRole('table', {name: 'Activations by node'});
  const rows = within(table)
    .getAllByRole('row')
    .slice(1)
    .map((row) => row.textContent);
  expect(rows).toEqual(['Story1—', 'Proposer2$0.000062', 'Reviewer2$0.000062', 'Funny story1—']);
});
