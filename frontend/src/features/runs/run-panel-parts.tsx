import {useState} from 'react';
import type {ReactElement} from 'react';
import {errorMessage} from '../../api/index.ts';
import type {Limits, OperatorClient, RunDetail} from '../../api/index.ts';
import {ActionButton, ExpandableTextArea, moneyLabel} from '../../ui/index.ts';
import type {RunPanelProps} from './run-panel-props.ts';
import {isTerminal} from './run-tracker.ts';

/** Executes what is on screen with the message; a failure to start is kept to show. */
function useExecute(props: RunPanelProps, message: string) {
  const [problem, setProblem] = useState<string | null>(null);
  const execute = async (): Promise<void> => {
    setProblem(null);
    try {
      const source = await props.prepare();
      if (source === null) throw new Error('The graph could not be saved.');
      props.onStarted(await props.client.startRun(props.graphId, source, message));
    } catch (error) {
      setProblem(`The run did not start. ${errorMessage(error)}`);
    }
  };
  return {problem, execute};
}

function LimitsNote({limits}: {readonly limits: Limits}): ReactElement {
  return (
    <p className="field-note">
      Up to {limits.max_activations} activations, {limits.time_limit_seconds} s and{' '}
      {moneyLabel(limits.budget_usd)}. Check the points to observe on the left.
    </p>
  );
}

/** Before Execute: the message, when the Trigger asks for it, the limits and Execute. */
export function Ready(props: RunPanelProps): ReactElement {
  const [message, setMessage] = useState(props.message);
  const {problem, execute} = useExecute(props, message);
  return (
    <div className="run-panel-body">
      {props.ask ? (
        <ExpandableTextArea label="Message" value={message} onChange={setMessage} />
      ) : (
        <p className="field-note">Sends the Trigger's message: “{props.message}”</p>
      )}
      <LimitsNote limits={props.limits} />
      {props.blocked !== null && <p className="field-note">{props.blocked}</p>}
      {problem !== null && <p role="alert">{problem}</p>}
      <ActionButton primary disabled={props.blocked !== null} action={execute}>
        Execute
      </ActionButton>
    </div>
  );
}

/** Stop while the run has not ended; a stop that fails says why. */
export function Stop(props: {
  readonly client: OperatorClient;
  readonly run: RunDetail;
  readonly refresh: () => void;
}): ReactElement | null {
  const [problem, setProblem] = useState<string | null>(null);
  if (isTerminal(props.run.status)) return null;
  const stop = async (): Promise<void> => {
    try {
      await props.client.stopRun(props.run.run_id);
      props.refresh();
    } catch (error) {
      setProblem(`The run could not be stopped. ${errorMessage(error)}`);
    }
  };
  return (
    <>
      <ActionButton action={stop}>Stop</ActionButton>
      {problem !== null && <p role="alert">{problem}</p>}
    </>
  );
}
