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
export interface ConfigurationValue {
  readonly value: string;
  readonly source: 'Saved configuration' | 'Graph configuration';
}
export interface AgentConfiguration {
  readonly model: ConfigurationValue;
  readonly effort: ConfigurationValue;
}
export interface AgentPresentation {
  readonly name: string;
  readonly componentType: string;
  readonly knownAgent: boolean;
  readonly configuration: AgentConfiguration | undefined;
  readonly activity: {readonly state: string; readonly count: number} | undefined;
}
export type VisualNode = Node<{
  label: string;
  selection: GraphSelection | null;
  agent?: AgentPresentation;
}>;
export type VisualEdge = Edge<{
  selection: GraphSelection | null;
  returning: boolean;
  terminal: boolean;
  entry?: boolean;
  system: boolean;
}>;
export interface VisualGraph {
  readonly nodes: VisualNode[];
  readonly edges: VisualEdge[];
}
