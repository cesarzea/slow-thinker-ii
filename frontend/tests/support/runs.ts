const at = '2026-10-04T05:00:00.000Z';

export const usageBody = {
  day: {key: '2026-10-04', limit_usd: '1.00', used_usd: '0.000083'},
  month: {key: '2026-10', limit_usd: '20', used_usd: '0.5'},
};

export const totals = {
  duration_ms: 6000,
  activations: 6,
  messages: 5,
  llm_calls: 4,
  input_tokens: 412,
  output_tokens: 173,
  cost_usd: '0.000083',
};

type Fields = Readonly<Record<string, unknown>>;

export function runSummary(fields: Fields = {}): Record<string, unknown> {
  return {
    run_id: 'run-1',
    graph_id: 'funny-story-with-review',
    version: 1,
    change: 1,
    status: 'completed',
    reason: null,
    detail: '',
    created_at: at,
    ended_at: at,
    totals,
    ...fields,
  };
}

export function runDetail(fields: Fields = {}): Record<string, unknown> {
  return {
    ...runSummary(),
    results: [{node_id: 'result', name: 'Funny story', payload: 'Simulated reply to: a story', at}],
    activations_by_node: {story: 1, proposer: 2, reviewer: 2, result: 1},
    messages_by_connection: {
      'story.out -> proposer.in': 1,
      'proposer.out -> reviewer.in': 2,
      'reviewer.revise -> proposer.in': 1,
      'reviewer.accepted -> result.in': 1,
    },
    ...fields,
  };
}

export function versionBody(document: unknown, version = 1): Record<string, unknown> {
  return {
    graph_id: (document as {id: string}).id,
    version,
    branch: 'main',
    parent: version > 1 ? version - 1 : null,
    change: version,
    created_at: at,
    document,
  };
}
