import type {ReactElement} from 'react';
import {BaseEdge} from '@xyflow/react';
import type {EdgeProps} from '@xyflow/react';
import type {VisualEdge} from './types.ts';

export function ReturnEdge(props: EdgeProps<VisualEdge>): ReactElement {
  const {sourceX, sourceY, targetX, targetY} = props;
  const lane = Math.max(sourceY, targetY) + 130;
  const path = `M ${point(sourceX, sourceY)} C ${point(sourceX + 70, lane)} ${point(targetX - 70, lane)} ${point(targetX, targetY)}`;
  return (
    <BaseEdge
      id={props.id}
      label={props.label}
      markerEnd={props.markerEnd ?? ''}
      style={props.style ?? {}}
      path={path}
      labelX={(sourceX + targetX) / 2}
      labelY={lane - 32.5}
    />
  );
}
function point(x: number, y: number): string {
  return `${String(x)},${String(y)}`;
}
