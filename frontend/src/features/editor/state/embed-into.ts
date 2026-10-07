import type {Catalog, ComponentDeclaration} from '../../../api/index.ts';
import {embedComponent} from './embedding.ts';
import {isTriggerOrOutput} from './ports.ts';
import type {EditorModel} from './use-editor.ts';

/** Whether a component only goes inside a node, such as Memory. */
export const insideOnly = (declaration: ComponentDeclaration): boolean =>
  !declaration.placements.includes('node');

/**
 * Embeds a component that only goes inside a node into that node, or explains why not.
 * The node is the one it was dropped on, or the selected one.
 */
export function embedInto(
  editor: EditorModel,
  catalog: Catalog,
  declaration: ComponentDeclaration,
  nodeId: string | null,
): void {
  const node = editor.state.document.nodes.find((item) => item.id === nodeId);
  if (node === undefined) {
    editor.history.notify(`Drag ${declaration.label} onto a node, or select a node first.`);
    return;
  }
  if (isTriggerOrOutput(node)) {
    editor.history.notify(`${node.name} cannot contain ${declaration.label}.`);
    return;
  }
  editor.dispatch({
    type: 'change',
    update: (value) => embedComponent(value, node.id, declaration, catalog),
  });
  editor.history.notify(`${declaration.label} added to ${node.name}.`);
}
