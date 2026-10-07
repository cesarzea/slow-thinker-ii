import type {GraphDocument} from '../../../api/index.ts';
import type {UndoModel} from '../state/use-undo.ts';
import type {EditorModel} from '../state/use-editor.ts';

/**
 * What the canvas toolbar works on: a document, its changes, and Undo and Redo over them.
 * The editor saves each change; a run's view keeps them locally and saves nothing.
 */
export interface CanvasModel {
  readonly document: GraphDocument;
  readonly change: (update: (document: GraphDocument) => GraphDocument) => void;
  readonly history: Pick<UndoModel, 'canUndo' | 'canRedo' | 'undo' | 'redo'>;
}

/** The editor's document, each change saved as the branch's next change. */
export function editorCanvas(editor: EditorModel): CanvasModel {
  return {
    document: editor.state.document,
    change: (update) => {
      editor.dispatch({type: 'change', update});
    },
    history: editor.history,
  };
}
