import type {ReactElement} from 'react';
import type {ActivationDetails} from '../../api/index.ts';
import {EvidenceLink} from './evidence-link.tsx';
import type {InspectionLinks} from './types.ts';

type Props = InspectionLinks & {readonly activation: ActivationDetails};

export function ActivationSummary({activation, onCall, onPayload}: Props): ReactElement {
  return (
    <>
      <p>
        Agente: {activation.target.instance} · Nodo: {activation.node_id ?? 'No registrado'}
      </p>
      <p>
        Estado: {activation.state}
        {activation.reason !== null && ` · ${activation.reason}`}
      </p>
      <EvidenceLink identity={activation.input_payload_id} select={onPayload}>
        Ver entrada efectiva
      </EvidenceLink>
      <EvidenceLink identity={activation.output_payload_id} select={onPayload}>
        Ver salida publicada
      </EvidenceLink>
      {activation.output_payload_id === null && (
        <p>No hay salida publicada para esta activación.</p>
      )}
      <EvidenceLink identity={activation.bindings_payload_id} select={onPayload}>
        Ver procedencia de entradas
      </EvidenceLink>
      <EvidenceLink identity={activation.root_call_id} select={onCall}>
        Ver llamada principal
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
      <h4>Llamadas de esta activación</h4>
      <ul>
        {calls.map((call) => (
          <li key={call.call_id}>
            {call.caller ?? 'Orquestador'} → {call.target.instance}.{call.target.operation} ·{' '}
            {call.state}{' '}
            <EvidenceLink identity={call.call_id} select={onCall}>
              Abrir llamada
            </EvidenceLink>
          </li>
        ))}
      </ul>
    </>
  );
}
