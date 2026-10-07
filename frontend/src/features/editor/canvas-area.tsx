import {useMemo, useState} from 'react';
import type {ReactElement} from 'react';
import type {Catalog, GraphDocument} from '../../api/index.ts';
import {useCanvasInteraction} from './canvas/canvas-interaction.tsx';
import type {CanvasInteraction} from './canvas/canvas-interaction.tsx';
import {editorCanvas} from './canvas/canvas-model.ts';
import {CanvasToolbar} from './canvas/canvas-toolbar.tsx';
import {viewOf} from './canvas/connection-style.ts';
import {flowEdges, flowNodes} from './canvas/flow-model.ts';
import {GraphCanvas} from './canvas/graph-canvas.tsx';
import type {GraphCanvasProps} from './canvas/graph-canvas.tsx';
import {Outline} from './canvas/outline.tsx';
import type {NodeActions} from './canvas/node-actions.ts';
import {useNodeDeleteKeys} from './canvas/use-node-delete-keys.ts';
import {nodeSections} from './dialogs/sections.ts';
import type {OpenDialog} from './editor-dialogs.tsx';
import {embedInto, insideOnly} from './state/embed-into.ts';
import {removeNode} from './state/node-removal.ts';
import {connect, disconnect, moveNode} from './state/document.ts';
import {declarationFor} from './state/ports.ts';
import type {EditorModel} from './state/use-editor.ts';

interface Props {
  readonly editor: EditorModel;
  readonly catalog: Catalog;
  readonly open: (dialog: OpenDialog) => void;
}

/** A card's actions: its node dialog, its deletion, and removing its embedded component. */
function nodeActions({editor, catalog, open}: Props): NodeActions {
  return {
    edit: (nodeId) => {
      const node = editor.state.document.nodes.find((item) => item.id === nodeId);
      const section = node === undefined ? undefined : nodeSections(node, catalog)[0]?.key;
      if (section !== undefined) open({kind: 'node', nodeId, section});
    },
    remove: (nodeId) => {
      removeNode(editor, nodeId);
    },
    removeComponent: (nodeId) => {
      open({kind: 'remove-component', nodeId});
    },
  };
}

type Update = (value: GraphDocument) => GraphDocument;

/** The canvas edits: each is the editor's usual change, or adding a dropped component. */
function canvasEdits(editor: EditorModel, catalog: Catalog): Partial<GraphCanvasProps> {
  const {dispatch} = editor;
  const change = (update: Update): void => {
    dispatch({type: 'change', update});
  };
  return {
    onSelect: (nodeId) => {
      dispatch({type: 'select', nodeId});
    },
    onMove: (nodeId, position) => {
      change((value) => moveNode(value, nodeId, position));
    },
    onConnect: (from, to) => {
      change((value) => connect(value, from, to));
    },
    onDisconnect: (from, to) => {
      change((value) => disconnect(value, from, to));
    },
    onDropComponent: (component, position, nodeId) => {
      const declaration = declarationFor(catalog, component);
      if (declaration === undefined) return;
      if (insideOnly(declaration)) embedInto(editor, catalog, declaration, nodeId);
      else dispatch({type: 'add', declaration, position});
    },
  };
}

function EditableCanvas(
  props: Props & {readonly interaction: CanvasInteraction; readonly curvature: number | null},
): ReactElement {
  const {editor, catalog, curvature} = props;
  const {document, diagnostics, selected} = editor.state;
  const view = useMemo(() => {
    const saved = viewOf(document);
    return curvature === null ? saved : {...saved, curvature};
  }, [document, curvature]);
  useNodeDeleteKeys(editor);
  const flow = useMemo(() => {
    const input = {document, catalog, diagnostics, selected, editable: true};
    const nodes = flowNodes(input);
    return {nodes, edges: flowEdges(input, nodes)};
  }, [document, catalog, diagnostics, selected]);
  return (
    <GraphCanvas
      nodes={flow.nodes}
      edges={flow.edges}
      editable
      view={view}
      label="Graph canvas"
      interaction={props.interaction}
      nodeActions={nodeActions(props)}
      {...canvasEdits(editor, catalog)}
    />
  );
}

/** The working copy's outline: selecting or deleting a node acts on the editor. */
function EditorOutline({editor, catalog}: Props): ReactElement {
  const {document, diagnostics, selected} = editor.state;
  return (
    <Outline
      document={document}
      catalog={catalog}
      diagnostics={diagnostics}
      selected={selected}
      onSelect={(nodeId) => {
        editor.dispatch({type: 'select', nodeId});
      }}
      onDelete={(nodeId) => {
        removeNode(editor, nodeId);
      }}
    />
  );
}

/** The editable canvas with its floating toolbar, or the outline of the graph. */
export function CanvasArea(props: Props): ReactElement {
  const [outline, setOutline] = useState(false);
  const [curvature, setCurvature] = useState<number | null>(null);
  const interaction = useCanvasInteraction();
  return (
    <div className="canvas-area">
      <CanvasToolbar
        model={editorCanvas(props.editor)}
        catalog={props.catalog}
        outline={outline}
        onOutline={setOutline}
        manual={interaction.manual}
        onPreview={setCurvature}
      />
      {outline ? (
        <EditorOutline {...props} />
      ) : (
        <EditableCanvas {...props} interaction={interaction} curvature={curvature} />
      )}
    </div>
  );
}
