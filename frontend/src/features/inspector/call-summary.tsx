import type {ReactElement} from 'react';
import type {CallDetails} from '../../api/index.ts';
import {moneyLabel} from '../../ui/index.ts';
import {EvidenceLink} from './evidence-link.tsx';
import type {InspectionLinks} from './types.ts';

type SummaryProps = InspectionLinks & {
  readonly call: CallDetails;
  readonly onActivation: (id: string) => void;
};

export function CallSummary({call, onCall, onPayload, onActivation}: SummaryProps): ReactElement {
  const {context} = call;
  return (
    <>
      <p>
        {context.caller ?? 'Orchestrator'} → {context.target.instance}.{context.target.operation}
      </p>
      <p>
        State: {call.state}
        {call.reason !== null && ` · ${call.reason}`}
      </p>
      <p>
        Node: {context.node_id ?? 'No associated node'} · Activation:{' '}
        {context.activation_id ?? 'Not applicable'}
      </p>
      <CallLinks call={call} onCall={onCall} onPayload={onPayload} onActivation={onActivation} />
      <CallCost cost={call.accounting} />
    </>
  );
}

function CallCost({cost}: {readonly cost: CallDetails['accounting']}): ReactElement {
  if (cost === null) return <p>No direct charge recorded for this call.</p>;
  return (
    <p>
      Own cost: {cost.amount === null ? 'No confirmed amount' : moneyLabel(cost.amount)} ·{' '}
      {moneyLabel(cost.outstanding)} pending · Accounting state: {cost.state} · Month:{' '}
      {cost.month_id}
      {cost.source !== null && ` · Source: ${cost.source}`}
    </p>
  );
}

function CallLinks({call, onCall, onPayload, onActivation}: SummaryProps): ReactElement {
  const {context} = call;
  return (
    <>
      <EvidenceLink identity={context.activation_id} select={onActivation}>
        View activation
      </EvidenceLink>
      <EvidenceLink identity={context.parent_call_id} select={onCall}>
        View parent call
      </EvidenceLink>
      <EvidenceLink identity={call.request_payload_id} select={onPayload}>
        View arguments
      </EvidenceLink>
      <EvidenceLink identity={call.pricing_payload_id} select={onPayload}>
        View pricing basis
      </EvidenceLink>
    </>
  );
}
