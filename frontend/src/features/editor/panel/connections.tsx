import type {ReactElement} from 'react';
import {Icon} from '../../../ui/index.ts';
import {MissingOutputs, Row} from './connection-rows.tsx';
import type {ConnectionsProps as Props} from './connection-rows.tsx';
import {staleConnections} from '../state/document.ts';
import {inputTargets, nodePorts, outgoingConnections, portLabel, splitRef} from '../state/ports.ts';

/** Connections into the node, each named by the output it comes from. */
function Incoming(props: Props): ReactElement | null {
  const incoming = props.document.connections.filter(
    (connection) => splitRef(connection.to)[0] === props.node.id,
  );
  if (incoming.length === 0) return null;
  return (
    <ul className="connection-list" aria-label="Incoming connections">
      {incoming.map((connection) => {
        const label = portLabel(props.document, connection.from);
        return (
          <Row
            key={`${connection.from}->${connection.to}`}
            direction="←"
            remove={`Remove connection from ${label}`}
            onRemove={() => {
              props.onDisconnect(connection);
            }}
          >
            {label}
          </Row>
        );
      })}
    </ul>
  );
}

/** Connections from the node's outputs; the port shows when the node has several. */
function Outgoing(props: Props & {readonly outputs: readonly string[]}): ReactElement | null {
  const outgoing = outgoingConnections(props.document, props.node, props.catalog).filter(
    (connection) => props.outputs.includes(splitRef(connection.from)[1]),
  );
  if (outgoing.length === 0) return null;
  return (
    <ul className="connection-list" aria-label="Outgoing connections">
      {outgoing.map((connection) => {
        const label = portLabel(props.document, connection.to);
        const port = splitRef(connection.from)[1];
        return (
          <Row
            key={`${connection.from}->${connection.to}`}
            direction="→"
            remove={`Remove connection to ${label}`}
            onRemove={() => {
              props.onDisconnect(connection);
            }}
          >
            {props.outputs.length > 1 && <span className="port-name">{port}</span>}
            {label}
          </Row>
        );
      })}
    </ul>
  );
}

/** “Connect <port> to”: a compact select of the input ports not connected yet. */
function ConnectPort(props: Props & {readonly port: string}): ReactElement {
  const from = `${props.node.id}.${props.port}`;
  const taken = props.document.connections.filter((item) => item.from === from);
  const targets = inputTargets(props.document, props.catalog).filter(
    (target) => !taken.some((item) => item.to === target.ref),
  );
  return (
    <label className="connect-port">
      <Icon name="plus" size={14} />
      <select
        aria-label={`Connect ${props.port} to`}
        value=""
        onChange={(event) => {
          if (event.target.value !== '') props.onConnect(from, event.target.value);
        }}
      >
        <option value="">{`Connect ${props.port} to…`}</option>
        {targets.map((target) => (
          <option key={target.ref} value={target.ref}>
            {target.label}
          </option>
        ))}
      </select>
    </label>
  );
}

/** Connections into the node and from its outputs, made and removed here. */
export function Connections(props: Props): ReactElement {
  const outputs = nodePorts(props.node, props.catalog).outputs;
  const stale = staleConnections(props.document, props.node.id, props.catalog);
  return (
    <section className="inspector-section" aria-label="Connections">
      <h3 className="panel-title">Connections</h3>
      <div className="connection-cells">
        <Incoming {...props} />
        <Outgoing {...props} outputs={outputs} />
        <MissingOutputs {...props} connections={stale} />
        {outputs.map((port) => (
          <ConnectPort key={port} {...props} port={port} />
        ))}
      </div>
      {outputs.length === 0 && <p className="muted">This node has no outputs.</p>}
    </section>
  );
}
