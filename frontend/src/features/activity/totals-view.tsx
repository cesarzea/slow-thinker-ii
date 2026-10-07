import type {ReactElement} from 'react';
import {moneyLabel} from '../../ui/index.ts';
import type {ActivityTotals, NodeTotals} from './totals.ts';

function NodeTable({nodes}: {readonly nodes: readonly NodeTotals[]}): ReactElement {
  return (
    <table className="node-totals">
      <caption>Activations by node</caption>
      <thead>
        <tr>
          <th scope="col">Node</th>
          <th scope="col">Activations</th>
          <th scope="col">Cost</th>
        </tr>
      </thead>
      <tbody>
        {nodes.map((node) => (
          <tr key={node.nodeId}>
            <th scope="row">{node.name}</th>
            <td>{node.activations}</td>
            <td>{node.cost === null ? '—' : moneyLabel(node.cost)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/** Run status and totals, with activations and cost per node. */
export function TotalsView({totals}: {readonly totals: ActivityTotals}): ReactElement {
  return (
    <section className="totals" aria-label="Totals">
      <h2>Totals</h2>
      <p className="run-status-line" role="status">
        {totals.status}
      </p>
      <dl className="figures">
        {totals.figures.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      <NodeTable nodes={totals.nodes} />
    </section>
  );
}
