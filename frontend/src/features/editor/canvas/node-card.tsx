import {useEffect, useRef} from 'react';
import type {ReactElement} from 'react';
import {useUpdateNodeInternals} from '@xyflow/react';
import type {NodeProps} from '@xyflow/react';
import {Icon, KindTile} from '../../../ui/index.ts';
import type {IconName} from '../../../ui/index.ts';
import type {ComponentIcon} from '../../../api/index.ts';
import {PortRail, PortRow} from './card-ports.tsx';
import {useNodeActions} from './node-actions.ts';
import type {CardBand, CardData, CardNode} from './types.ts';

const BAND_ICONS: Readonly<Record<ComponentIcon, IconName>> = {
  trigger: 'trigger',
  agent: 'llm',
  router: 'router',
  output: 'output',
  memory: 'memory',
  component: 'component',
};

/** The embedded component's label, with the ports it provides listed under it. */
function Band({data, band}: {readonly data: CardData; readonly band: CardBand}): ReactElement {
  return (
    <div className="card-band">
      <span className="band-label">
        <Icon name={BAND_ICONS[band.icon]} size={12} />
        {band.label}
      </span>
      <PortRow data={data} band />
    </div>
  );
}

/**
 * Handles change when ports are renamed or move to another side without the card changing
 * size; React Flow must then measure them again. The first measurement is left to React Flow,
 * which frames all nodes.
 */
function usePortRefresh(id: string, data: CardData): void {
  const update = useUpdateNodeInternals();
  const ports = [
    ...data.ports.map((port) => [port.kind, port.name, port.side].join(':')),
    data.band?.label ?? '',
  ].join('|');
  const measured = useRef(ports);
  useEffect(() => {
    if (measured.current === ports) return;
    measured.current = ports;
    update(id);
  }, [id, ports, update]);
}

function CardValues({values}: {readonly values: CardData['values']}): ReactElement | null {
  if (values.length === 0) return null;
  return (
    <div className="card-values">
      {values.map((value, index) => (
        <span
          key={`${String(index)}:${value.text}`}
          className={value.chip ? 'card-chip' : 'card-value'}
        >
          {value.text}
        </span>
      ))}
    </div>
  );
}

/** On a selected card of an editable canvas: delete it, at its top right corner. */
function DeleteButton({
  id,
  name,
}: {
  readonly id: string;
  readonly name: string;
}): ReactElement | null {
  const actions = useNodeActions();
  if (actions === null) return null;
  return (
    <button
      type="button"
      className="card-delete nodrag nopan"
      aria-label={`Delete ${name}`}
      title={`Delete ${name}`}
      onClick={(event) => {
        event.stopPropagation();
        actions.remove(id);
      }}
    >
      <Icon name="trash" size={12} />
    </button>
  );
}

/** The node's memory under its values, as its own declaration names it. */
function MemoryChip({text}: {readonly text: string | null}): ReactElement | null {
  if (text === null) return null;
  return (
    <span className="card-memory">
      <Icon name="memory" size={12} />
      {text}
    </span>
  );
}

/** The kind tile, the kind and the node's name. */
function CardHead({data}: {readonly data: CardData}): ReactElement {
  return (
    <div className="card-head">
      <KindTile icon={data.icon} />
      <div className="card-titles">
        <span className="card-kind">{data.label}</span>
        <strong className="card-name">{data.name}</strong>
      </div>
    </div>
  );
}

/**
 * A node on the canvas: kind tile, kind and name, card values, the ports row and the band of
 * an embedded component; ports placed on the top or bottom edge sit there.
 */
export function NodeCard({id, data, selected}: NodeProps<CardNode>): ReactElement {
  usePortRefresh(id, data);
  const classes = ['node-card', selected ? 'selected' : '', data.problem === null ? '' : 'invalid'];
  return (
    <div className={classes.join(' ').trim()}>
      <PortRail data={data} side="top" />
      <CardHead data={data} />
      <CardValues values={data.values} />
      <MemoryChip text={data.memory} />
      <PortRow data={data} band={false} />
      {data.band !== null && <Band data={data} band={data.band} />}
      {data.problem !== null && <span className="card-problem">{data.problem}</span>}
      <PortRail data={data} side="bottom" />
      {selected && <DeleteButton id={id} name={data.name} />}
      {data.activations !== null && (
        <span className="card-count" title="Activations">
          {data.activations}
        </span>
      )}
    </div>
  );
}
