import {useState} from 'react';
import type {ReactElement} from 'react';
import {applyNodeChanges, Background, Controls, ReactFlow} from '@xyflow/react';
import type {NodeChange} from '@xyflow/react';
import {AgentCard, EntryAnchor, TerminalAnchor} from './agent-card.tsx';
import {RouteEdge} from './route-edge.tsx';
import type {GraphViewProps, VisualGraph, VisualNode, VisualEdge} from './types.ts';

const edgeTypes = {route: RouteEdge};
const nodeTypes = {agent: AgentCard, entry: EntryAnchor, terminal: TerminalAnchor};
type Props = VisualGraph & Pick<GraphViewProps, 'onSelect'>;
export function GraphCanvas({nodes, edges, onSelect}: Props): ReactElement {
  const {positioned, onNodesChange, retainPosition} = useCanvasNodes(nodes);
  return (
    <div className="agent-canvas" aria-label="Agent collaboration canvas">
      <ReactFlow
        nodes={positioned}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        minZoom={0.2}
        maxZoom={1.6}
        fitViewOptions={{minZoom: 0.2, maxZoom: 1, padding: 0.25}}
        nodesConnectable={false}
        onNodesChange={onNodesChange}
        onNodeDragStop={retainPosition}
        {...selectionEvents(onSelect)}
      >
        <Background color="#dce5ed" gap={24} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
function useCanvasNodes(nodes: VisualNode[]): {
  positioned: VisualNode[];
  onNodesChange: (changes: NodeChange<VisualNode>[]) => void;
  retainPosition: (_: unknown, node: VisualNode) => void;
} {
  const [retained, setRetained] = useState<Readonly<Record<string, VisualNode>>>({});
  const onNodesChange = (changes: NodeChange<VisualNode>[]): void => {
    setRetained((previous) =>
      Object.fromEntries(
        applyNodeChanges(changes, currentNodes(nodes, previous)).map((node) => [node.id, node]),
      ),
    );
  };
  return {
    positioned: currentNodes(nodes, retained),
    onNodesChange,
    retainPosition: (_, node) => {
      onNodesChange([{id: node.id, type: 'position', position: node.position}]);
    },
  };
}
function currentNodes(
  nodes: VisualNode[],
  retained: Readonly<Record<string, VisualNode>>,
): VisualNode[] {
  return nodes.map((node) => ({
    ...retained[node.id],
    ...node,
    position: retained[node.id]?.position ?? node.position,
  }));
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
