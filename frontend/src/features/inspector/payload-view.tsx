import {useCallback} from 'react';
import type {ReactElement} from 'react';
import {OperatorClient} from '../../api/index.ts';
import type {RetainedPayload} from '../../api/index.ts';
import {useRead} from './use-read.ts';
import {ReadStatus} from './read-status.tsx';
import {FocusHeading} from './focus-heading.tsx';
import type {InspectionSource} from './types.ts';

type Props = InspectionSource & {
  readonly id: string;
  readonly focusRequest: number | undefined;
};

export function PayloadView({credential, run, id, focusRequest}: Props): ReactElement {
  const read = useCallback(
    (signal: AbortSignal) => new OperatorClient(credential).payload(run, id, signal),
    [credential, run, id],
  );
  const {data, error, refresh} = useRead(read);
  return (
    <section aria-label="Retained content">
      <FocusHeading request={focusRequest}>Retained content</FocusHeading>
      <ReadStatus error={error} loading={data === null && error === null} refresh={refresh} />
      {data !== null && <PayloadContent payload={data} />}
    </section>
  );
}

function PayloadContent({payload}: {readonly payload: RetainedPayload}): ReactElement {
  const available = payload.status === 'present' || payload.status === 'redacted';
  return (
    <>
      <p>
        {payload.payload_id} · Capture state: {payload.status}
      </p>
      {payload.reason !== null && <p>Reason: {payload.reason}</p>}
      {available ? (
        <pre>{JSON.stringify(payload.content, null, 2)}</pre>
      ) : (
        <p>Content unavailable.</p>
      )}
    </>
  );
}
