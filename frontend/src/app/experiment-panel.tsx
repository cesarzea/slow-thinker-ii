import type {ReactElement} from 'react';
import type {GraphSummary} from '../api/index.ts';

interface PanelProps {
  readonly graphs: GraphSummary[];
  readonly graph: GraphSummary;
  readonly onSelect: (id: string) => void;
}

function ExperimentSelector({graphs, graph, onSelect}: PanelProps): ReactElement {
  return (
    <label>
      Experiment
      <select
        value={graph.graph_id}
        onChange={(event) => {
          onSelect(event.target.value);
        }}
      >
        {graphs.map((item) => (
          <option key={item.graph_id} value={item.graph_id}>
            {item.graph_id}
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
