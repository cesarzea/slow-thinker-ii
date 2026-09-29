import type {ReactElement} from 'react';
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
  return (
    <section aria-label="Controles de ejecución">
      <RunInput
        key={`${graph.graph_id}:${graph.revision}`}
        schema={graph.input_schema ?? legacyInputSchema}
      >
        {(input, valid) => <RunButtons {...props} input={input} valid={valid} />}
      </RunInput>
      {state.stale && <p role="status">Estado sin confirmar. Se está consultando al servidor.</p>}
      {state.stopRequested && (
        <p role="status">Parada solicitada; esperando confirmación del estado final.</p>
      )}
    </section>
  );
}

function RunButtons({
  state,
  commands,
  graph,
  input,
  valid,
  inputUnavailable,
}: Props & {readonly input: unknown; readonly valid: boolean}): ReactElement {
  return (
    <div className="actions">
      <button
        disabled={!canStart(state) || !valid || inputUnavailable === true}
        onClick={() => {
          void commands.start(graph, input);
        }}
      >
        Iniciar ejecución
      </button>
      <button
        disabled={!canStop(state)}
        onClick={() => {
          void commands.stop();
        }}
      >
        Detener ejecución
      </button>
    </div>
  );
}
