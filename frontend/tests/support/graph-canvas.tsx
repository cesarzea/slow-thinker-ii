import type {ReactElement, ReactNode} from 'react';
import type {Edge, Node, XYPosition} from '@xyflow/react';

type CanvasNode = Node<{label: string; selection: unknown}>;
type CanvasEdge = Edge<{selection: unknown}>;
interface Props {
  readonly nodes: CanvasNode[];
  readonly edges: CanvasEdge[];
  readonly children: ReactNode;
  readonly onNodeClick: (event: unknown, node: CanvasNode) => void;
  readonly onEdgeClick: (event: unknown, edge: CanvasEdge) => void;
  readonly onNodeDragStop: (event: unknown, node: CanvasNode) => void;
}
export function Canvas(props: Props): ReactElement {
  return (
    <div aria-label="Test canvas">
      {props.nodes.map((node) => (
        <CanvasNodeItem key={node.id} node={node} {...props} />
      ))}
      {props.edges.map((edge) => (
        <button
          key={edge.id}
          data-source={edge.source}
          data-target={edge.target}
          onClick={() => {
            props.onEdgeClick(null, edge);
          }}
        >
          {edge.label}
        </button>
      ))}
      {props.children}
    </div>
  );
}
function position(value: XYPosition): string {
  return `${String(value.x)},${String(value.y)}`;
}
export function Empty(): null {
  return null;
}

function CanvasNodeItem({
  node,
  onNodeClick,
  onNodeDragStop,
}: Props & {readonly node: CanvasNode}): ReactElement {
  return (
    <div data-testid={node.id} data-position={position(node.position)} style={node.style}>
      <button
        onClick={() => {
          onNodeClick(null, node);
        }}
      >
        {node.data.label}
      </button>
      <button
        onClick={() => {
          onNodeDragStop(null, {...node, position: {x: 800, y: 900}});
        }}
      >
        Move {node.id}
      </button>
    </div>
  );
}
