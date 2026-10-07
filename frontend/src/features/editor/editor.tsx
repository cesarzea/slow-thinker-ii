import {useCallback, useState} from 'react';
import type {ReactElement} from 'react';
import {ReactFlowProvider} from '@xyflow/react';

import {useRead} from '../../ui/index.ts';
import {EditorWorkspace} from './editor-workspace.tsx';
import type {EditorProps} from './editor-props.ts';
import {loadEditor, MAIN_BRANCH} from './state/load.ts';
import './editor.css';

function LoadFailure(props: {readonly error: string; readonly onRetry: () => void}): ReactElement {
  return (
    <div role="alert" className="load-failure">
      <p>Could not open the graph. {props.error}</p>
      <button type="button" onClick={props.onRetry}>
        Try again
      </button>
    </div>
  );
}

/** The graph editor: the working copy of a branch, saved as it changes. */
export function Editor(props: EditorProps): ReactElement {
  const {client, graphId, created} = props;
  const [branch, setBranch] = useState(MAIN_BRANCH);
  const [historyOpen, setHistoryOpen] = useState(false);
  const read = useCallback(
    async (signal: AbortSignal) => loadEditor(client, graphId, branch, created, signal),
    [client, graphId, branch, created],
  );
  const {data, error, refresh} = useRead(read);
  if (error !== null) return <LoadFailure error={error} onRetry={refresh} />;
  if (data === null) return <p className="muted page-loading">Loading the graph…</p>;
  return (
    <ReactFlowProvider>
      <EditorWorkspace
        key={`${data.target.graphId}:${data.target.branch}`}
        {...props}
        source={data}
        onBranchChange={setBranch}
        historyOpen={historyOpen}
        onHistory={setHistoryOpen}
      />
    </ReactFlowProvider>
  );
}
