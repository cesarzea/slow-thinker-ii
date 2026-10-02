import type {ReactElement, ReactNode} from 'react';
import {useEditor} from './use-editor.ts';
import type {DefinitionEditorProps, EditorModel} from './types.ts';

export interface DefinitionSessionProps extends DefinitionEditorProps {
  readonly children: (model: EditorModel) => ReactNode;
}

export function DefinitionSession(props: DefinitionSessionProps): ReactElement {
  return (
    <Session
      key={JSON.stringify([props.credential, props.reference.graph_id, props.reference.revision])}
      {...props}
    />
  );
}

function Session(props: DefinitionSessionProps): ReactElement {
  const model = useEditor(props);
  return <>{props.children(model)}</>;
}
