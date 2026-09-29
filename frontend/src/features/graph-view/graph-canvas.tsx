import {useState} from 'react';
import type {ReactElement} from 'react';
import {Background, Controls, ReactFlow} from '@xyflow/react';
import type {XYPosition} from '@xyflow/react';
import {ReturnEdge} from './return-edge.tsx';
import type {GraphViewProps, VisualGraph, VisualNode, VisualEdge} from './types.ts';

const edgeTypes = {'control-return': ReturnEdge};

type Props = VisualGraph & Pick<GraphViewProps, 'onSelect'>;
export function GraphCanvas({nodes, edges, onSelect}: Props): ReactElement {
  const [positions, setPositions] = useState<Readonly<Record<string, XYPosition>>>({});
  const positioned = nodes.map((node) => ({
    ...node,
    position: positions[node.id] ?? node.position,
  }));
  return (
    <div className="graph" aria-label="Lienzo de relaciones">
      <ReactFlow
        nodes={positioned}
        edges={edges}
        edgeTypes={edgeTypes}
        fitView
        minZoom={0.1}
        fitViewOptions={{minZoom: 0.1}}
        nodesConnectable={false}
        {...selectionEvents(onSelect)}
        onNodeDragStop={(_, node) => {
          setPositions({...positions, [node.id]: node.position});
        }}
      >
        <Background />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
function selectionEvents(onSelect: GraphViewProps['onSelect']): {
  onNodeClick: (_: unknown, node: VisualNode) => void;
  onEdgeClick: (_: unknown, edge: VisualEdge) => void;
} {
  return {
    onNodeClick: (_, node) => {
      if (node.data.selection !== null) onSelect?.(node.data.selection);
    },
    onEdgeClick: (_, edge) => {
      const selection = edge.data?.selection;
      if (selection !== undefined && selection !== null) onSelect?.(selection);
    },
  };
}
