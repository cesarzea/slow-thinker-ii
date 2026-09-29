import {MarkerType, Position} from '@xyflow/react';
import type {GraphSelection, VisualNode, VisualEdge} from './types.ts';

export function visualNode(
  id: string,
  label: string,
  x: number,
  y: number,
  selection: GraphSelection | null,
): VisualNode {
  return {
    id,
    position: {x, y},
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
    data: {label, selection},
    ariaLabel: label,
  };
}
export function visualEdge(
  id: string,
  source: string,
  target: string,
  label: string,
  color: string,
  selection: GraphSelection | null = null,
): VisualEdge {
  return {
    id,
    source,
    target,
    label,
    type: 'smoothstep',
    markerEnd: {type: MarkerType.ArrowClosed, color},
    style: {stroke: color, strokeWidth: 2},
    data: {selection},
    ariaLabel: label,
    focusable: selection !== null,
  };
}
