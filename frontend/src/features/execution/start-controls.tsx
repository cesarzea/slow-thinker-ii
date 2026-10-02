import type {ReactElement} from 'react';
import {useId} from 'react';
import type {GraphSummary} from '../../api/index.ts';
import {RunInput} from './run-input.tsx';
import {legacyInputSchema} from './input-schema.ts';
import type {ExecutionCommands} from './commands.ts';
import {canStart, canStop} from './state.ts';
import type {ExecutionState} from './state.ts';

interface Props {
  readonly state: ExecutionState;
  readonly commands: ExecutionCommands;
  readonly graph: GraphSummary;
  readonly inputUnavailable?: boolean;
}

export function StartControls(props: Props): ReactElement {
  const {state, graph} = props;
  const unavailableId = useId();
  return (
    <section aria-label="Run controls">
      <RunInput
        key={JSON.stringify([graph.graph_id, graph.revision])}
        schema={graph.input_schema ?? legacyInputSchema}
      >
        {(input, valid) => (
          <RunButtons {...props} input={input} valid={valid} unavailableId={unavailableId} />
        )}
      </RunInput>
      <RunMessages
        state={state}
        inputUnavailable={props.inputUnavailable === true}
        unavailableId={unavailableId}
      />
    </section>
  );
}

interface ButtonProps extends Props {
  readonly input: unknown;
  readonly valid: boolean;
  readonly unavailableId: string;
}

function RunButtons(props: ButtonProps): ReactElement {
  const {state, commands, graph, input, valid, inputUnavailable, unavailableId} = props;
  return (
    <div className="actions">
      <button
        disabled={!canStart(state) || !valid || inputUnavailable === true}
        aria-describedby={inputUnavailable === true ? unavailableId : undefined}
        onClick={() => {
          void commands.start(graph, input);
        }}
      >
        Start run
      </button>
      <button
        disabled={!canStop(state)}
        onClick={() => {
          void commands.stop();
        }}
      >
        Stop run
      </button>
    </div>
  );
}

function RunMessages({
  state,
  inputUnavailable,
  unavailableId,
}: {
  readonly state: ExecutionState;
  readonly inputUnavailable: boolean;
  readonly unavailableId: string;
}): ReactElement {
  return (
    <>
      {inputUnavailable && (
        <p id={unavailableId} role="status">
          Start is unavailable until the saved definition is loaded and any draft is saved or
          discarded.
        </p>
      )}
      {state.stale && <p role="status">State unconfirmed. Checking with the server.</p>}
      {state.stopRequested && (
        <p role="status">Stop requested; waiting for confirmation of the final state.</p>
      )}
    </>
  );
}
