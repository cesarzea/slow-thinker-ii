import {expect, it} from 'vitest';
import type {RunEvent} from '../src/api/index.ts';
import {activityNames} from '../src/features/activity/names.ts';
import {rowText} from '../src/features/activity/summaries.ts';
import {activityTotals} from '../src/features/activity/totals.ts';
import {catalog, j3} from './support/contract.ts';
import {j3Events} from './support/j3-events.ts';

const events = j3Events as unknown as RunEvent[];
const event = (kind: string, data: unknown, node: string | null = 'reviewer'): RunEvent =>
  ({
    run_id: 'r',
    seq: 99,
    at: '2026-10-04T05:00:00.000Z',
    elapsed_ms: 10,
    kind,
    evidence: 'observed',
    node_id: node,
    activation_id: 'a9',
    data,
  }) as unknown as RunEvent;
const failure = (message: string): {code: string; message: string} => ({code: 'x', message});
const router = {position: 'output', component: 'router@1.0.0'};
const call = {position: 'node', component: 'llm-call@1.0.0', operation: 'activate', arguments: {}};
const totals = {duration_ms: 1, activations: 3, messages: 2, llm_calls: 0};
const tokens = {input_tokens: 0, output_tokens: 0, cost_usd: '0'};
const llmCall = {call_id: 'c', llm: 'x/y', provider_model: 'y', request: {}, usage: null};
const charges = {reserved_usd: '0.01', cost_usd: '0.01', estimated: true, rates: {}};

it.each<[string, unknown, string]>([
  ['host.ready', {...router, startup_ms: 80}, 'Router is ready'],
  ['host.failed', {...call, error: failure('Exited.')}, 'LLM Call could not start: Exited.'],
  [
    'message.discarded',
    {from: {node_id: 'reviewer', port: 'revise'}, reason: 'no_connection', payload: 1},
    'Discarded: output revise has no connection',
  ],
  [
    'message.dropped',
    {message_id: 'm9', to: {node_id: 'proposer', port: 'in'}, reason: 'run_ending'},
    'Dropped before reaching Proposer: the run was ending',
  ],
  ['activation.failed', {error: failure('Too slow.'), duration_ms: 5}, 'Failed: Too slow.'],
  ['activation.cancelled', {reason: 'run_ending'}, 'Cancelled: run_ending'],
  [
    'component.called',
    {...call, error: failure('Bad reply.'), duration_ms: 3},
    'Failed: Bad reply.',
  ],
  ['report', {kind: 'state', content: {step: 2}}, 'Reported by LLM Call: {"step":2}'],
  [
    'run.finished',
    {
      status: 'stopped',
      reason: 'activation_limit',
      detail: 'The run reached its limit of 3 activations before Proposer could start.',
      totals: {...totals, ...tokens},
      dropped: 1,
    },
    'Stopped: activation limit reached. The run reached its limit of 3 activations before Proposer could start.',
  ],
  [
    'run.finished',
    {
      status: 'failed',
      reason: 'startup_failed',
      detail: '',
      totals: {...totals, ...tokens},
      dropped: 0,
    },
    'Failed: a component could not start',
  ],
])('summarizes %s', (kind, data, summary) => {
  const item = event(kind, data);
  expect(rowText(item, {names: activityNames(j3, catalog), events: [item]}).summary).toBe(summary);
});

it('summarizes a refused model call recorded before a model was resolved', () => {
  const data = {...llmCall, llm: null, provider_model: null, request: 'not json', ...charges};
  const refused = event('llm.called', {
    ...data,
    rates: null,
    error: null,
    status: 400,
    duration_ms: 1,
  });
  expect(rowText(refused, {names: activityNames(null, null), events: [refused]}).summary).toBe(
    'Unknown model · Error: no detail recorded',
  );
});

it('summarizes a failed model call with unknown usage', () => {
  const failed = event('llm.called', {
    ...llmCall,
    ...charges,
    error: failure('Refused.'),
    status: 502,
    duration_ms: 20,
  });
  const names = activityNames(null, null);
  expect(rowText(failed, {names, events: [failed]})).toMatchObject({
    summary: 'x/y · Error: Refused.',
    metrics: 'tokens unknown · $0.01 · 20 ms',
  });
  expect(names.node('reviewer')).toBe('reviewer');
  expect(names.reporter(event('report', {kind: 'step', content: 1}), [])).toBe('component');
});

it('totals a run still in progress from its events', () => {
  const partial = events.slice(0, 12);
  const result = activityTotals(partial, activityNames(null, null));
  expect(result.status).toBe('Running');
  expect(result.figures).toContainEqual(['LLM calls', '1']);
  expect(result.nodes.map((node) => [node.name, node.activations])).toEqual([
    ['story', 1],
    ['proposer', 1],
  ]);
  expect(activityTotals([], activityNames(null, null))).toMatchObject({
    status: 'Starting',
    nodes: [],
  });
});
