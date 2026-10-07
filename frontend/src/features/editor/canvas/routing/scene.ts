import {Position} from '@xyflow/react';
import type {InternalNode} from '@xyflow/react';
import type {PortSide} from '../../state/port-sides.ts';
import type {Box, Point} from './geometry.ts';

/** Where a connection meets a handle: its outer edge, on the side of its card. */
export interface HandleEnd extends Point {
  readonly side: PortSide;
  readonly box: Box;
}
export interface SceneCard {
  readonly id: string;
  readonly box: Box;
}
/** The cards and handles as React Flow measured them, in canvas coordinates. */
export interface Scene {
  readonly cards: readonly SceneCard[];
  readonly handles: ReadonlyMap<string, HandleEnd>;
}
export type HandleType = 'source' | 'target';

const SIDES: Readonly<Record<Position, PortSide>> = {
  [Position.Left]: 'left',
  [Position.Right]: 'right',
  [Position.Top]: 'top',
  [Position.Bottom]: 'bottom',
};

export const handleKey = (nodeId: string, type: HandleType, handle: string): string =>
  `${nodeId}/${type}/${handle}`;

function edgePoint(box: Box, side: PortSide): Point {
  const points: Readonly<Record<PortSide, Point>> = {
    left: {x: box.x, y: box.y + box.height / 2},
    right: {x: box.x + box.width, y: box.y + box.height / 2},
    top: {x: box.x + box.width / 2, y: box.y},
    bottom: {x: box.x + box.width / 2, y: box.y + box.height},
  };
  return points[side];
}

function addHandles(node: InternalNode, handles: Map<string, HandleEnd>): void {
  const origin = node.internals.positionAbsolute;
  for (const type of ['source', 'target'] as const)
    for (const handle of node.internals.handleBounds?.[type] ?? []) {
      if (typeof handle.id !== 'string') continue;
      const box = {
        x: origin.x + handle.x,
        y: origin.y + handle.y,
        width: handle.width,
        height: handle.height,
      };
      const side = SIDES[handle.position];
      handles.set(handleKey(node.id, type, handle.id), {...edgePoint(box, side), side, box});
    }
}

/** The measured cards and their handles. */
export function sceneOf(nodes: Iterable<InternalNode>): Scene {
  const cards: SceneCard[] = [];
  const handles = new Map<string, HandleEnd>();
  for (const node of nodes) {
    const {width, height} = node.measured;
    if (width === undefined || height === undefined) continue;
    const {x, y} = node.internals.positionAbsolute;
    cards.push({id: node.id, box: {x, y, width, height}});
    addHandles(node, handles);
  }
  return {cards, handles};
}

const boxText = (box: Box): string =>
  [box.x, box.y, box.width, box.height].map((value) => value.toFixed(1)).join(',');

/** Whether two scenes have the same cards and handles in the same places. */
export function sameScene(a: Scene, b: Scene): boolean {
  const text = (scene: Scene): string =>
    [
      ...scene.cards.map((card) => `${card.id}:${boxText(card.box)}`),
      ...[...scene.handles].map(([key, end]) => `${key}:${end.side}:${boxText(end.box)}`),
    ].join(';');
  return a === b || text(a) === text(b);
}
