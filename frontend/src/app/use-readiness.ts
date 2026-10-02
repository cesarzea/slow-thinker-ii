import {useEffect, useMemo} from 'react';
import type {GraphDetail} from '../api/index.ts';
import {definitionLocked} from '../features/definition-editor/index.tsx';
import type {EditorModel} from '../features/definition-editor/index.tsx';
import type {ExperimentExecutionProps} from './experiment-types.ts';
import {referenceKey} from './catalog-state.ts';
export function useReadiness(
  props: ExperimentExecutionProps & {
    readonly model: EditorModel;
    readonly detail: GraphDetail | null;
    readonly error: string | null;
  },
): void {
  const {graph, detail, model, error, onReadiness} = props;
  const selected = useMemo(
    () => (detail === null ? graph : {...graph, input_schema: detail.input_schema}),
    [graph, detail],
  );
  const reason = startReason(model);
  const blocked = detail === null || model.dirty || definitionLocked(model.state);
  useEffect(() => {
    onReadiness?.({key: referenceKey(graph), graph: selected, blocked, error, reason});
  }, [onReadiness, graph, selected, blocked, error, reason]);
}

function startReason(model: EditorModel): string | null {
  if (model.dirty)
    return 'This experiment has unsaved changes. Save or discard its draft before starting a run.';
  return definitionLocked(model.state)
    ? 'Definition configuration is pending or unconfirmed. Resolve it before starting a run.'
    : null;
}
