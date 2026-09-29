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
      Experimento
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
  return (
    <>
      <ExperimentSelector {...props} />
      <p>
        {graph.participants} agentes · {graph.nodes.length} nodos declarados · {graph.revision}
      </p>
      <ol aria-label="Nodos del experimento">
        {graph.nodes.map((node) => (
          <li key={node.id}>
            {node.id}: {node.component}
          </li>
        ))}
      </ol>
    </>
  );
}
