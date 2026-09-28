import {useCallback, useState} from 'react';
import type {ReactElement} from 'react';
import {OperatorClient} from '../../api/index.ts';
import type {EventPage} from '../../api/index.ts';
import {EvidenceLink} from './evidence-link.tsx';
import {useRead} from './use-read.ts';
import {ReadStatus, TracePages} from './read-status.tsx';
import type {InspectionSource, InspectionLinks, Paging} from './types.ts';

type Props = InspectionSource & InspectionLinks;

export function EventView(props: Props): ReactElement {
  const [cursor, onPage] = useState<string>();
  return (
    <section aria-label="Eventos registrados">
      <h3>Eventos registrados</h3>
      <EventRead key={cursor ?? 'first'} {...props} cursor={cursor} onPage={onPage} />
    </section>
  );
}

function EventRead(props: Props & Paging): ReactElement {
  const {credential, run, cursor} = props;
  const read = useCallback(
    (signal: AbortSignal) => new OperatorClient(credential).events(run, signal, cursor),
    [credential, run, cursor],
  );
  const {data, error, refresh} = useRead(read);
  return (
    <>
      <ReadStatus error={error} loading={data === null && error === null} refresh={refresh} />
      {data !== null && (
        <>
          <p>
            Lectura hasta el evento {data.through_sequence}. Vuelve al principio para ver nuevos
            eventos.
          </p>
          <EventTable page={data} onCall={props.onCall} onPayload={props.onPayload} />
          <TracePages cursor={cursor} next={data.next_cursor} onPage={props.onPage} />
        </>
      )}
    </>
  );
}

function EventTable({
  page,
  onCall,
  onPayload,
}: InspectionLinks & {readonly page: EventPage}): ReactElement {
  return (
    <div className="trace-table">
      <table>
        <thead>
          <tr>
            <th>Orden</th>
            <th>Evento</th>
            <th>Registrado</th>
            <th>Evidencia</th>
          </tr>
        </thead>
        <tbody>
          {page.items.map((event) => (
            <EventRow key={event.sequence} event={event} onCall={onCall} onPayload={onPayload} />
          ))}
        </tbody>
      </table>
      {page.items.length === 0 && <p>No hay eventos registrados.</p>}
    </div>
  );
}

function EventRow({
  event,
  onCall,
  onPayload,
}: InspectionLinks & {
  readonly event: EventPage['items'][number];
}): ReactElement {
  return (
    <tr>
      <td>{event.sequence}</td>
      <td>{event.event}</td>
      <td>
        <time>{event.received_at}</time>
      </td>
      <td>
        <EvidenceLink identity={event.call_id} select={onCall}>
          Ver llamada {event.sequence}
        </EvidenceLink>
        <EvidenceLink identity={event.payload_id} select={onPayload}>
          Ver contenido {event.sequence}
        </EvidenceLink>
      </td>
    </tr>
  );
}
