import {useEffect, useMemo, useState} from 'react';
import {DefinitionClient} from '../../api/index.ts';
import {initialDraft} from './draft.ts';
import {editActions} from './edit-actions.ts';
import {deriveAction} from './derive-action.ts';
import {writeActions} from './write-actions.ts';
import {useRequests} from './use-requests.ts';
import {useSource} from './use-source.ts';
import type {DefinitionEditorProps, EditorModel} from './types.ts';

export function useEditor({
  credential,
  reference,
  onSaved,
  onDirtyChange,
}: DefinitionEditorProps): EditorModel {
  const [state, update] = useState(initialDraft);
  const client = useMemo(() => new DefinitionClient(credential), [credential]);
  const requests = useRequests();
  const reload = useSource(client, reference, update);
  const dirty = state.source !== state.baseline || state.uncertain || state.pending === 'save';
  useEffect(() => {
    onDirtyChange(dirty);
  }, [dirty, onDirtyChange]);
  return {
    state,
    reload,
    dirty,
    ...editActions(state, update, requests),
    derive: deriveAction(state, {client, reference, requests, update}),
    ...writeActions(state, {client, requests, update, onSaved}),
  };
}
