import {useCallback, useState} from 'react';
import type {ReactElement} from 'react';
import {OperatorClient} from '../../api/index.ts';
import {useRead} from './use-read.ts';
import {ReadStatus, TracePages} from './read-status.tsx';
import {CallSummary} from './call-summary.tsx';
import {ReceiptView} from './receipt-view.tsx';
import {ReportView} from './report-view.tsx';
import {FocusHeading} from './focus-heading.tsx';
import type {InspectionSource, InspectionLinks, Paging} from './types.ts';

type Props = InspectionSource &
  InspectionLinks & {
    readonly id: string;
    readonly onActivation: (id: string) => void;
    readonly focusRequest: number | undefined;
  };

export function CallView(props: Props): ReactElement {
  const [cursor, onPage] = useState<string>();
  return (
    <section aria-label="Detalle de llamada">
      <FocusHeading request={props.focusRequest}>
        Llamada <code>{props.id}</code>
      </FocusHeading>
      <CallRead key={cursor ?? 'first'} {...props} cursor={cursor} onPage={onPage} />
    </section>
  );
}

function CallRead(props: Props & Paging): ReactElement {
  const {credential, run, id, cursor} = props;
  const read = useCallback(
    (signal: AbortSignal) => new OperatorClient(credential).call(run, id, signal, cursor),
    [credential, run, id, cursor],
  );
  const {data, error, refresh} = useRead(read);
  return (
    <>
      <ReadStatus error={error} loading={data === null && error === null} refresh={refresh} />
      {data !== null && (
        <>
          <CallSummary
            call={data}
            onCall={props.onCall}
            onPayload={props.onPayload}
            onActivation={props.onActivation}
          />
          <ReceiptView call={data} onPayload={props.onPayload} />
          <ReportView reports={data.reports ?? []} onPayload={props.onPayload} />
          <TracePages cursor={cursor} next={data.receipts.next_cursor} onPage={props.onPage} />
        </>
      )}
    </>
  );
}
