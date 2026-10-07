import {useId, useState} from 'react';
import type {ReactElement} from 'react';
import type {RunEvent} from '../../api/index.ts';
import type {Names} from './names.ts';
import {RowDetail} from './row-detail.tsx';
import {rowText} from './summaries.ts';
import type {RowGroup} from './summaries.ts';

export type Filter = 'all' | 'message' | 'call';
const FILTERS: readonly (readonly [Filter, string])[] = [
  ['all', 'All'],
  ['message', 'Messages'],
  ['call', 'Calls'],
];

/** The timeline filter: All, Messages or Calls. */
export function FilterChoice(props: {
  readonly value: Filter;
  readonly onChange: (filter: Filter) => void;
}): ReactElement {
  const name = useId();
  return (
    <div role="radiogroup" aria-label="Show" className="filters">
      {FILTERS.map(([filter, label]) => (
        <label key={filter} className="radio">
          <input
            type="radio"
            name={name}
            checked={props.value === filter}
            onChange={() => {
              props.onChange(filter);
            }}
          />
          {label}
        </label>
      ))}
    </div>
  );
}

interface RowProps {
  readonly event: RunEvent;
  readonly events: readonly RunEvent[];
  readonly names: Names;
}

function RowButton(
  props: RowProps & {
    readonly open: boolean;
    readonly detail: string;
    readonly onToggle: () => void;
  },
): ReactElement {
  const {event} = props;
  const text = rowText(event, {names: props.names, events: props.events});
  return (
    <button
      type="button"
      aria-expanded={props.open}
      aria-controls={props.detail}
      onClick={props.onToggle}
    >
      <span className="row-time">{(event.elapsed_ms / 1000).toFixed(2)}</span>
      <span className="row-node">{props.names.node(event.node_id)}</span>
      <span className="row-kind">{text.label}</span>
      <span className="row-summary">{text.summary}</span>
      <span className="row-metrics">{text.metrics ?? ''}</span>
    </button>
  );
}

function Row(props: RowProps): ReactElement {
  const [open, setOpen] = useState(false);
  const detail = useId();
  const {event} = props;
  const toggle = (): void => {
    setOpen(!open);
  };
  return (
    <li className={`row ${event.evidence}`}>
      <RowButton {...props} open={open} detail={detail} onToggle={toggle} />
      {open && (
        <div
          id={detail}
          role="region"
          aria-label={`Details of event ${String(event.seq)}`}
          className="row-detail"
        >
          <RowDetail event={event} />
        </div>
      )}
    </li>
  );
}

function group(event: RunEvent, names: Names, events: readonly RunEvent[]): RowGroup {
  return rowText(event, {names, events}).group ?? 'other';
}

/** Every recorded event in sequence order; each row expands to its detail. */
export function Timeline(props: {
  readonly events: readonly RunEvent[];
  readonly names: Names;
  readonly filter: Filter;
}): ReactElement {
  const {events, names, filter} = props;
  const shown =
    filter === 'all' ? events : events.filter((event) => group(event, names, events) === filter);
  return (
    <ol className="timeline" aria-label="Timeline">
      {shown.map((event) => (
        <Row key={event.seq} event={event} events={events} names={names} />
      ))}
    </ol>
  );
}
