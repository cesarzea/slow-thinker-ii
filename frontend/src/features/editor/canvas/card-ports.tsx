import type {KeyboardEvent, ReactElement, SyntheticEvent} from 'react';
import {Handle, Position} from '@xyflow/react';
import type {PortSide} from '../state/port-sides.ts';
import {usePortTip} from './port-tip.tsx';
import type {CardData, CardPort} from './types.ts';

const POSITIONS: Readonly<Record<PortSide, Position>> = {
  left: Position.Left,
  right: Position.Right,
  top: Position.Top,
  bottom: Position.Bottom,
};

function pressOnKey(event: KeyboardEvent<HTMLDivElement>): void {
  if (event.key !== 'Enter' && event.key !== ' ') return;
  event.preventDefault();
  event.stopPropagation();
  event.currentTarget.click();
}

/**
 * One handle per effective port on its side; hovered or focused, it shows the port's full name
 * and connections. In the editor it is a button named after node, kind and port.
 */
function PortHandle(props: {readonly data: CardData; readonly port: CardPort}): ReactElement {
  const {data, port} = props;
  const tips = usePortTip();
  const show = (event: SyntheticEvent<HTMLDivElement>): void => {
    tips?.show(port, event.currentTarget);
  };
  const hide = (): void => {
    tips?.hide();
  };
  const handle = {
    type: port.kind === 'input' ? 'target' : 'source',
    position: POSITIONS[port.side],
    id: port.name,
    onMouseEnter: show,
    onMouseLeave: hide,
  } as const;
  if (!data.interactive) return <Handle {...handle} isConnectable={false} />;
  return (
    <Handle
      {...handle}
      role="button"
      tabIndex={0}
      aria-label={`${data.name} ${port.kind} ${port.name}`}
      onKeyDown={pressOnKey}
      onFocus={show}
      onBlur={hide}
    />
  );
}

/** Ports placed on the top or bottom edge, spread evenly along it, named under or over. */
export function PortRail(props: {
  readonly data: CardData;
  readonly side: 'top' | 'bottom';
}): ReactElement | null {
  const ports = props.data.ports.filter((port) => port.side === props.side);
  if (ports.length === 0) return null;
  return (
    <ul className={`port-rail rail-${props.side}`}>
      {ports.map((port) => (
        <li key={`${port.kind}:${port.name}`} className={port.band ? 'port band' : 'port'}>
          <span className="port-label">{port.name}</span>
          <PortHandle data={props.data} port={port} />
        </li>
      ))}
    </ul>
  );
}

function PortList(props: {
  readonly data: CardData;
  readonly ports: readonly CardPort[];
  readonly side: 'left' | 'right';
}): ReactElement {
  return (
    <ul className={`ports ports-${props.side}`}>
      {props.ports.map((port) => (
        <li key={`${port.kind}:${port.name}`} className="port-row">
          <span className="port-label">{port.name}</span>
          <PortHandle data={props.data} port={port} />
        </li>
      ))}
    </ul>
  );
}

/**
 * The card's ports row: left ports listed at the left and right ports at the right, with
 * their handles on the card's edges; the band's ports, or the others.
 */
export function PortRow(props: {
  readonly data: CardData;
  readonly band: boolean;
}): ReactElement | null {
  const ports = props.data.ports.filter((port) => port.band === props.band);
  const side = (name: 'left' | 'right'): CardPort[] => ports.filter((port) => port.side === name);
  if (side('left').length + side('right').length === 0) return null;
  return (
    <div className="card-ports">
      <PortList data={props.data} ports={side('left')} side="left" />
      <PortList data={props.data} ports={side('right')} side="right" />
    </div>
  );
}
