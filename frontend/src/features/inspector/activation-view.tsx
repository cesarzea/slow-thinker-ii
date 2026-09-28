import {useCallback, useState} from 'react';
import type {ReactElement} from 'react';
import {OperatorClient} from '../../api/index.ts';
import {useRead} from './use-read.ts';
import {ReadStatus, TracePages} from './read-status.tsx';
import {ActivationSummary} from './activation-summary.tsx';
import type {InspectionSource, InspectionLinks, Paging} from './types.ts';

type Props = InspectionSource & InspectionLinks & {readonly id: string};

export function ActivationView(props: Props): ReactElement {
  const [cursor, onPage] = useState<string>();
  return (
    <section aria-label="Detalle de activación">
      <h3>
        Activación <code>{props.id}</code>
      </h3>
      <ActivationRead key={cursor ?? 'first'} {...props} cursor={cursor} onPage={onPage} />
    </section>
  );
}

function ActivationRead(props: Props & Paging): ReactElement {
  const {credential, run, id, cursor} = props;
  const read = useCallback(
    (signal: AbortSignal) => new OperatorClient(credential).activation(run, id, signal, cursor),
    [credential, run, id, cursor],
  );
  const {data, error, refresh} = useRead(read);
  return (
    <>
      <ReadStatus error={error} loading={data === null && error === null} refresh={refresh} />
      {data !== null && (
        <>
          <ActivationSummary activation={data} onCall={props.onCall} onPayload={props.onPayload} />
          <TracePages cursor={cursor} next={data.calls.next_cursor} onPage={props.onPage} />
        </>
      )}
    </>
  );
}
