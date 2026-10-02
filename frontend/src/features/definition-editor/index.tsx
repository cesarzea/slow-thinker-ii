import type {ReactElement} from 'react';
import type {DefinitionEditorProps} from './types.ts';
import {EditorWorkspace} from './editor-workspace.tsx';
import './style.css';

export type {DefinitionEditorProps} from './types.ts';
export type {EditorModel} from './types.ts';
export {DefinitionSession} from './definition-session.tsx';
export {EditorView as DefinitionEditorView} from './editor-workspace.tsx';
export {locked as definitionLocked} from './draft.ts';

export function DefinitionEditor(props: DefinitionEditorProps): ReactElement {
  const {credential, reference} = props;
  return (
    <EditorWorkspace
      key={JSON.stringify([credential, reference.graph_id, reference.revision])}
      {...props}
    />
  );
}
