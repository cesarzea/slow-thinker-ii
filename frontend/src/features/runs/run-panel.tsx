import {useEffect} from 'react';
import type {ReactElement} from 'react';
import {Button, IconButton, runSourceText} from '../../ui/index.ts';
import {Ready, Stop} from './run-panel-parts.tsx';
import type {RunPanelProps} from './run-panel-props.ts';
import {RunFigures} from './run-parts.tsx';
import {isTerminal} from './run-tracker.ts';
import {useRun} from './use-run.ts';
import './runs.css';

function Running(props: RunPanelProps & {readonly runId: string}): ReactElement {
  const {run, error, refresh} = useRun(props.client, props.runId);
  const {onCounts} = props;
  useEffect(() => {
    if (run !== null)
      onCounts({activations: run.activations_by_node, messages: run.messages_by_connection});
  }, [run, onCounts]);
  if (run === null)
    return (
      <div className="run-panel-body">
        <p className="muted">
          {error === null ? 'Starting the run…' : `Could not load the run. ${error}`}
        </p>
      </div>
    );
  return (
    <div className="run-panel-body">
      <RunFigures run={run} limits={props.limits} />
      <div className="run-panel-actions">
        <Stop client={props.client} run={run} refresh={refresh} />
        {isTerminal(run.status) && <Button onClick={props.onReset}>Run again</Button>}
      </div>
      {props.feed(props.runId)}
      <p className="run-panel-links muted">Executed {runSourceText(run)}</p>
    </div>
  );
}

/** Run mode's panel: the message and Execute, then the run's figures, Stop and observed events. */
export function RunPanel(props: RunPanelProps): ReactElement {
  return (
    <aside className="side-panel run-panel" aria-label="Run">
      <div className="inspector-head">
        <div className="inspector-titles">
          <h2>Run</h2>
          <span className="inspector-sub">{props.graphName}</span>
        </div>
        <IconButton icon="close" label="Back to editing" size="sm" onClick={props.onClose} />
      </div>
      {props.runId === null ? (
        <Ready key="ready" {...props} />
      ) : (
        <Running key={props.runId} {...props} runId={props.runId} />
      )}
      <div className="run-panel-foot">
        <Button icon="edit" onClick={props.onClose}>
          Back to editing
        </Button>
      </div>
    </aside>
  );
}
