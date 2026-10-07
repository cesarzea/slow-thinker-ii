import {afterEach, expect, it} from 'vitest';
import {cleanup, render, screen} from '@testing-library/react';
import type {RunDetail} from '../src/api/index.ts';
import {RunFigures} from '../src/features/runs/run-parts.tsx';
import {j1} from './support/contract.ts';
import {runDetail} from './support/runs.ts';

afterEach(cleanup);

const figures = (): Record<string, string> =>
  Object.fromEntries(
    [...document.querySelectorAll('.figures div')].map((row) => [
      row.querySelector('dt')?.textContent ?? '',
      row.querySelector('dd')?.textContent ?? '',
    ]),
  );

it('counts a running run’s activations and leaves the other figures unknown', () => {
  const run = runDetail({
    status: 'running',
    ended_at: null,
    totals: null,
    activations_by_node: {story: 1, proposer: 2},
  }) as unknown as RunDetail;
  render(<RunFigures run={run} limits={j1.limits} />);
  expect(figures()).toMatchObject({
    Activations: '3',
    'LLM calls': '—',
    Cost: '—',
    'Budget used': '—',
  });
  expect(screen.getByRole('status').textContent).toBe('Running');
});

it('shows the cost of a finished run, and its share of the budget when one is known', () => {
  const run = runDetail() as unknown as RunDetail;
  render(<RunFigures run={run} limits={null} />);
  expect(figures()['Budget used']).toBe('—');
  expect(figures()['Cost']).not.toBe('—');
  cleanup();
  render(<RunFigures run={run} limits={j1.limits} />);
  expect(figures()['Budget used']).toMatch(/ of \$0\.10$/u);
});
