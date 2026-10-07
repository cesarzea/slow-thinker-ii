import type {ReactElement} from 'react';
import type {Catalog} from '../../../api/index.ts';
import type {OpenDialog} from '../editor-dialogs.tsx';
import type {EditorModel} from '../state/use-editor.ts';
import {GraphInspector} from './graph-inspector.tsx';
import {NodeInspector} from './node-inspector.tsx';

/** The selected node, or the graph when no node is selected; it starts afresh per node. */
export function Inspector(props: {
  readonly editor: EditorModel;
  readonly catalog: Catalog;
  readonly open: (dialog: OpenDialog | null) => void;
}): ReactElement {
  const {document, selected} = props.editor.state;
  const node = document.nodes.find((item) => item.id === selected);
  if (node === undefined) return <GraphInspector editor={props.editor} />;
  return <NodeInspector key={node.id} {...props} node={node} />;
}
