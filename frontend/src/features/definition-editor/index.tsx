import type {ReactElement} from 'react';
import type {DefinitionEditorProps} from './types.ts';
import {EditorWorkspace} from './editor-workspace.tsx';
import './style.css';

export type {DefinitionEditorProps} from './types.ts';

export function DefinitionEditor(props: DefinitionEditorProps): ReactElement {
  const {credential, reference} = props;
  return (
    <EditorWorkspace
      key={JSON.stringify([credential, reference.graph_id, reference.revision])}
      {...props}
    />
  );
}
