import type {ReactElement} from 'react';
import type {GraphSummary} from '../api/index.ts';
import {referenceKey} from './catalog-state.ts';

interface PanelProps {
  readonly graphs: readonly GraphSummary[];
  readonly graph: GraphSummary;
  readonly onSelect: (id: string) => void;
}

function ExperimentSelector({graphs, graph, onSelect}: PanelProps): ReactElement {
  const options = graphs.some((item) => referenceKey(item) === referenceKey(graph))
    ? graphs
    : [graph, ...graphs];
  return (
    <label>
      Experiment
      <select
        value={referenceKey(graph)}
        onChange={(event) => {
          onSelect(event.target.value);
        }}
      >
        {options.map((item) => (
          <option key={referenceKey(item)} value={referenceKey(item)}>
            {item.graph_id} · {item.revision}
          </option>
        ))}
      </select>
    </label>
  );
}

export function ExperimentPanel(props: PanelProps): ReactElement {
  const {graph} = props;
  const agents = graph.participants === 1 ? 'agent' : 'agents';
  const nodes = graph.nodes.length === 1 ? 'declared node' : 'declared nodes';
  return (
    <>
      <ExperimentSelector {...props} />
      <p>
        {graph.participants} {agents} · {graph.nodes.length} {nodes} · {graph.revision}
      </p>
      <ol aria-label="Experiment nodes">
        {graph.nodes.map((node) => (
          <li key={node.id}>
            {node.id}: {node.component}
          </li>
        ))}
      </ol>
    </>
  );
}
