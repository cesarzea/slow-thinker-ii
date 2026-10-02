import type {ReactElement} from 'react';
import {locked, sourceSize} from './draft.ts';
import {useEditor} from './use-editor.ts';
import {EditorActions} from './editor-actions.tsx';
import {EditorFeedback} from './editor-feedback.tsx';
import {RevisionDraft} from './revision-draft.tsx';
import type {DefinitionEditorProps, EditorModel} from './types.ts';

export function EditorWorkspace(props: DefinitionEditorProps): ReactElement {
  const model = useEditor(props);
  const {reference} = props;
  return (
    <section className="definition-editor" aria-label="Experiment definition editor">
      <h2>Experiment definition</h2>
      <p>
        Selected saved definition: {reference.graph_id} · {reference.revision}
      </p>
      <p role="status">
        {model.dirty
          ? 'Unsaved draft — save or discard before starting a run.'
          : 'No unsaved changes.'}
      </p>
      <DraftText model={model} />
      <EditorActions model={model} />
      <EditorFeedback state={model.state} />
      <RevisionDraft reference={reference} model={model} />
    </section>
  );
}

function DraftText({model}: {readonly model: EditorModel}): ReactElement {
  return (
    <label>
      Definition JSON · limit 1 MiB (1,048,576 UTF-8 bytes)
      <textarea
        rows={16}
        spellCheck={false}
        readOnly={locked(model.state)}
        value={model.state.source}
        onChange={(event) => {
          model.edit(event.target.value);
        }}
      />
      <span>
        {sourceSize(model.state.source).toLocaleString('en')} UTF-8 bytes. Backend limits may be
        smaller.
      </span>
    </label>
  );
}
