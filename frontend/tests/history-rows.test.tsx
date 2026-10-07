import {expect, it} from 'vitest';
import {runListSchema} from '../src/api/schemas/runs.ts';
import type {RunSummary} from '../src/api/index.ts';
import {isActive, numberedRuns, runRows} from '../src/features/history/run-rows.ts';
import {runSummary} from './support/runs.ts';

function runs(...fields: Record<string, unknown>[]): RunSummary[] {
  return runListSchema.parse({runs: fields.map((field) => runSummary(field))}).runs;
}

it('numbers each run among the listed runs of its graph, oldest first', () => {
  const list = runs(
    {run_id: 'a3', graph_id: 'a'},
    {run_id: 'b2', graph_id: 'b'},
    {run_id: 'a2', graph_id: 'a'},
    {run_id: 'b1', graph_id: 'b'},
    {run_id: 'a1', graph_id: 'a'},
  );
  expect(numberedRuns(list).map(({run, number}) => [run.run_id, number])).toEqual([
    ['a3', 3],
    ['b2', 2],
    ['a2', 2],
    ['b1', 1],
    ['a1', 1],
  ]);
  expect(numberedRuns([])).toEqual([]);
});

it('formats each row and names graphs without a known name by their id', () => {
  const started = '2026-10-04T05:00:00.000Z';
  const list = runs(
    {run_id: 'r2', graph_id: 'other', status: 'running', totals: {}, ended_at: null},
    {
      run_id: 'r1',
      graph_id: 'story',
      status: 'stopped',
      reason: 'time_limit',
      totals: null,
      ended_at: '2026-10-04T05:00:02.500Z',
    },
  );
  const rows = runRows(list, new Map([['story', 'Funny story']]));
  expect(
    rows.map((row) => [row.name, row.statusText, row.duration, row.llmCalls, row.cost]),
  ).toEqual([
    ['other · Run 1', 'Running', '—', '—', '—'],
    ['Funny story · Run 1', 'Stopped: time limit reached', '2.5 s', '—', '—'],
  ]);
  const local = new Intl.DateTimeFormat('en', {dateStyle: 'medium', timeStyle: 'medium'});
  expect(rows[1]).toMatchObject({graphId: 'story', runId: 'r1', version: 'v1', status: 'stopped'});
  expect(rows[1]?.started).toBe(local.format(new Date(started)));
  expect(list.map(isActive)).toEqual([true, false]);
});

it('takes figures from the totals of a finished run', () => {
  const [row] = runRows(runs({graph_id: 'story'}), new Map());
  expect(row).toMatchObject({
    name: 'story · Run 1',
    statusText: 'Completed',
    duration: '6.0 s',
    llmCalls: '4',
    cost: '$0.000083',
  });
});
