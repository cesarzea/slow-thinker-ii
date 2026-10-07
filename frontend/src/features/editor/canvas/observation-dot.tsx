import {createContext, use} from 'react';
import type {ReactElement} from 'react';
import {EdgeLabelRenderer} from '@xyflow/react';
import type {PointId} from '../../../api/index.ts';

/** Run mode's observation points on the canvas: which are observed, and toggling one. */
export interface CanvasObservation {
  readonly observed: ReadonlySet<PointId>;
  readonly toggle: (id: PointId) => void;
}

export const ObservationContext = createContext<CanvasObservation | null>(null);

export const useObservation = (): CanvasObservation | null => use(ObservationContext);

/**
 * A connection's observation point at its middle: filled while observed, with the number of
 * messages it carried; a click observes it or stops observing it.
 */
export function ObservationDot(props: {
  readonly id: PointId;
  readonly route: string;
  readonly x: number;
  readonly y: number;
  readonly count: string | null;
  readonly observation: CanvasObservation;
}): ReactElement {
  const observed = props.observation.observed.has(props.id);
  const at = `translate(${String(props.x)}px, ${String(props.y)}px)`;
  return (
    <EdgeLabelRenderer>
      <button
        type="button"
        className={`observation-dot${observed ? ' observed' : ''} nodrag nopan`}
        style={{transform: `translate(-50%, -50%) ${at}`}}
        aria-pressed={observed}
        aria-label={`Observe ${props.route}`}
        title={observed ? `Observed: ${props.route}` : `Observe ${props.route}`}
        onClick={() => {
          props.observation.toggle(props.id);
        }}
      >
        {props.count}
      </button>
    </EdgeLabelRenderer>
  );
}
