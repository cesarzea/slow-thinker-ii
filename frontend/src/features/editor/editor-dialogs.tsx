import type {ReactElement} from 'react';
import type {Catalog, GraphDocument, OperatorClient} from '../../api/index.ts';
import {NodeDialog} from './dialogs/node-dialog.tsx';
import {AddComponentDialog, RemoveComponentDialog} from './panel/component-dialogs.tsx';
import {
  embedComponent,
  embeddable,
  freePositions,
  providedConnections,
  removeEmbedded,
} from './state/embedding.ts';
import {declarationFor, embeddedAt} from './state/ports.ts';
import type {EmbeddedPosition} from './state/ports.ts';
import type {EditorModel} from './state/use-editor.ts';

export type OpenDialog =
  | {readonly kind: 'node'; readonly nodeId: string; readonly section: string}
  | {readonly kind: 'add-component'; readonly nodeId: string}
  | {
      readonly kind: 'remove-component';
      readonly nodeId: string;
      /** The output's component when absent. */
      readonly position?: EmbeddedPosition;
    };

interface Props {
  readonly dialog: OpenDialog | null;
  readonly editor: EditorModel;
  readonly client: OperatorClient;
  readonly catalog: Catalog;
  readonly close: () => void;
}
type Change = (update: (document: GraphDocument) => GraphDocument) => void;
type ComponentProps = Props & {readonly nodeId: string; readonly change: Change};

/** The dialog the editor has open, if any. */
export function EditorDialogs(props: Props): ReactElement | null {
  const {dialog, editor, close} = props;
  const change: Change = (update) => {
    editor.dispatch({type: 'change', update});
    close();
  };
  switch (dialog?.kind) {
    case undefined:
      return null;
    case 'node':
      return <NodeEditing {...props} nodeId={dialog.nodeId} section={dialog.section} />;
    case 'add-component':
      return <AddDialog {...props} nodeId={dialog.nodeId} change={change} />;
    case 'remove-component':
      return (
        <RemoveDialog
          {...props}
          nodeId={dialog.nodeId}
          position={dialog.position ?? 'output'}
          change={change}
        />
      );
  }
}

function NodeEditing(
  props: Props & {readonly nodeId: string; readonly section: string},
): ReactElement {
  return (
    <NodeDialog
      client={props.client}
      document={props.editor.state.document}
      catalog={props.catalog}
      nodeId={props.nodeId}
      section={props.section}
      onApplied={(document, diagnostics) => {
        props.editor.dispatch({type: 'applied', document, diagnostics});
        props.close();
      }}
      onCancel={props.close}
    />
  );
}

function AddDialog(props: ComponentProps): ReactElement {
  const {document} = props.editor.state;
  const outgoing = document.connections.filter((item) => item.from.startsWith(`${props.nodeId}.`));
  const node = document.nodes.find((item) => item.id === props.nodeId);
  const free = node === undefined ? [] : freePositions(node);
  return (
    <AddComponentDialog
      components={embeddable(props.catalog, free)}
      outgoing={outgoing.length}
      onAdd={(declaration) => {
        props.change((value) => embedComponent(value, props.nodeId, declaration, props.catalog));
      }}
      onCancel={props.close}
    />
  );
}

function RemoveDialog(
  props: ComponentProps & {readonly position: EmbeddedPosition},
): ReactElement | null {
  const {document} = props.editor.state;
  const {position} = props;
  const node = document.nodes.find((item) => item.id === props.nodeId);
  const embedded = node === undefined ? undefined : embeddedAt(node, position);
  if (embedded === undefined) return null;
  const connections =
    position === 'output' ? providedConnections(document, props.nodeId, props.catalog) : [];
  return (
    <RemoveComponentDialog
      label={declarationFor(props.catalog, embedded.component)?.label ?? embedded.component}
      document={document}
      connections={connections}
      onConfirm={() => {
        props.change((value) => removeEmbedded(value, props.nodeId, props.catalog, position));
      }}
      onCancel={props.close}
    />
  );
}
