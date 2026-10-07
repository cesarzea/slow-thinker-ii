import type {ReactElement} from 'react';
import {EdgeLabelRenderer} from '@xyflow/react';
import type {EdgeProps} from '@xyflow/react';
import {useEdgeRemoval} from './edge-selection.ts';
import type {EdgeRoute} from './routing/edge-routes.ts';
import type {Box} from './routing/geometry.ts';
import type {RouteEdgeType} from './types.ts';

/** The connection's source port name beside its route; in the accent colour while active. */
function SourcePort(props: {
  readonly text: string;
  readonly box: Box;
  readonly active: boolean;
}): ReactElement {
  const {box} = props;
  return (
    <EdgeLabelRenderer>
      <span
        className={props.active ? 'edge-port active' : 'edge-port'}
        style={{
          width: box.width,
          height: box.height,
          transform: `translate(${String(box.x)}px, ${String(box.y)}px)`,
        }}
      >
        {props.text}
      </span>
    </EdgeLabelRenderer>
  );
}

/** The × at the middle of a selected connection on an editable canvas. */
function RemoveButton(props: {
  readonly route: string;
  readonly x: number;
  readonly y: number;
  readonly onRemove: () => void;
}): ReactElement {
  return (
    <EdgeLabelRenderer>
      <button
        type="button"
        className="edge-remove nodrag nopan"
        style={{
          transform: `translate(-50%, -50%) translate(${String(props.x)}px, ${String(props.y)}px)`,
        }}
        aria-label={`Remove connection from ${props.route}`}
        onClick={props.onRemove}
      >
        ×
      </button>
    </EdgeLabelRenderer>
  );
}

/** The source port's name, only while the connection is hovered or selected. */
function shown(port: EdgeRoute['label'], active: boolean): EdgeRoute['label'] {
  return active ? port : null;
}

/** The source port's name beside the route, and × at the middle while selected on an editor. */
export function Overlays(
  props: EdgeProps<RouteEdgeType> & {
    readonly middle: readonly [number, number];
    readonly port: EdgeRoute['label'];
  },
): ReactElement {
  const remove = useEdgeRemoval();
  const {route, active = false} = props.data ?? {};
  const [x, y] = props.middle;
  const removable = remove !== null && props.selected === true && route !== undefined;
  const port = shown(props.port, active);
  return (
    <>
      {port !== null && <SourcePort text={port.text} box={port.placement.box} active={active} />}
      {removable && (
        <RemoveButton
          route={route}
          x={x}
          y={y}
          onRemove={() => {
            remove(props.id);
          }}
        />
      )}
    </>
  );
}
