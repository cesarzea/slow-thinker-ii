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
        {context.caller ?? 'Orquestador'} → {context.target.instance}.{context.target.operation}
      </p>
      <p>
        Estado: {call.state}
        {call.reason !== null && ` · ${call.reason}`}
      </p>
      <p>
        Nodo: {context.node_id ?? 'Sin nodo asociado'} · Activación:{' '}
        {context.activation_id ?? 'No aplicable'}
      </p>
      <CallLinks call={call} onCall={onCall} onPayload={onPayload} onActivation={onActivation} />
      <CallCost cost={call.accounting} />
    </>
  );
}

function CallCost({cost}: {readonly cost: CallDetails['accounting']}): ReactElement {
  if (cost === null) return <p>Sin cargo directo registrado para esta llamada.</p>;
  return (
    <p>
      Coste propio: {cost.amount === null ? 'Sin importe confirmado' : moneyLabel(cost.amount)} ·{' '}
      {moneyLabel(cost.outstanding)} pendiente · Estado contable: {cost.state} · Mes:{' '}
      {cost.month_id}
      {cost.source !== null && ` · Fuente: ${cost.source}`}
    </p>
  );
}

function CallLinks({call, onCall, onPayload, onActivation}: SummaryProps): ReactElement {
  const {context} = call;
  return (
    <>
      <EvidenceLink identity={context.activation_id} select={onActivation}>
        Ver activación
      </EvidenceLink>
      <EvidenceLink identity={context.parent_call_id} select={onCall}>
        Ver llamada de origen
      </EvidenceLink>
      <EvidenceLink identity={call.request_payload_id} select={onPayload}>
        Ver argumentos
      </EvidenceLink>
      <EvidenceLink identity={call.pricing_payload_id} select={onPayload}>
        Ver base de cálculo
      </EvidenceLink>
    </>
  );
}
