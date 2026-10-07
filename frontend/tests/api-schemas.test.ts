import {afterEach, expect, it, vi} from 'vitest';
import {OperatorClient} from '../src/api/index.ts';
import {FakeApi} from './support/fake-api.ts';
import {j3Events} from './support/j3-events.ts';
import {runDetail, runSummary} from './support/runs.ts';

afterEach(() => {
  vi.unstubAllGlobals();
});
const client = (): OperatorClient => new OperatorClient('operator-credential');
const page = (events: readonly unknown[]): {status: number; body: unknown} => ({
  status: 200,
  body: {events, last_seq: events.length, finished: true},
});

it('parses every recorded event kind of the J3 log', async () => {
  new FakeApi().on('GET /runs/run-1/events', page(j3Events)).install();
  const result = await client().events('run-1', 0);
  expect(result.events.map((event) => event.kind)).toContain('llm.called');
  expect(result.events.at(-1)?.kind).toBe('run.finished');
  expect(result.events.find((event) => event.kind === 'report')?.evidence).toBe('reported');
});

it('rejects an unknown event kind or an unexpected event field', async () => {
  const first = j3Events[0] ?? {};
  const data = first['data'] as Record<string, unknown>;
  new FakeApi()
    .on('GET /runs/a/events', page([{...first, kind: 'run.paused'}]))
    .on('GET /runs/b/events', page([{...first, extra: true}]))
    .on('GET /runs/c/events', page([{...first, data: {...data, extra: 1}}]))
    .install();
  for (const run of ['a', 'b', 'c'])
    await expect(client().events(run, 0)).rejects.toMatchObject({code: 'invalid_response'});
});

it('reads a running run whose totals are not yet recorded', async () => {
  const running = {status: 'running', ended_at: null, detail: null};
  new FakeApi()
    .on('GET /runs/empty', {status: 200, body: runDetail({...running, totals: {}})})
    .on('GET /runs/none', {status: 200, body: runDetail({...running, totals: null})})
    .on('GET /runs', {status: 200, body: {runs: [runSummary({totals: {cost_usd: '1'}})]}})
    .install();
  expect((await client().run('empty')).totals).toBeNull();
  expect((await client().run('none')).totals).toBeNull();
  await expect(client().runs()).rejects.toMatchObject({code: 'invalid_response'});
});

it('rejects statuses and reasons outside the execution contract', async () => {
  new FakeApi()
    .on('GET /runs/a', {status: 200, body: runDetail({status: 'paused'})})
    .on('GET /runs/b', {status: 200, body: runDetail({reason: 'unknown'})})
    .install();
  await expect(client().run('a')).rejects.toMatchObject({code: 'invalid_response'});
  await expect(client().run('b')).rejects.toMatchObject({code: 'invalid_response'});
});
