import type {Connection, Edge, ReactFlowProps} from '@xyflow/react';
import {FIT_VIEW} from './canvas-interaction.tsx';
import type {CanvasInteraction} from './canvas-interaction.tsx';
import type {EdgeSelection} from './edge-selection.ts';
import type {CardNode, RouteEdgeType} from './types.ts';

type FlowProps = Partial<ReactFlowProps<CardNode, RouteEdgeType>>;

/** The canvas's edits; only an editable canvas makes them. */
export interface CanvasEdits {
  readonly edges: RouteEdgeType[];
  readonly editable: boolean;
  /** Cards can be dragged although nothing else is editable. */
  readonly movable?: boolean;
  readonly onSelect?: (nodeId: string | null) => void;
  readonly onConnect?: (from: string, to: string) => void;
}

/** Selecting a node or the empty canvas clears the selected connection. */
function selecting(props: CanvasEdits, edges: EdgeSelection): FlowProps {
  return {
    onNodeClick: (_, node) => {
      edges.select(null);
      props.onSelect?.(node.id);
    },
    onPaneClick: () => {
      edges.select(null);
      props.onSelect?.(null);
    },
    onEdgeClick: (_, edge) => {
      props.onSelect?.(null);
      edges.select(edge.id);
    },
  };
}

function connecting(props: CanvasEdits): FlowProps {
  const exists = (connection: Edge | Connection): boolean =>
    props.edges.some(
      (edge) =>
        edge.source === connection.source &&
        edge.target === connection.target &&
        edge.sourceHandle === connection.sourceHandle &&
        edge.targetHandle === connection.targetHandle,
    );
  return {
    onConnect: (connection) => {
      const {source, sourceHandle, target, targetHandle} = connection;
      if (sourceHandle === null || targetHandle === null) return;
      props.onConnect?.(`${source}.${sourceHandle}`, `${target}.${targetHandle}`);
    },
    isValidConnection: (connection) =>
      typeof connection.sourceHandle === 'string' &&
      typeof connection.targetHandle === 'string' &&
      !exists(connection),
  };
}

const VIEW = {minZoom: 0.2, maxZoom: 1.6, fitView: true, fitViewOptions: FIT_VIEW} as const;

function mode(editable: boolean, movable: boolean): FlowProps {
  return {
    nodesDraggable: editable || movable,
    nodesConnectable: editable,
    nodesFocusable: editable,
    elementsSelectable: editable,
    edgesFocusable: false,
    deleteKeyCode: null,
  };
}

/** React Flow's behaviour: editing, the connection selection and palette drops when editable. */
export function behaviour(
  props: CanvasEdits,
  selection: EdgeSelection,
  interaction: CanvasInteraction,
  drop: FlowProps,
): FlowProps {
  const editing = props.editable ? {...selecting(props, selection), ...connecting(props)} : {};
  return {
    ...VIEW,
    ...mode(props.editable, props.movable === true),
    ...editing,
    ...interaction.events,
    ...drop,
  };
}
