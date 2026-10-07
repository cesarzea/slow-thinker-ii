import type {ReactElement, ReactNode} from 'react';
import type {Catalog, Connection, GraphDocument, GraphNode} from '../../../api/index.ts';
import {IconButton} from '../../../ui/index.ts';
import {portLabel, splitRef} from '../state/ports.ts';

export interface ConnectionsProps {
  readonly document: GraphDocument;
  readonly catalog: Catalog;
  readonly node: GraphNode;
  readonly onConnect: (from: string, to: string) => void;
  readonly onDisconnect: (connection: Connection) => void;
}

/** One connection: where it leads, and × to remove it. */
export function Row(props: {
  readonly direction: '←' | '→';
  readonly children: ReactNode;
  readonly remove: string;
  readonly onRemove: () => void;
}): ReactElement {
  return (
    <li className="connection-row">
      <span className="direction" aria-hidden="true">
        {props.direction}
      </span>
      <span className="connection-text">{props.children}</span>
      <IconButton icon="close" size="sm" label={props.remove} onClick={props.onRemove} />
    </li>
  );
}

/** Connections from outputs the node no longer has, so they can be removed. */
export function MissingOutputs(
  props: ConnectionsProps & {readonly connections: readonly Connection[]},
): ReactElement | null {
  if (props.connections.length === 0) return null;
  return (
    <ul className="connection-list missing" aria-label="Connections from missing outputs">
      {props.connections.map((connection) => {
        const label = portLabel(props.document, connection.to);
        return (
          <Row
            key={`${connection.from}->${connection.to}`}
            direction="→"
            remove={`Remove connection to ${label}`}
            onRemove={() => {
              props.onDisconnect(connection);
            }}
          >
            {`From missing output “${splitRef(connection.from)[1]}” to ${label}`}
          </Row>
        );
      })}
    </ul>
  );
}
