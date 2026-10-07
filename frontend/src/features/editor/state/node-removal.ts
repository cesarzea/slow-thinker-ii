import {deleteNode} from './document.ts';
import type {EditorModel} from './use-editor.ts';

/** Delete a node with its connections as one change, and offer to undo it. */
export function removeNode(editor: EditorModel, nodeId: string): void {
  const node = editor.state.document.nodes.find((item) => item.id === nodeId);
  if (node === undefined) return;
  editor.dispatch({type: 'change', update: (value) => deleteNode(value, nodeId)});
  editor.history.notify(`Deleted ${node.name}`, true);
}
