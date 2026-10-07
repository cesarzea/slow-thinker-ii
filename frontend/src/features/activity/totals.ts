import type {EventOf, RunEvent, RunEventKind, RunTotals} from '../../api/index.ts';
import {budgetShare, durationLabel, moneyLabel, runStatusText, sumMoney} from '../../ui/index.ts';
import type {Names} from './names.ts';

export interface NodeTotals {
  readonly nodeId: string;
  readonly name: string;
  readonly activations: number;
  readonly cost: string | null;
}
export interface ActivityTotals {
  readonly status: string;
  readonly figures: readonly (readonly [string, string])[];
  readonly nodes: readonly NodeTotals[];
}

function ofKind<K extends RunEventKind>(events: readonly RunEvent[], kind: K): EventOf<K>[] {
  return events.filter((event): event is EventOf<K> => event.kind === kind);
}

function status(events: readonly RunEvent[]): string {
  const finished = ofKind(events, 'run.finished')[0];
  if (finished !== undefined) return runStatusText(finished.data.status, finished.data.reason);
  return ofKind(events, 'run.running').length > 0 ? 'Running' : 'Starting';
}

function nodeTotals(events: readonly RunEvent[], names: Names): NodeTotals[] {
  const started = ofKind(events, 'activation.started');
  const calls = ofKind(events, 'llm.called');
  const ids =
    names.nodes.length > 0
      ? names.nodes.map((node) => node.id)
      : [...new Set(started.map((event) => event.node_id ?? ''))];
  return ids.map((nodeId) => {
    const costs = calls.filter((call) => call.node_id === nodeId).map((call) => call.data.cost_usd);
    return {
      nodeId,
      name: names.node(nodeId),
      activations: started.filter((event) => event.node_id === nodeId).length,
      cost: costs.length === 0 ? null : sumMoney(costs),
    };
  });
}

function counted(events: readonly RunEvent[]): RunTotals {
  const calls = ofKind(events, 'llm.called');
  const tokens = (side: 'input' | 'output'): number =>
    calls.reduce((sum, call) => sum + (call.data.usage?.[side] ?? 0), 0);
  return {
    duration_ms: events.at(-1)?.elapsed_ms ?? 0,
    activations: ofKind(events, 'activation.started').length,
    messages: ofKind(events, 'message.sent').length,
    llm_calls: calls.length,
    input_tokens: tokens('input'),
    output_tokens: tokens('output'),
    cost_usd: sumMoney(calls.map((call) => call.data.cost_usd)),
  };
}

function figures(totals: RunTotals, budget: string | undefined): (readonly [string, string])[] {
  const cost = totals.cost_usd;
  const share =
    budget === undefined ? '—' : `${budgetShare(cost, budget)} of ${moneyLabel(budget)}`;
  return [
    ['Duration', durationLabel(totals.duration_ms)],
    ['Activations', String(totals.activations)],
    ['Messages', String(totals.messages)],
    ['LLM calls', String(totals.llm_calls)],
    ['Tokens in / out', `${String(totals.input_tokens)} / ${String(totals.output_tokens)}`],
    ['Cost', moneyLabel(cost)],
    ['Budget used', share],
  ];
}

/** Status, duration, counts, tokens, cost, budget used and per-node figures of a run. */
export function activityTotals(events: readonly RunEvent[], names: Names): ActivityTotals {
  const totals = ofKind(events, 'run.finished')[0]?.data.totals ?? counted(events);
  const budget = ofKind(events, 'run.started')[0]?.data.limits.budget_usd;
  return {
    status: status(events),
    figures: figures(totals, budget),
    nodes: nodeTotals(events, names),
  };
}
