import {useState} from 'react';
import type {ReactFlowProps} from '@xyflow/react';
import {arrowhead} from './edge-look.ts';
import type {CardNode, RouteEdgeType} from './types.ts';

type FlowProps = Partial<ReactFlowProps<CardNode, RouteEdgeType>>;

/** The selected connection, and the hovered one, drawn in the accent colour. */
export function markActive(
  edges: RouteEdgeType[],
  selected: string | null,
  hovered: string | null,
): RouteEdgeType[] {
  return edges.map((edge) => {
    if (edge.id !== selected && edge.id !== hovered) return edge;
    const data = edge.data === undefined ? {} : {data: {...edge.data, active: true}};
    return {...edge, ...data, selected: edge.id === selected, markerEnd: arrowhead(true)};
  });
}

/** The connection under the pointer, on any canvas. */
export function useHovered(): {hovered: string | null; events: FlowProps} {
  const [hovered, setHovered] = useState<string | null>(null);
  return {
    hovered,
    events: {
      onEdgeMouseEnter: (_, edge) => {
        setHovered(edge.id);
      },
      onEdgeMouseLeave: () => {
        setHovered(null);
      },
    },
  };
}
