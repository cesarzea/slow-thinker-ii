import type {ReactElement} from 'react';
import type {
  Catalog,
  ComponentIcon,
  Diagnostic,
  GraphDocument,
  GraphNode,
} from '../../../api/index.ts';
import {IconButton, KindTile} from '../../../ui/index.ts';
import {flowOrder} from '../state/arrange.ts';
import {
  declarationFor,
  nodePorts,
  outgoingConnections,
  portLabel,
  splitRef,
} from '../state/ports.ts';

interface EntryProps {
  readonly node: GraphNode;
  readonly document: GraphDocument;
  readonly catalog: Catalog;
  readonly problems: number;
  readonly selected: boolean;
  readonly onSelect?: (nodeId: string) => void;
  readonly onDelete?: (nodeId: string) => void;
}

/** Where a node's outputs lead, “accepted → Funny story · in”. */
function Connections({node, document, catalog}: EntryProps): ReactElement | null {
  const outgoing = outgoingConnections(document, node, catalog);
  if (outgoing.length === 0) return null;
  const several = nodePorts(node, catalog).outputs.length > 1;
  return (
    <ul className="outline-connections" aria-label={`Connections from ${node.name}`}>
      {outgoing.map((item) => (
        <li key={`${item.from}->${item.to}`}>
          {several && <span className="port-name">{splitRef(item.from)[1]}</span>}
          <span aria-hidden="true">→</span> {portLabel(document, item.to)}
        </li>
      ))}
    </ul>
  );
}

function kindOf(catalog: Catalog, node: GraphNode): {label: string; icon: ComponentIcon} {
  const declaration = declarationFor(catalog, node.component);
  return {label: declaration?.label ?? node.component, icon: declaration?.icon ?? 'component'};
}

const errorCount = (diagnostics: readonly Diagnostic[], id: string): number =>
  diagnostics.filter((item) => item.node_id === id && item.severity === 'error').length;

const problemText = (count: number): string =>
  count === 1 ? '1 problem' : `${String(count)} problems`;

function DeleteEntry({node, onDelete}: EntryProps): ReactElement | null {
  if (onDelete === undefined) return null;
  return (
    <span className="outline-delete">
      <IconButton
        icon="trash"
        label={`Delete ${node.name}`}
        size="sm"
        tone="danger"
        onClick={() => {
          onDelete(node.id);
        }}
      />
    </span>
  );
}

function OutlineEntry(props: EntryProps): ReactElement {
  const {node} = props;
  const kind = kindOf(props.catalog, node);
  return (
    <li className={props.selected ? 'outline-entry selected' : 'outline-entry'}>
      <button
        type="button"
        className="outline-node"
        aria-current={props.selected ? 'true' : undefined}
        onClick={() => {
          props.onSelect?.(node.id);
        }}
      >
        <KindTile icon={kind.icon} size="sm" />
        <span className="outline-name">{node.name}</span>
        <span className="outline-kind">{kind.label}</span>
        {props.problems > 0 && (
          <span className="outline-problems">{problemText(props.problems)}</span>
        )}
      </button>
      <DeleteEntry {...props} />
      <Connections {...props} />
    </li>
  );
}

function orderedNodes(document: GraphDocument, catalog: Catalog): GraphNode[] {
  return flowOrder(document, catalog).flatMap(
    (id) => document.nodes.find((node) => node.id === id) ?? [],
  );
}

interface OutlineProps {
  readonly document: GraphDocument;
  readonly catalog: Catalog;
  readonly diagnostics?: readonly Diagnostic[];
  readonly selected?: string | null;
  /** Selecting and deleting a node; the editor's outline only. */
  readonly onSelect?: (nodeId: string) => void;
  readonly onDelete?: (nodeId: string) => void;
}

/** The selection and deletion an entry offers, only those the outline was given. */
function entryActions(props: OutlineProps): Pick<EntryProps, 'onSelect' | 'onDelete'> {
  return {
    ...(props.onSelect === undefined ? {} : {onSelect: props.onSelect}),
    ...(props.onDelete === undefined ? {} : {onDelete: props.onDelete}),
  };
}

/** The nodes in the order the graph flows, with their problems and connections. */
export function Outline(props: OutlineProps): ReactElement {
  const {document, diagnostics = []} = props;
  const ordered = orderedNodes(document, props.catalog);
  const entry = (node: GraphNode): ReactElement => (
    <OutlineEntry
      key={node.id}
      node={node}
      document={document}
      catalog={props.catalog}
      problems={errorCount(diagnostics, node.id)}
      selected={props.selected === node.id}
      {...entryActions(props)}
    />
  );
  return (
    <div className="outline">
      {ordered.length === 0 ? <p className="muted">The graph has no nodes yet.</p> : null}
      <ol className="outline-list" aria-label="Outline">
        {ordered.map(entry)}
      </ol>
    </div>
  );
}
