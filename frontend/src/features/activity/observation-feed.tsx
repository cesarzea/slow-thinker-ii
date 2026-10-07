import type {ReactElement} from 'react';
import {eventPoint} from '../../api/index.ts';
import type {OperatorClient, PointId, RunEvent} from '../../api/index.ts';
import {Button} from '../../ui/index.ts';
import {FeedItem} from './feed-item.tsx';
import {LIFECYCLE, ViewChoice, useView} from './feed-view.tsx';
import type {View} from './feed-view.tsx';
import {activityNames} from './names.ts';
import type {Names} from './names.ts';
import {useActivityContext, useEvents} from './use-activity.ts';
import './activity.css';

export interface ObservationFeedProps {
  readonly client: OperatorClient;
  readonly runId: string;
  /** The points shown: every observed point, or the one the operator focused. */
  readonly points: readonly PointId[];
  readonly focus: PointId | null;
  readonly labels: Readonly<Partial<Record<PointId, string>>>;
  readonly onClearFocus: () => void;
}

/** Why nothing is listed, or null when something is. */
function emptyText(points: readonly PointId[], shown: readonly RunEvent[]): string | null {
  if (points.length === 0) return 'Check points on the left to observe them.';
  return shown.length === 0 ? 'Nothing recorded here yet.' : null;
}

function FeedTitle(props: ObservationFeedProps & {readonly title: string}): ReactElement {
  return (
    <div className="feed-title">
      <h2>{props.title}</h2>
      {props.focus !== null && (
        <Button size="sm" variant="ghost" onClick={props.onClearFocus}>
          All observed
        </Button>
      )}
    </div>
  );
}

/** The events at the shown points, without the lifecycle ones in the Content view. */
function shownEvents(events: readonly RunEvent[], points: readonly PointId[], view: View) {
  const shown = new Set(points);
  return events.filter(
    (event) => shown.has(eventPoint(event)) && (view === 'all' || !LIFECYCLE.has(event.kind)),
  );
}

/**
 * The events of a run recorded at the given observation points, as they arrive: what each
 * message carried, each model reply, result and report, with the recorded detail on demand.
 */
/** “Observed”, or the activity of the focused point. */
function feedTitle(props: ObservationFeedProps): string {
  if (props.focus === null) return 'Observed';
  return `Activity of ${props.labels[props.focus] ?? props.focus}`;
}

/** Readable names of what the run recorded, once its catalog and document are read. */
function useNames(client: OperatorClient, runId: string): Names {
  const context = useActivityContext(client, runId).data;
  return activityNames(context?.document ?? null, context?.catalog ?? null);
}

export function ObservationFeed(props: ObservationFeedProps): ReactElement {
  const {events, error} = useEvents(props.client, props.runId);
  const names = useNames(props.client, props.runId);
  const [view, setView] = useView();
  const shown = shownEvents(events, props.points, view);
  const empty = emptyText(props.points, shown);
  const title = feedTitle(props);
  return (
    <section className="observation-feed" aria-label={title}>
      <FeedTitle {...props} title={title} />
      <ViewChoice view={view} onChange={setView} />
      {error !== null && <p role="alert">{error}</p>}
      {empty !== null && <p className="muted">{empty}</p>}
      <ol className="feed-list">
        {shown.map((event) => (
          <FeedItem
            key={event.seq}
            event={event}
            events={events}
            names={names}
            label={props.labels[eventPoint(event)] ?? eventPoint(event)}
          />
        ))}
      </ol>
    </section>
  );
}
