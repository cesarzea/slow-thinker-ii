import type {ReactElement} from 'react';
import type {GraphSummary} from '../api/index.ts';
import {GraphView} from '../features/graph-view/index.ts';

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
        {graph.participants} agentes · {graph.nodes.length} activaciones · {graph.revision}
      </p>
      <GraphView key={graph.graph_id} graph={graph} />
      <ol aria-label="Orden de ejecución">
        {graph.nodes.map((node) => (
          <li key={node.id}>
            {node.id}: {node.component}
          </li>
        ))}
      </ol>
    </>
  );
}
