import {useEffect, useRef, useState} from 'react';
import type {ReactElement} from 'react';
import type {Catalog, GraphDocument, PointId} from '../../api/index.ts';
import {Icon, KindTile} from '../../ui/index.ts';
import type {Point} from './observation-points.ts';

export interface PanelProps {
  readonly document: GraphDocument;
  readonly catalog: Catalog;
  readonly observed: ReadonlySet<PointId>;
  /** The point whose activity the run panel shows, or null for every observed point. */
  readonly focus: PointId | null;
  readonly onObserve: (ids: readonly PointId[], observe: boolean) => void;
  readonly onFocus: (id: PointId | null) => void;
}

function PointIcon({icon}: {readonly icon: Point['icon']}): ReactElement | null {
  if (icon === null) return null;
  if (icon !== 'run' && icon !== 'connection') return <KindTile icon={icon} size="sm" />;
  return (
    <span className="tile tile-sm observation-tile" aria-hidden="true">
      <Icon name={icon === 'run' ? 'play' : 'connection'} size={13} />
    </span>
  );
}

/** Checked when every member is observed, mixed when only some are. */
function ObserveBox(props: PanelProps & {readonly point: Point}): ReactElement {
  const {point, observed} = props;
  const count = point.members.filter((id) => observed.has(id)).length;
  const all = count === point.members.length && count > 0;
  const box = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (box.current !== null) box.current.indeterminate = count > 0 && !all;
  });
  return (
    <input
      ref={box}
      type="checkbox"
      aria-label={`Observe ${point.title}`}
      checked={all}
      onChange={() => {
        props.onObserve(point.members, !all);
      }}
    />
  );
}

function PointName(props: PanelProps & {readonly point: Point}): ReactElement {
  const {point, focus} = props;
  return (
    <button
      type="button"
      className="observation-name"
      aria-pressed={focus === point.id}
      title="Show this point's activity"
      onClick={() => {
        props.onFocus(focus === point.id ? null : point.id);
      }}
    >
      <PointIcon icon={point.icon} />
      <span className="observation-text">
        <span className="observation-label">{point.title}</span>
        {point.icon !== null && <span className="observation-kind">{point.detail}</span>}
      </span>
    </button>
  );
}

function Unfold(props: {
  readonly title: string;
  readonly open: boolean;
  readonly onToggle: () => void;
}): ReactElement {
  return (
    <button
      type="button"
      className={props.open ? 'observation-expand open' : 'observation-expand'}
      aria-expanded={props.open}
      aria-label={`${props.open ? 'Hide' : 'Show'} what ${props.title} records`}
      onClick={props.onToggle}
    >
      <Icon name="chevron-down" size={14} />
    </button>
  );
}

function PointRow(props: PanelProps & {readonly point: Point}): ReactElement {
  const {point, focus} = props;
  const [open, setOpen] = useState(false);
  const nested = point.facets.length > 0;
  const toggle = (): void => {
    setOpen(!open);
  };
  return (
    <li className="observation-item">
      <div className={focus === point.id ? 'observation-point focused' : 'observation-point'}>
        <ObserveBox {...props} />
        <PointName {...props} />
        {nested && <Unfold title={point.title} open={open} onToggle={toggle} />}
      </div>
      {nested && open && (
        <ul className="observation-facets" aria-label={`What ${point.title} records`}>
          {point.facets.map((facet) => (
            <PointRow key={facet.id} {...props} point={facet} />
          ))}
        </ul>
      )}
    </li>
  );
}

/** A titled group of points: the run, the nodes or the connections. */
export function PointGroup(
  props: PanelProps & {readonly title: string; readonly points: readonly Point[]},
): ReactElement | null {
  if (props.points.length === 0) return null;
  return (
    <section className="palette-group" aria-label={props.title}>
      <h3>{props.title}</h3>
      <ul className="observation-list">
        {props.points.map((point) => (
          <PointRow key={point.id} {...props} point={point} />
        ))}
      </ul>
    </section>
  );
}
