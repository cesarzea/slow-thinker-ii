import type {ReactElement} from 'react';
import type {GraphSummary} from '../../api/index.ts';
import {SessionControls} from './session-controls.tsx';
import {StartControls} from './start-controls.tsx';
import {PendingControls} from './pending-controls.tsx';
import {BudgetView, RunView} from './run-view.tsx';
import {ResultPanel} from './result-view.tsx';
import {HistoryView} from './history-view.tsx';
import {useExecution} from './use-execution.ts';

interface Props {
  readonly credential: string;
  readonly graph: GraphSummary;
  readonly onInspect: (id: string) => void;
}

export function ExecutionPanel({credential, graph, onInspect}: Props): ReactElement {
  const {state, store, commands, refresh} = useExecution(credential);
  return (
    <section className="execution" aria-label="Ejecución del experimento">
      <h2>Ejecutar experimento</h2>
      {state.message !== null && <p role="status">{state.message}</p>}
      <PendingControls state={state} commands={commands} refresh={refresh} />
      <SessionControls state={state} store={store} commands={commands} />
      <StartControls state={state} commands={commands} graph={graph} />
      {typeof state.workspace?.blocking_run_id === 'string' && (
        <button
          onClick={() => {
            store.selectRun(state.workspace?.blocking_run_id ?? '');
          }}
        >
          Ver ejecución que bloquea el inicio
        </button>
      )}
      {state.workspace !== null && <BudgetView budget={state.workspace.month_budget} label="Mes" />}
      <RunView run={state.run} />
      <InspectionButton run={state.runId} onInspect={onInspect} />
      <ResultPanel credential={credential} run={state.run} />
      <HistoryView state={state} store={store} />
    </section>
  );
}

function InspectionButton({
  run,
  onInspect,
}: Pick<Props, 'onInspect'> & {
  readonly run: string;
}): ReactElement | null {
  return run === '' ? null : (
    <button
      onClick={() => {
        onInspect(run);
      }}
    >
      Inspeccionar ejecución
    </button>
  );
}
