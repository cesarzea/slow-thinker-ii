import type {ReactElement} from 'react';
import type {Limits, RunDetail} from '../../api/index.ts';
import {budgetShare, durationLabel, moneyLabel, runStatusText} from '../../ui/index.ts';
import {runDuration} from './status.ts';

type Figure = readonly [string, string];

function spending(run: RunDetail, limits: Limits | null): Figure[] {
  const cost = run.totals?.cost_usd;
  const budget = limits?.budget_usd;
  if (cost === undefined)
    return [
      ['Cost', '—'],
      ['Budget used', '—'],
    ];
  const share =
    budget === undefined ? '—' : `${budgetShare(cost, budget)} of ${moneyLabel(budget)}`;
  return [
    ['Cost', moneyLabel(cost)],
    ['Budget used', share],
  ];
}

function runFigures(run: RunDetail, limits: Limits | null): Figure[] {
  const counted = Object.values(run.activations_by_node).reduce((sum, count) => sum + count, 0);
  return [
    ['Duration', durationLabel(runDuration(run))],
    ['Activations', String(run.totals?.activations ?? counted)],
    ['LLM calls', run.totals === null ? '—' : String(run.totals.llm_calls)],
    ...spending(run, limits),
  ];
}

/** The status line, with the run's detail in its own paragraph below it. */
function RunStatusLine({run}: {readonly run: RunDetail}): ReactElement {
  return (
    <>
      <p className={`run-status ${run.status}`} role="status">
        {runStatusText(run.status, run.reason)}
      </p>
      {run.detail !== null && run.detail !== '' && <p className="run-detail">{run.detail}</p>}
    </>
  );
}

/** Status, duration, activations, LLM calls, cost and budget used. */
export function RunFigures(props: {
  readonly run: RunDetail;
  readonly limits: Limits | null;
}): ReactElement {
  const {run} = props;
  return (
    <>
      <RunStatusLine run={run} />
      <dl className="figures">
        {runFigures(run, props.limits).map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </>
  );
}
