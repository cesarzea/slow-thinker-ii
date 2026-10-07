import {useState} from 'react';
import type {ReactElement} from 'react';
import type {EventOf, RunEvent, RunEventKind} from '../../api/index.ts';
import {EvidenceContent, isJsonObject} from '../../ui/index.ts';
import type {Names} from './names.ts';
import {RowDetail} from './row-detail.tsx';
import {replyContent, rowText} from './summaries.ts';

/** Seconds since the run was admitted, to the millisecond. */
const elapsed = (ms: number): string => `${(ms / 1000).toFixed(3)} s`;

/** A call's result, or what it was given when it returned nothing, or its error. */
function callContent(event: EventOf<'component.called'>): unknown {
  const {error, result, arguments: given} = event.data;
  const empty = isJsonObject(result) && Object.keys(result).length === 0;
  return error ?? (empty ? given : result);
}

type Content<K extends RunEventKind> = (event: EventOf<K>) => unknown;

/** What passed through the point, by kind: a payload, a reply, a report or a call. */
const CONTENT: {readonly [K in RunEventKind]?: Content<K>} = {
  'message.sent': (event) => event.data.payload,
  'run.result': (event) => event.data.payload,
  'llm.called': (event) => event.data.error ?? replyContent(event.data.response),
  report: (event) => event.data.content,
  'component.called': callContent,
};

function content(event: RunEvent): unknown {
  const read = CONTENT[event.kind] as Content<RunEventKind> | undefined;
  return read?.(event);
}

/** The recorded detail, shown on demand. */
function Detail({event}: {readonly event: RunEvent}): ReactElement {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        className="feed-more"
        aria-expanded={open}
        onClick={() => {
          setOpen(!open);
        }}
      >
        {open ? 'Hide details' : 'Details'}
      </button>
      {open && (
        <div className="feed-detail">
          <RowDetail event={event} />
        </div>
      )}
    </>
  );
}

/** One recorded event: its point, kind and time, what it carried, and its detail on demand. */
export function FeedItem(props: {
  readonly event: RunEvent;
  readonly events: readonly RunEvent[];
  readonly names: Names;
  readonly label: string;
}): ReactElement {
  const {event} = props;
  const text = rowText(event, {names: props.names, events: props.events});
  const value = content(event);
  return (
    <li className="feed-item">
      <div className="feed-head">
        <span className="feed-point">{props.label}</span>
        <span className="feed-kind">{text.label}</span>
        <span className="feed-time">{elapsed(event.elapsed_ms)}</span>
      </div>
      {value === undefined ? (
        <p className="feed-summary">{text.summary}</p>
      ) : (
        <div className="feed-content">
          <EvidenceContent value={value} />
        </div>
      )}
      <Detail event={event} />
    </li>
  );
}
