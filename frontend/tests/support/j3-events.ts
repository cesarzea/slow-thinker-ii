import {totals} from './runs.ts';

type Data = Record<string, unknown>;
interface Draft {
  readonly kind: string;
  readonly node: string | null;
  readonly activation: string | null;
  readonly data: Data;
  readonly evidence?: 'reported';
}

const STORY = 'A cat tried to learn to fly.';
const FUNNY = 'Simulated reply to: A cat tried to learn to fly.';
type Step = (kind: string, node: string | null, activation: string | null, data: Data) => Draft;
const step: Step = (kind, node, activation, data) => ({kind, node, activation, data});
const sent = (id: string, from: string, to: string, activation: string, payload: unknown) => {
  const [fromNode = '', fromPort = ''] = from.split('.');
  const [toNode = '', toPort = ''] = to.split('.');
  return step('message.sent', fromNode, activation, {
    message_id: id,
    from: {node_id: fromNode, port: fromPort},
    to: {node_id: toNode, port: toPort},
    payload,
  });
};
const started = (node: string, activation: string, message: string | null, number: number) =>
  step('activation.started', node, activation, {message_id: message, number});
const completed = (node: string, activation: string, port: string | null, message = '') =>
  step('activation.completed', node, activation, {
    emitted: port === null ? [] : [{port, message_ids: [message]}],
    duration_ms: 1300,
  });
const llmCall = (node: string, activation: string, llm: string, user: string, reply: string) =>
  step('llm.called', node, activation, {
    call_id: `call-${activation}`,
    llm,
    provider_model: llm.split('/')[1] ?? llm,
    request: {
      model: llm,
      messages: [
        {role: 'system', content: 'Rewrite this story so that it is funny.'},
        {role: 'user', content: user},
      ],
      max_completion_tokens: 300,
    },
    response: {choices: [{message: {role: 'assistant', content: reply}}]},
    usage: {input: 38, cached_input: 0, cache_write: 0, output: 71},
    reserved_usd: '0.0002',
    cost_usd: '0.000031',
    estimated: false,
    rates: {input: '0.10', output: '0.50'},
    status: 200,
    duration_ms: 1300,
  });
const called = (node: string, activation: string, result: unknown) =>
  step('component.called', node, activation, {
    position: 'node',
    component: 'llm-call@1.0.0',
    operation: 'activate',
    arguments: {message: STORY},
    result,
    duration_ms: 1310,
  });
const routed = (activation: string, port: string, received: unknown) =>
  step('component.called', 'reviewer', activation, {
    position: 'output',
    component: 'router@1.0.0',
    operation: 'select_output',
    arguments: {received, node_input: FUNNY},
    result: {port, payload: FUNNY},
    duration_ms: 4,
  });
const report: Draft = {
  ...step('report', 'proposer', 'a2', {kind: 'step', content: 'Messages built, one call.'}),
  evidence: 'reported',
};

const drafts: readonly Draft[] = [
  step('run.started', null, null, {
    graph_id: 'funny-story-with-review',
    graph_version: 1,
    input: STORY,
    limits: {
      max_activations: 10,
      max_running_nodes: 4,
      time_limit_seconds: 120,
      budget_usd: '0.05',
    },
    budgets: {run_usd: '0.05', day_usd: '1.00', month_usd: '20.00'},
  }),
  step('host.ready', 'proposer', null, {
    position: 'node',
    component: 'llm-call@1.0.0',
    startup_ms: 80,
  }),
  step('run.running', null, null, {}),
  started('story', 'a1', null, 1),
  sent('m1', 'story.out', 'proposer.in', 'a1', STORY),
  completed('story', 'a1', 'out', 'm1'),
  started('proposer', 'a2', 'm1', 1),
  report,
  llmCall('proposer', 'a2', 'openai/gpt-6-luna', STORY, FUNNY),
  called('proposer', 'a2', {emissions: [{port: 'out', payload: FUNNY}]}),
  sent('m2', 'proposer.out', 'reviewer.in', 'a2', FUNNY),
  completed('proposer', 'a2', 'out', 'm2'),
  started('reviewer', 'a3', 'm2', 1),
  llmCall('reviewer', 'a3', 'deepseek/deepseek-flash', FUNNY, '{"score": 5}'),
  routed('a3', 'revise', {score: 5}),
  sent('m3', 'reviewer.revise', 'proposer.in', 'a3', FUNNY),
  completed('reviewer', 'a3', 'revise', 'm3'),
  started('proposer', 'a4', 'm3', 2),
  llmCall('proposer', 'a4', 'openai/gpt-6-luna', FUNNY, FUNNY),
  sent('m4', 'proposer.out', 'reviewer.in', 'a4', FUNNY),
  completed('proposer', 'a4', 'out', 'm4'),
  started('reviewer', 'a5', 'm4', 2),
  llmCall('reviewer', 'a5', 'deepseek/deepseek-flash', FUNNY, '{"score": 8}'),
  routed('a5', 'accepted', {score: 8}),
  sent('m5', 'reviewer.accepted', 'result.in', 'a5', FUNNY),
  completed('reviewer', 'a5', 'accepted', 'm5'),
  started('result', 'a6', 'm5', 1),
  step('run.result', 'result', 'a6', {name: 'Funny story', message_id: 'm5', payload: FUNNY}),
  completed('result', 'a6', null),
  step('run.finished', null, null, {
    status: 'completed',
    reason: null,
    detail: '',
    totals,
    dropped: 0,
  }),
];

/** The recorded J3 event log of a completed review loop, as served by the operator API. */
export const j3Events: readonly Data[] = drafts.map((draft, index) => ({
  run_id: 'run-1',
  seq: index + 1,
  at: new Date(Date.UTC(2026, 9, 4, 5, 0, 0, index * 200)).toISOString(),
  elapsed_ms: index * 200,
  kind: draft.kind,
  evidence: draft.evidence ?? 'observed',
  node_id: draft.node,
  activation_id: draft.activation,
  data: draft.data,
}));
