import type {ReactElement} from 'react';
import type {Usage} from '../../api/index.ts';
import {moneyLabel, Panel} from '../../ui/index.ts';
import type {ReadResult} from '../../ui/index.ts';

function BudgetTable({usage}: {readonly usage: Usage}): ReactElement {
  const budgets = [
    ['Daily', usage.day],
    ['Monthly', usage.month],
  ] as const;
  return (
    <div className="table-frame catalog-budgets">
      <table className="data-table" aria-label="Budgets">
        <thead>
          <tr>
            <th scope="col">Budget</th>
            <th scope="col">Period</th>
            <th scope="col">Limit</th>
            <th scope="col">Used</th>
          </tr>
        </thead>
        <tbody>
          {budgets.map(([name, budget]) => (
            <tr key={name}>
              <th scope="row">{name}</th>
              <td>{budget.key}</td>
              <td className="number">{moneyLabel(budget.limit_usd)}</td>
              <td className="number">{moneyLabel(budget.used_usd)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** The daily and monthly spending limits and the amounts used, exactly. */
export function Budgets({usage}: {readonly usage: ReadResult<Usage>}): ReactElement {
  return (
    <Panel title="Budgets" className="catalog-section">
      {usage.error !== null && <p role="alert">Could not load the budgets. {usage.error}</p>}
      {usage.data === null ? (
        usage.error === null && <p className="muted">Loading the budgets…</p>
      ) : (
        <BudgetTable usage={usage.data} />
      )}
    </Panel>
  );
}
