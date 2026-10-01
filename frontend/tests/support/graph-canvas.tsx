import type {ComponentType, ReactElement, ReactNode} from 'react';
import type {BaseEdgeProps, Edge, EdgeProps, Node, XYPosition} from '@xyflow/react';

type CanvasNode = Node<{label: string; selection: unknown}>;
type CanvasEdge = Edge<{selection: unknown}>;
type RendererProps = Omit<EdgeProps<CanvasEdge>, 'sourcePosition' | 'targetPosition'> & {
  sourcePosition: 'right';
  targetPosition: 'left';
};
interface Props {
  readonly nodes: CanvasNode[];
  readonly edges: CanvasEdge[];
  readonly children: ReactNode;
  readonly nodeTypes: Readonly<Record<string, ComponentType<{data: CanvasNode['data']}>>>;
  readonly edgeTypes: Readonly<Record<string, ComponentType<RendererProps>>>;
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
      <svg>
        {props.edges.map((edge) => (
          <CanvasEdgeItem key={edge.id} edge={edge} {...props} />
        ))}
      </svg>
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
function CanvasNodeItem({node, ...props}: Props & {readonly node: CanvasNode}): ReactElement {
  const Renderer = props.nodeTypes[node.type ?? 'default'];
  return (
    <div
      data-testid={node.id}
      data-position={position(node.position)}
      style={node.style}
      aria-hidden={node.focusable === false}
    >
      {Renderer !== undefined && <Renderer data={node.data} />}
      {node.selectable !== false && <NodeActions node={node} {...props} />}
    </div>
  );
}
function NodeActions({
  node,
  onNodeClick,
  onNodeDragStop,
}: Props & {readonly node: CanvasNode}): ReactElement {
  return (
    <>
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
    </>
  );
}
function CanvasEdgeItem({
  edge,
  edgeTypes,
}: Props & {readonly edge: CanvasEdge}): ReactElement | null {
  const Renderer = edgeTypes[edge.type ?? 'default'];
  if (Renderer === undefined) return null;
  return (
    <g data-testid={edge.id}>
      <Renderer
        {...edge}
        markerStart=""
        markerEnd=""
        sourceX={264}
        sourceY={100}
        targetX={400}
        targetY={100}
        sourcePosition="right"
        targetPosition="left"
      />
    </g>
  );
}

export function EdgeFrame(props: BaseEdgeProps): ReactElement {
  return (
    <g>
      <path d={props.path} />
      <text x={props.labelX} y={props.labelY}>
        {props.label}
      </text>
    </g>
  );
}
