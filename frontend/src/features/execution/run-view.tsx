import type {ReactElement} from 'react';
import type {Budget, Run} from '../../api/index.ts';
import {moneyLabel} from '../../ui/index.ts';

const stateLabels = {
  created: 'Preparando',
  running: 'En curso',
  stopping: 'Deteniéndose',
  completed: 'Completada',
  failed: 'Fallida',
  cancelled: 'Cancelada',
  timed_out: 'Tiempo agotado',
  interrupted: 'Interrumpida',
};

export function RunView({run}: {readonly run: Run | null}): ReactElement | null {
  if (run === null) return null;
  return (
    <section aria-label="Estado de ejecución">
      <h2>{stateLabels[run.state]}</h2>
      <p>
        {run.graph_id} · {run.graph_revision}
      </p>
      {run.reason !== null && <p>Motivo: {run.reason}</p>}
      <p>
        {run.cleanup === 'confirmed'
          ? 'Limpieza de procesos confirmada'
          : 'Limpieza de procesos pendiente'}
      </p>
      <BudgetView budget={run.budget} label="Esta ejecución" />
      <BudgetView budget={run.session_budget} label="Sesión" />
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
      <strong>{label}:</strong> {moneyLabel(budget.settled)} registrado ·{' '}
      {moneyLabel(budget.outstanding)} pendiente · {moneyLabel(budget.cap)} de límite
    </p>
  );
}
