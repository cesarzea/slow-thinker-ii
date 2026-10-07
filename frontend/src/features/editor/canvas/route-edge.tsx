import type {ReactElement} from 'react';
import {BaseEdge, getBezierPath} from '@xyflow/react';
import type {EdgeProps} from '@xyflow/react';
import {connectionPoint} from '../../../api/index.ts';
import {Overlays} from './edge-overlays.tsx';
import {ObservationDot, useObservation} from './observation-dot.tsx';
import {useEdgeRoute} from './routing/use-routes.ts';
import type {RouteEdgeType} from './types.ts';

/** Run mode's dot at the middle of the connection, with the messages it carried. */
function EdgeDot(props: {
  readonly edge: EdgeProps<RouteEdgeType>;
  readonly x: number;
  readonly y: number;
}): ReactElement | null {
  const observation = useObservation();
  const {data, label} = props.edge;
  if (observation === null || data === undefined) return null;
  return (
    <ObservationDot
      id={connectionPoint(data.from, data.to)}
      route={data.route}
      x={props.x}
      y={props.y}
      count={typeof label === 'string' ? label : null}
      observation={observation}
    />
  );
}

/**
 * A connection along its route around the cards, with its source port's name beside it.
 * Until the canvas has measured both handles, a curve between them. In run mode the count of
 * messages sits in the observation dot instead of a label.
 */
export function RouteEdge(props: EdgeProps<RouteEdgeType>): ReactElement {
  const routed = useEdgeRoute(props.id);
  const observing = useObservation() !== null;
  const [path, labelX, labelY] =
    routed === undefined
      ? getBezierPath(props)
      : [routed.route.path, routed.route.middle.x, routed.route.middle.y];
  return (
    <>
      <BaseEdge
        id={props.id}
        path={path}
        label={observing ? undefined : props.label}
        labelX={labelX}
        labelY={labelY}
        labelShowBg
        labelBgPadding={[4, 2]}
        labelBgBorderRadius={8}
        markerEnd={props.markerEnd ?? ''}
        style={props.style ?? {}}
      />
      <Overlays {...props} middle={[labelX, labelY]} port={routed?.label ?? null} />
      <EdgeDot edge={props} x={labelX} y={labelY} />
    </>
  );
}
