import type {ReactElement} from 'react';
import type {ActivationDetails} from '../../api/index.ts';
import {EvidenceLink} from './evidence-link.tsx';
import type {InspectionLinks} from './types.ts';

type Props = InspectionLinks & {readonly activation: ActivationDetails};

export function ActivationSummary({activation, onCall, onPayload}: Props): ReactElement {
  return (
    <>
      <p>
        Agent: {activation.target.instance} · Node: {activation.node_id ?? 'Not recorded'}
      </p>
      <p>
        State: {activation.state}
        {activation.reason !== null && ` · ${activation.reason}`}
      </p>
      <EvidenceLink identity={activation.input_payload_id} select={onPayload}>
        View effective input
      </EvidenceLink>
      <EvidenceLink identity={activation.output_payload_id} select={onPayload}>
        View published output
      </EvidenceLink>
      {activation.output_payload_id === null && <p>No output was published for this activation.</p>}
      <EvidenceLink identity={activation.bindings_payload_id} select={onPayload}>
        View input provenance
      </EvidenceLink>
      <EvidenceLink identity={activation.root_call_id} select={onCall}>
        View root call
      </EvidenceLink>
      <ActivationCalls calls={activation.calls.items} onCall={onCall} />
    </>
  );
}

function ActivationCalls({
  calls,
  onCall,
}: Pick<InspectionLinks, 'onCall'> & {
  readonly calls: ActivationDetails['calls']['items'];
}): ReactElement {
  return (
    <>
      <h4>Calls for this activation</h4>
      <ul>
        {calls.map((call) => (
          <li key={call.call_id}>
            {call.caller ?? 'Orchestrator'} → {call.target.instance}.{call.target.operation} ·{' '}
            {call.state}{' '}
            <EvidenceLink identity={call.call_id} select={onCall}>
              View call
            </EvidenceLink>
          </li>
        ))}
      </ul>
    </>
  );
}
