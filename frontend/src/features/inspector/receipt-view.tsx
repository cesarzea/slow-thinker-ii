import type {ReactElement} from 'react';
import type {CallDetails} from '../../api/index.ts';
import {moneyLabel} from '../../ui/index.ts';
import {EvidenceLink} from './evidence-link.tsx';
import type {InspectionLinks} from './types.ts';

type ReceiptProps = Pick<InspectionLinks, 'onPayload'> & {readonly call: CallDetails};

export function ReceiptView({call, onPayload}: ReceiptProps): ReactElement {
  return (
    <>
      <h4>Respuestas conservadas</h4>
      {call.receipts.items.length === 0 && <p>No hay respuestas registradas.</p>}
      <ul>
        {call.receipts.items.map((receipt) => (
          <li key={receipt.receipt_id}>
            <p>
              <time>{receipt.received_at}</time> · {receipt.succeeded ? 'Correcta' : 'Error'} ·{' '}
              {receipt.publish ? 'Aceptada para continuar' : 'No publicada como resultado'}
            </p>
            {receipt.reason !== null && <p>Motivo: {receipt.reason}</p>}
            {receipt.amount !== null && <p>Importe comunicado: {moneyLabel(receipt.amount)}</p>}
            <EvidenceLink identity={receipt.response_payload_id} select={onPayload}>
              Ver respuesta
            </EvidenceLink>
            <EvidenceLink identity={receipt.usage_payload_id} select={onPayload}>
              Ver uso comunicado
            </EvidenceLink>
          </li>
        ))}
      </ul>
    </>
  );
}
