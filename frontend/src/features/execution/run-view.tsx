import type {ReactElement} from 'react';
import type {Budget, Run} from '../../api/index.ts';
import {moneyLabel} from '../../ui/index.ts';

const stateLabels = {
  created: 'Preparing',
  running: 'Running',
  stopping: 'Stopping',
  completed: 'Completed',
  failed: 'Failed',
  cancelled: 'Cancelled',
  timed_out: 'Timed out',
  interrupted: 'Interrupted',
};

export function RunView({run}: {readonly run: Run | null}): ReactElement | null {
  if (run === null) return null;
  return (
    <section aria-label="Run state">
      <h2>{stateLabels[run.state]}</h2>
      <p>
        {run.graph_id} · {run.graph_revision}
      </p>
      {run.reason !== null && <p>Reason: {run.reason}</p>}
      <p>{run.cleanup === 'confirmed' ? 'Process cleanup confirmed' : 'Process cleanup pending'}</p>
      <BudgetView budget={run.budget} label="This run" />
      <BudgetView budget={run.session_budget} label="Session" />
    </section>
  );
}

export function BudgetView({
  budget,
  label,
}: {
  readonly budget: Budget;
  readonly label: string;
}): ReactElement {
  return (
    <p>
      <strong>{label}:</strong> {moneyLabel(budget.settled)} recorded ·{' '}
      {moneyLabel(budget.outstanding)} pending · {moneyLabel(budget.cap)} limit
    </p>
  );
}
