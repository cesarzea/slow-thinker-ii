import type {ReactElement} from 'react';
import type {CallDetails} from '../../api/index.ts';
import {moneyLabel} from '../../ui/index.ts';
import {EvidenceLink} from './evidence-link.tsx';
import type {InspectionLinks} from './types.ts';

type ReceiptProps = Pick<InspectionLinks, 'onPayload'> & {readonly call: CallDetails};

export function ReceiptView({call, onPayload}: ReceiptProps): ReactElement {
  return (
    <>
      <h4>Retained responses</h4>
      {call.receipts.items.length === 0 && <p>No responses recorded.</p>}
      <ul>
        {call.receipts.items.map((receipt) => (
          <li key={receipt.receipt_id}>
            <p>
              <time>{receipt.received_at}</time> · {receipt.succeeded ? 'Succeeded' : 'Error'} ·{' '}
              {receipt.publish ? 'Accepted for continuation' : 'Not published as the result'}
            </p>
            {receipt.reason !== null && <p>Reason: {receipt.reason}</p>}
            {receipt.amount !== null && <p>Reported amount: {moneyLabel(receipt.amount)}</p>}
            <EvidenceLink identity={receipt.response_payload_id} select={onPayload}>
              View response
            </EvidenceLink>
            <EvidenceLink identity={receipt.usage_payload_id} select={onPayload}>
              View reported usage
            </EvidenceLink>
          </li>
        ))}
      </ul>
    </>
  );
}
