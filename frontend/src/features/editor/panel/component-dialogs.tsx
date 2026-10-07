import type {ReactElement} from 'react';
import type {ComponentDeclaration, Connection, GraphDocument} from '../../../api/index.ts';
import {ActionButton, Dialog} from '../../../ui/index.ts';
import {portLabel} from '../state/ports.ts';

function ComponentChoices(props: {
  readonly components: readonly ComponentDeclaration[];
  readonly onAdd: (declaration: ComponentDeclaration) => void;
}): ReactElement {
  return (
    <ul className="component-choices">
      {props.components.map((component) => (
        <li key={`${component.type}@${component.version}`}>
          <ActionButton
            action={() => {
              props.onAdd(component);
            }}
          >
            {component.label}
          </ActionButton>
          <span className="muted">{component.description}</span>
        </li>
      ))}
    </ul>
  );
}

/** Lists the components that can be embedded in a node: at its output, or as its memory. */
export function AddComponentDialog(props: {
  readonly components: readonly ComponentDeclaration[];
  readonly outgoing: number;
  readonly onAdd: (declaration: ComponentDeclaration) => void;
  readonly onCancel: () => void;
}): ReactElement {
  return (
    <Dialog title="Add component" onClose={props.onCancel}>
      <p className="dialog-description">
        A component at the node&apos;s output receives each result and chooses the output that
        carries it. A memory adds the node&apos;s earlier exchanges to each new message.
      </p>
      {props.outgoing > 0 &&
        props.components.some((item) => !item.placements.includes('memory')) && (
          <p className="field-note">
            The node&apos;s current outputs are replaced, so its outgoing connections are removed.
          </p>
        )}
      <ComponentChoices components={props.components} onAdd={props.onAdd} />
    </Dialog>
  );
}

function RemovedConnections(props: {
  readonly document: GraphDocument;
  readonly connections: readonly Connection[];
}): ReactElement {
  if (props.connections.length === 0) return <p>No connections will be removed.</p>;
  const label = (ref: string): string => portLabel(props.document, ref);
  return (
    <>
      <p>These connections will be removed:</p>
      <ul aria-label="Connections to remove">
        {props.connections.map((item) => (
          <li key={`${item.from}->${item.to}`}>{`${label(item.from)} → ${label(item.to)}`}</li>
        ))}
      </ul>
    </>
  );
}

/** Confirms removing an embedded component and lists the connections that go with it. */
export function RemoveComponentDialog(props: {
  readonly label: string;
  readonly document: GraphDocument;
  readonly connections: readonly Connection[];
  readonly onConfirm: () => void;
  readonly onCancel: () => void;
}): ReactElement {
  return (
    <Dialog title={`Remove ${props.label}`} onClose={props.onCancel}>
      <RemovedConnections document={props.document} connections={props.connections} />
      <div className="dialog-actions">
        <ActionButton action={props.onCancel}>Cancel</ActionButton>
        <ActionButton action={props.onConfirm} className="danger">
          Remove
        </ActionButton>
      </div>
    </Dialog>
  );
}
