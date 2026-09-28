import {useState} from 'react';
import type {ReactElement} from 'react';
import type {GraphSummary} from '../../api/index.ts';
import type {ExecutionCommands} from './commands.ts';
import {canStart, canStop} from './state.ts';
import type {ExecutionState} from './state.ts';

interface Props {
  readonly state: ExecutionState;
  readonly commands: ExecutionCommands;
  readonly graph: GraphSummary;
}

export function StartControls({state, commands, graph}: Props): ReactElement {
  const [problem, setProblem] = useState('');
  return (
    <section aria-label="Controles de ejecución">
      <label>
        Problema o tarea
        <textarea
          value={problem}
          onChange={(event) => {
            setProblem(event.target.value);
          }}
          rows={4}
        />
      </label>
      <RunButtons state={state} commands={commands} graph={graph} problem={problem} />
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
  problem,
}: Props & {readonly problem: string}): ReactElement {
  return (
    <div className="actions">
      <button
        disabled={!canStart(state) || problem.trim() === ''}
        onClick={() => {
          void commands.start(graph, problem);
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
