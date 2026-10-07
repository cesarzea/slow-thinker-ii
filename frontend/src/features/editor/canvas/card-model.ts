import type {Catalog, GraphDocument, GraphNode} from '../../../api/index.ts';
import {portSide} from '../state/port-sides.ts';
import type {PortKind} from '../state/port-sides.ts';
import {embeddedOutput, nodePorts, portLabel} from '../state/ports.ts';
import type {CardPort} from './types.ts';

/** "<node> · <port>" of each port connected to this one. */
function links(document: GraphDocument, ref: string, kind: PortKind): string[] {
  return document.connections.flatMap((connection) => {
    const [own, other] =
      kind === 'output' ? [connection.from, connection.to] : [connection.to, connection.from];
    return own === ref ? [portLabel(document, other)] : [];
  });
}

/** The node's ports, inputs first, each on its side and with what it is connected to. */
export function cardPorts(document: GraphDocument, node: GraphNode, catalog: Catalog): CardPort[] {
  const {inputs, outputs} = nodePorts(node, catalog);
  const embedded = embeddedOutput(node) !== undefined;
  const port = (name: string, kind: PortKind): CardPort => ({
    name,
    kind,
    side: portSide(document, node.id, name, kind),
    band: embedded && kind === 'output',
    links: links(document, `${node.id}.${name}`, kind),
  });
  return [
    ...inputs.map((name) => port(name, 'input')),
    ...outputs.map((name) => port(name, 'output')),
  ];
}
