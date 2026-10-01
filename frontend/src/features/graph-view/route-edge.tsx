import type {ReactElement} from 'react';
import {BaseEdge, getBezierPath} from '@xyflow/react';
import type {EdgeProps} from '@xyflow/react';
import type {VisualEdge} from './types.ts';
import {boundaryDistance} from './boundary-routes.ts';

type Path = readonly [string, number, number, number, number];
export function RouteEdge(props: EdgeProps<VisualEdge>): ReactElement {
  const [path, labelX, labelY, endX, endY] = routePath(props);
  return (
    <>
      <BaseEdge
        id={props.id}
        label={props.label}
        markerEnd={props.markerEnd ?? ''}
        style={props.style ?? {}}
        path={path}
        labelX={labelX}
        labelY={labelY - 17}
      />
      {props.data?.system === true && (
        <g className="system-markers" aria-label="System mediation" role="img">
          <circle cx={labelX} cy={labelY} r={5} />
          {props.data.terminal && <circle cx={endX} cy={endY} r={5} />}
        </g>
      )}
    </>
  );
}
function routePath(props: EdgeProps<VisualEdge>): Path {
  if (props.data?.entry === true) {
    return horizontalPath(props.targetX - boundaryDistance, props.targetY, props.targetX);
  }
  if (props.data?.terminal === true) {
    return horizontalPath(props.sourceX, props.sourceY, props.sourceX + boundaryDistance);
  }
  if (props.data?.returning !== true) {
    const [path, x, y] = getBezierPath(props);
    return [path, x, y, props.targetX, props.targetY];
  }
  const {sourceX, sourceY, targetX, targetY} = props;
  const lane = Math.max(sourceY, targetY) + 150;
  const path = `M ${point(sourceX, sourceY)} C ${point(sourceX, lane)} ${point(targetX, lane)} ${point(targetX, targetY)}`;
  return [path, (sourceX + targetX) / 2, (sourceY + targetY) / 8 + lane * 0.75, targetX, targetY];
}
function horizontalPath(sourceX: number, y: number, targetX: number): Path {
  return [`M ${point(sourceX, y)} L ${point(targetX, y)}`, (sourceX + targetX) / 2, y, targetX, y];
}
function point(x: number, y: number): string {
  return `${String(x)},${String(y)}`;
}
