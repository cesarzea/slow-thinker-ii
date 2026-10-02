import {useCallback, useState} from 'react';
import type {ReactElement} from 'react';
import type {GraphReference, GraphSummary} from '../api/index.ts';
import {DefinitionEditor} from '../features/definition-editor/index.tsx';
import {ExecutionPanel} from '../features/execution/index.ts';
import type {ExecutionObservation} from '../features/execution/index.ts';
import {DefinitionGraph} from './graph-workspace.tsx';
import {referenceKey} from './catalog-state.ts';
import {useGraphDetail} from './use-graph-detail.ts';

interface Props {
  readonly credential: string;
  readonly graph: GraphSummary;
  readonly onSaved: (reference: GraphReference) => void;
  readonly onObservation: (observation: ExecutionObservation) => void;
  readonly onInspect: (run: string) => void;
  readonly selectionBlocked: boolean;
}

export function ExperimentExecution(props: Props): ReactElement {
  const {credential, graph} = props;
  const {detail, error} = useGraphDetail(graph, credential);
  const key = referenceKey(graph);
  const {dirty, onDirtyChange} = useDraftStatus(key);
  const selected = detail === null ? graph : {...graph, input_schema: detail.input_schema};
  return (
    <>
      <DefinitionGraph key={key} {...{graph, detail, error}} />
      <DefinitionEditor
        {...{credential, reference: graph}}
        onSaved={props.onSaved}
        onDirtyChange={onDirtyChange}
      />
      <ExecutionPanel
        credential={credential}
        graph={selected}
        inputUnavailable={detail === null || props.selectionBlocked || dirty}
        onObservation={props.onObservation}
        onInspect={props.onInspect}
      />
    </>
  );
}

function useDraftStatus(key: string): {
  readonly dirty: boolean;
  readonly onDirtyChange: (dirty: boolean) => void;
} {
  const [draft, setDraft] = useState({key, dirty: false});
  const onDirtyChange = useCallback(
    (dirty: boolean): void => {
      setDraft({key, dirty});
    },
    [key],
  );
  return {dirty: draft.key === key && draft.dirty, onDirtyChange};
}
