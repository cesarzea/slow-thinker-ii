import type {GraphSummary, GraphDetail, ExecutionPage} from '../../api/index.ts';
import type {Node, Edge} from '@xyflow/react';

export type GraphSelection = Readonly<{
  kind: 'component' | 'node' | 'activation' | 'call';
  id: string;
}>;
export interface GraphViewProps {
  readonly graph: GraphSummary;
  readonly detail?: GraphDetail;
  readonly execution?: ExecutionPage;
  readonly onSelect?: ((selection: GraphSelection) => void) | undefined;
}
export interface GraphLayers {
  readonly control: boolean;
  readonly permission: boolean;
  readonly binding: boolean;
  readonly observed: boolean;
}
export type VisualNode = Node<{label: string; selection: GraphSelection | null}>;
export type VisualEdge = Edge<{selection: GraphSelection | null}>;
export interface VisualGraph {
  readonly nodes: VisualNode[];
  readonly edges: VisualEdge[];
}
