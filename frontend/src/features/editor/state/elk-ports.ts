import type {ElkPort} from 'elkjs/lib/elk-api.js';
import type {Catalog, GraphDocument, GraphNode} from '../../../api/index.ts';
import {portSide} from './port-sides.ts';
import type {PortKind, PortSide} from './port-sides.ts';
import {nodePorts} from './ports.ts';

interface Point {
  readonly x: number;
  readonly y: number;
}
/** A card's measured size and each handle's centre from its top left corner. */
export interface CardGeometry {
  readonly width: number;
  readonly height: number;
  readonly inputs: ReadonlyMap<string, Point>;
  readonly outputs: ReadonlyMap<string, Point>;
}
interface SidePort {
  readonly name: string;
  readonly kind: PortKind;
  readonly side: PortSide;
}

/** Used for a card not measured yet. */
export const DEFAULT_SIZE = {width: 220, height: 150};
const ELK_SIDES: Readonly<Record<PortSide, string>> = {
  left: 'WEST',
  right: 'EAST',
  top: 'NORTH',
  bottom: 'SOUTH',
};

export const portId = (node: string, kind: PortKind, port: string): string =>
  `${node}/${kind === 'input' ? 'in' : 'out'}/${port}`;

function sidePorts(document: GraphDocument, node: GraphNode, catalog: Catalog): SidePort[] {
  const {inputs, outputs} = nodePorts(node, catalog);
  const port = (name: string, kind: PortKind): SidePort => ({
    name,
    kind,
    side: portSide(document, node.id, name, kind),
  });
  return [
    ...inputs.map((name) => port(name, 'input')),
    ...outputs.map((name) => port(name, 'output')),
  ];
}

/** On its side's border: at the handle's measured centre, or spread evenly when unmeasured. */
function onBorder(
  side: PortSide,
  centre: Point | undefined,
  share: number,
  size: {width: number; height: number},
): Point {
  const down = centre?.y ?? size.height * share;
  const across = centre?.x ?? size.width * share;
  const points: Readonly<Record<PortSide, Point>> = {
    left: {x: 0, y: down},
    right: {x: size.width, y: down},
    top: {x: across, y: 0},
    bottom: {x: across, y: size.height},
  };
  return points[side];
}

/** The node's ports for ELK, fixed on their sides where the card draws them. */
export function elkPorts(
  document: GraphDocument,
  node: GraphNode,
  catalog: Catalog,
  geometry: CardGeometry | undefined,
): ElkPort[] {
  const ports = sidePorts(document, node, catalog);
  const size = geometry ?? DEFAULT_SIZE;
  return ports.map((port) => {
    const id = portId(node.id, port.kind, port.name);
    const peers = ports.filter((other) => other.side === port.side);
    const share = (peers.indexOf(port) + 1) / (peers.length + 1);
    const centre = (port.kind === 'input' ? geometry?.inputs : geometry?.outputs)?.get(port.name);
    return {
      id,
      ...onBorder(port.side, centre, share, size),
      width: 0,
      height: 0,
      layoutOptions: {'elk.port.side': ELK_SIDES[port.side]},
    };
  });
}
