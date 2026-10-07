import type {DragEvent} from 'react';
import {useReactFlow} from '@xyflow/react';
import {COMPONENT_DRAG_TYPE} from './drop.ts';
import type {CardNode, RouteEdgeType} from './types.ts';

type Drop = (component: string, position: [number, number], nodeId: string | null) => void;
interface DropHandlers {
  readonly onDragOver?: (event: DragEvent<HTMLDivElement>) => void;
  readonly onDrop?: (event: DragEvent<HTMLDivElement>) => void;
}

/** A card dropped from the palette is centred under the pointer, near the card's top. */
const GRAB = {x: 110, y: 24};

/** Accept components dragged from the palette and report where they were dropped. */
export function useComponentDrop(onDrop: Drop | undefined): DropHandlers {
  const flow = useReactFlow<CardNode, RouteEdgeType>();
  if (onDrop === undefined) return {};
  return {
    onDragOver: (event) => {
      if (!event.dataTransfer.types.includes(COMPONENT_DRAG_TYPE)) return;
      event.preventDefault();
      event.dataTransfer.dropEffect = 'copy';
    },
    onDrop: (event) => {
      const component = event.dataTransfer.getData(COMPONENT_DRAG_TYPE);
      if (component === '') return;
      event.preventDefault();
      const point = flow.screenToFlowPosition({x: event.clientX, y: event.clientY});
      const card = document
        .elementFromPoint(event.clientX, event.clientY)
        ?.closest('.react-flow__node')
        ?.getAttribute('data-id');
      const at: [number, number] = [Math.round(point.x - GRAB.x), Math.round(point.y - GRAB.y)];
      onDrop(component, at, card ?? null);
    },
  };
}
