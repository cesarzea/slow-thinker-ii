import type {ReactElement} from 'react';
import type {PointId} from '../../api/index.ts';
import {Button} from '../../ui/index.ts';
import {points} from './observation-points.ts';
import {PointGroup} from './observation-rows.tsx';
import type {PanelProps} from './observation-rows.tsx';

/** Observe every point, or none. */
function ObserveAll(props: {
  readonly ids: readonly PointId[];
  readonly onObserve: PanelProps['onObserve'];
}): ReactElement {
  const choice = (label: string, observe: boolean): ReactElement => (
    <Button
      size="sm"
      variant="ghost"
      onClick={() => {
        props.onObserve(props.ids, observe);
      }}
    >
      {label}
    </Button>
  );
  return (
    <div className="observation-actions">
      {choice('All', true)}
      {choice('None', false)}
    </div>
  );
}

/**
 * Run mode's left panel: every observation point of the graph. A node unfolds into what it
 * records; a checked point's events appear live in the run panel, and clicking a point shows
 * only its activity.
 */
export function ObservationPanel(props: PanelProps): ReactElement {
  const all = points(props.document, props.catalog);
  const ids = [all.run, ...all.nodes, ...all.connections].flatMap((point) => point.members);
  return (
    <nav className="palette observation-panel" aria-label="Observation points">
      <div className="palette-heading">
        <h2 className="panel-title">Observation points</h2>
      </div>
      <ObserveAll ids={ids} onObserve={props.onObserve} />
      <PointGroup {...props} title="Run" points={[all.run]} />
      <PointGroup {...props} title="Nodes" points={all.nodes} />
      <PointGroup {...props} title="Connections" points={all.connections} />
    </nav>
  );
}
