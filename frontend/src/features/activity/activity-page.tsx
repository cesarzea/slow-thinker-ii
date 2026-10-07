import {useMemo, useState} from 'react';
import type {ReactElement} from 'react';
import type {OperatorClient} from '../../api/index.ts';
import {activityNames} from './names.ts';
import {FilterChoice, Timeline} from './timeline-view.tsx';
import type {Filter} from './timeline-view.tsx';
import {activityTotals} from './totals.ts';
import {TotalsView} from './totals-view.tsx';
import {useActivityContext, useEvents} from './use-activity.ts';
import './activity.css';

export interface ActivityPageProps {
  readonly client: OperatorClient;
  readonly graphId: string;
  readonly runId: string;
  readonly runHref: string;
}

/** Everything recorded in a run, in order, with filters and totals. */
export function ActivityPage(props: ActivityPageProps): ReactElement {
  const context = useActivityContext(props.client, props.runId).data;
  const {events, finished, error} = useEvents(props.client, props.runId);
  const [filter, setFilter] = useState<Filter>('all');
  const names = useMemo(
    () => activityNames(context?.document ?? null, context?.catalog ?? null),
    [context],
  );
  return (
    <div className="activity-page">
      <div className="activity-header">
        <h1>Activity</h1>
        <a href={props.runHref}>Back to the run</a>
        {!finished && <span className="muted">Recording…</span>}
      </div>
      {error !== null && <p role="alert">Could not read the activity. {error}</p>}
      <div className="activity-body">
        <TotalsView totals={activityTotals(events, names)} />
        <section className="activity-timeline" aria-label="Recorded events">
          <FilterChoice value={filter} onChange={setFilter} />
          <Timeline events={events} names={names} filter={filter} />
        </section>
      </div>
    </div>
  );
}
