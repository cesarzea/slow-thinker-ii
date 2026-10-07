import {MarkerType} from '@xyflow/react';
import type {EdgeMarker} from '@xyflow/react';

/** React Flow's neutral connection grey, a shade darker for the arrowhead, and `--accent`. */
const ARROW_COLOUR = '#8b939e';
const ACTIVE_COLOUR = '#1d5c79';

/**
 * A closed arrowhead at the target end, in the accent colour while hovered or selected; sized
 * in canvas units, so it keeps its size when the line thickens.
 */
export function arrowhead(active: boolean): EdgeMarker {
  return {
    type: MarkerType.ArrowClosed,
    width: 22,
    height: 22,
    markerUnits: 'userSpaceOnUse',
    color: active ? ACTIVE_COLOUR : ARROW_COLOUR,
  };
}
