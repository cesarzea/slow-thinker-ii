import {Background, Controls, MarkerType, Position, ReactFlow} from '@xyflow/react';
import type {GraphSummary} from '../../api/index.ts';
import type {ReactElement} from 'react';

export function GraphView({graph}: Readonly<{graph: GraphSummary}>): ReactElement {
  const nodes = graph.nodes.map((node, index) => ({
    id: node.id,
    position: {x: index * 240, y: 40},
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
    data: {label: `${node.id} · ${node.component}`},
  }));
  const edges = graph.nodes.flatMap((node, index) => {
    const previous = graph.nodes[index - 1];
    return previous === undefined
      ? []
      : [
          {
            id: `step-${String(index)}`,
            source: previous.id,
            target: node.id,
            markerEnd: {type: MarkerType.ArrowClosed},
          },
        ];
  });
  return (
    <section className="graph" aria-label="Secuencia de activaciones">
      <ReactFlow nodes={nodes} edges={edges} fitView nodesConnectable={false}>
        <Background />
        <Controls showInteractive={false} />
      </ReactFlow>
    </section>
  );
}
