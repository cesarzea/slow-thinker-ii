import type {History} from '../../api/index.ts';
import type {ReactElement} from 'react';
import {PageControls} from './page-controls.tsx';
import type {ExecutionState, ExecutionStore} from './state.ts';

export function HistoryView({
  state,
  store,
}: {
  readonly state: ExecutionState;
  readonly store: ExecutionStore;
}): ReactElement | null {
  if (state.history === null) return null;
  return (
    <section aria-label="Session history">
      <h2>History</h2>
      {state.history.items.length === 0 && <p>This session has no runs yet.</p>}
      <HistoryItems history={state.history} store={store} />
      <PageControls
        kind="history"
        current={state.historyCursor}
        next={state.history.next_cursor}
        store={store}
      />
    </section>
  );
}

function HistoryItems({
  history,
  store,
}: {
  readonly history: History;
  readonly store: ExecutionStore;
}): ReactElement {
  return (
    <ul>
      {history.items.map((run) => (
        <li key={run.run_id}>
          <button
            onClick={() => {
              store.selectRun(run.run_id);
            }}
          >
            {run.graph_id} · {run.state} · {run.run_id.slice(0, 8)}
          </button>
        </li>
      ))}
    </ul>
  );
}
