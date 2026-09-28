import type {
  CallDetails,
  EventPage,
  RetainedPayload,
  ActivationDetails,
} from '../../src/api/index.ts';

export const events: EventPage = {
  run_id: 'run',
  through_sequence: 4,
  next_cursor: 'next-events',
  items: [
    {
      sequence: 1,
      event: 'run.created',
      received_at: '2026-09-28T12:00:00Z',
      call_id: null,
      payload_id: 'event:1',
    },
    {
      sequence: 3,
      event: 'call.requested',
      received_at: '2026-09-28T12:00:01Z',
      call_id: 'child',
      payload_id: 'event:3',
    },
  ],
};
export const childCall: CallDetails = {
  run_id: 'run',
  call_id: 'child',
  attempt_id: 'attempt',
  state: 'completed',
  reason: null,
  context: {
    caller: 'agent',
    parent_call_id: 'parent',
    target: {instance: 'model', operation: 'complete'},
    node_id: 'draft',
    activation_id: 'activation',
  },
  request_payload_id: 'request:child',
  pricing_payload_id: 'pricing:child',
  result_receipt_id: 'receipt',
  accounting: {
    state: 'settled',
    bound: '0.000000007',
    amount: '0.000000003',
    outstanding: '0.000000000',
    source: 'fixture',
    month_id: '2026-09',
  },
  receipts: {
    items: [
      {
        receipt_id: 'receipt',
        received_at: '2026-09-28T12:00:02Z',
        succeeded: true,
        publish: true,
        reason: null,
        response_payload_id: 'response:receipt',
        usage_payload_id: 'usage:receipt',
        amount: '0.000000003',
        source: 'fixture',
      },
    ],
    next_cursor: null,
  },
};

export function retained(identity: string): RetainedPayload {
  return {
    run_id: 'run',
    payload_id: identity,
    status: 'present',
    reason: null,
    size_bytes: 4,
    content: identity === 'response:receipt' ? null : {text: '<script>private input</script>'},
  };
}

export const activation: ActivationDetails = {
  run_id: 'run',
  activation_id: 'activation',
  node_id: 'draft',
  target: {instance: 'agent', operation: 'generate'},
  root_call_id: 'parent',
  state: 'completed',
  reason: null,
  input_payload_id: 'request:parent',
  output_payload_id: 'response:receipt',
  bindings_payload_id: 'bindings:parent',
  calls: {
    items: [
      {
        call_id: 'child',
        caller: 'agent',
        parent_call_id: 'parent',
        target: {instance: 'model', operation: 'complete'},
        state: 'completed',
      },
    ],
    next_cursor: 'next-activation',
  },
};
