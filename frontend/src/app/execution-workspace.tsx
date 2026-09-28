import {useState} from 'react';
import type {ReactElement} from 'react';
import type {GraphSummary} from '../api/index.ts';
import {ExecutionPanel} from '../features/execution/index.ts';
import {Inspector} from '../features/inspector/index.ts';

export function ExecutionWorkspace({
  credential,
  graph,
}: {
  readonly credential: string;
  readonly graph: GraphSummary;
}): ReactElement {
  const [run, onInspect] = useState<string>();
  return (
    <>
      <ExecutionPanel credential={credential} graph={graph} onInspect={onInspect} />
      {run !== undefined && (
        <>
          <button
            onClick={() => {
              onInspect(undefined);
            }}
          >
            Cerrar inspector
          </button>
          <Inspector key={run} credential={credential} run={run} />
        </>
      )}
    </>
  );
}
