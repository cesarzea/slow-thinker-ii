import type {ReactElement} from 'react';
import type {Catalog, GraphDocument, GraphNode} from '../../../api/index.ts';
import {Button, IconButton, KindTile, MenuButton} from '../../../ui/index.ts';
import type {MenuItem} from '../../../ui/index.ts';
import {embeddedLabel} from '../dialogs/node-dialog-state.ts';
import {nodeSections} from '../dialogs/sections.ts';
import type {OpenDialog} from '../editor-dialogs.tsx';
import {connect, disconnect, renameNode} from '../state/document.ts';
import {removeNode} from '../state/node-removal.ts';
import {embeddable, freePositions} from '../state/embedding.ts';
import {declarationFor, isTriggerOrOutput} from '../state/ports.ts';
import type {EditorModel} from '../state/use-editor.ts';
import {Connections} from './connections.tsx';
import {NodeNameField} from './node-name-field.tsx';
import {NodeProblems} from './node-problems.tsx';
import {PortSides} from './port-sides-field.tsx';
import {ExpandAll, SectionRows, useExpansion} from './section-rows.tsx';

export interface NodeInspectorProps {
  readonly editor: EditorModel;
  readonly catalog: Catalog;
  readonly open: (dialog: OpenDialog) => void;
  readonly node: GraphNode;
}
type Change = (update: (document: GraphDocument) => GraphDocument) => void;

function changer(editor: EditorModel): Change {
  return (update) => {
    editor.dispatch({type: 'change', update});
  };
}

/** Remove each embedded component, and delete the node. */
function nodeActions({node, catalog, editor, open}: NodeInspectorProps): MenuItem[] {
  const removals = (node.embedded ?? []).map((item) => ({
    label: `Remove ${declarationFor(catalog, item.component)?.label ?? item.component}`,
    onSelect: () => {
      open({kind: 'remove-component', nodeId: node.id, position: item.position});
    },
  }));
  const deletion = (): void => {
    removeNode(editor, node.id);
  };
  return [...removals, {label: 'Delete node', danger: true, onSelect: deletion}];
}

function subtitle(node: GraphNode, catalog: Catalog): string {
  const declaration = declarationFor(catalog, node.component);
  const embedded = embeddedLabel(node, catalog);
  const host = `${declaration?.label ?? node.component} · ${declaration?.version ?? 'unknown'}`;
  return embedded === null ? host : `${host} · with ${embedded}`;
}

function Head(props: NodeInspectorProps): ReactElement {
  const {node, catalog, editor} = props;
  return (
    <header className="inspector-head">
      <KindTile icon={declarationFor(catalog, node.component)?.icon ?? 'component'} />
      <div className="inspector-titles">
        <h2 aria-label={node.name}>
          <NodeNameField
            key={`${node.id}:${node.name}`}
            name={node.name}
            onRename={(name) => {
              changer(editor)((value) => renameNode(value, node.id, name));
            }}
          />
        </h2>
        <p className="inspector-sub">{subtitle(node, catalog)}</p>
      </div>
      <IconButton
        icon="trash"
        label="Delete node"
        onClick={() => {
          removeNode(editor, node.id);
        }}
      />
      <MenuButton label={`More actions for ${node.name}`} items={nodeActions(props)} />
    </header>
  );
}

function AddComponent({node, catalog, open}: NodeInspectorProps): ReactElement | null {
  const free = freePositions(node);
  if (isTriggerOrOutput(node) || embeddable(catalog, free).length === 0) return null;
  return (
    <Button
      size="sm"
      variant="ghost"
      icon="plus"
      onClick={() => {
        open({kind: 'add-component', nodeId: node.id});
      }}
    >
      Add component
    </Button>
  );
}

function Configuration(props: NodeInspectorProps): ReactElement {
  const {node, catalog, open} = props;
  const sections = nodeSections(node, catalog);
  const expansion = useExpansion(sections.map((entry) => entry.key));
  return (
    <section className="inspector-section" aria-label="Configuration">
      <div className="inspector-section-head">
        <h3 className="panel-title">Configuration</h3>
        {sections.length > 0 && <ExpandAll expansion={expansion} />}
      </div>
      <SectionRows
        {...props}
        sections={sections}
        expansion={expansion}
        onEdit={(section) => {
          open({kind: 'node', nodeId: node.id, section});
        }}
      />
      <AddComponent {...props} />
    </section>
  );
}

/** The selected node: name, configuration rows, port sides, connections and problems. */
export function NodeInspector(props: NodeInspectorProps): ReactElement {
  const change = changer(props.editor);
  const {document, diagnostics} = props.editor.state;
  return (
    <aside className="side-panel" aria-label="Selected node">
      <Head {...props} />
      <Configuration {...props} />
      <PortSides document={document} node={props.node} catalog={props.catalog} onChange={change} />
      <Connections
        document={document}
        catalog={props.catalog}
        node={props.node}
        onConnect={(from, to) => {
          change((value) => connect(value, from, to));
        }}
        onDisconnect={(item) => {
          change((value) => disconnect(value, item.from, item.to));
        }}
      />
      <section className="inspector-section" aria-label="Problems">
        <NodeProblems diagnostics={diagnostics} nodeId={props.node.id} />
      </section>
    </aside>
  );
}
