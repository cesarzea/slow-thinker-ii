import type {RunStatus, RunSummary} from '../../api/index.ts';
import {durationLabel, moneyLabel, runStatusText} from '../../ui/index.ts';

/** One row of the runs table, already formatted. */
export interface RunRow {
  readonly graphId: string;
  readonly runId: string;
  /** “<graph name> · Run <n>”. */
  readonly name: string;
  readonly version: string;
  readonly status: RunStatus;
  readonly statusText: string;
  readonly createdAt: string;
  readonly started: string;
  readonly duration: string;
  readonly llmCalls: string;
  readonly cost: string;
}

const ACTIVE: ReadonlySet<RunStatus> = new Set(['starting', 'running']);
const started = new Intl.DateTimeFormat('en', {dateStyle: 'medium', timeStyle: 'medium'});

/** Whether a run has not finished yet. */
export function isActive(run: RunSummary): boolean {
  return ACTIVE.has(run.status);
}

/**
 * Numbers the runs of a newest-first list: each run's position among the runs of its
 * graph in that list, oldest first.
 */
export function numberedRuns(
  runs: readonly RunSummary[],
): {readonly run: RunSummary; readonly number: number}[] {
  const counts = new Map<string, number>();
  return runs
    .toReversed()
    .map((run) => {
      const number = (counts.get(run.graph_id) ?? 0) + 1;
      counts.set(run.graph_id, number);
      return {run, number};
    })
    .toReversed();
}

function duration(run: RunSummary): number | null {
  if (run.totals !== null) return run.totals.duration_ms;
  return run.ended_at === null ? null : Date.parse(run.ended_at) - Date.parse(run.created_at);
}

/** The rows of a newest-first run list; graphs without a known name show their id. */
export function runRows(
  runs: readonly RunSummary[],
  graphNames: ReadonlyMap<string, string>,
): RunRow[] {
  return numberedRuns(runs).map(({run, number}) => ({
    graphId: run.graph_id,
    runId: run.run_id,
    name: `${graphNames.get(run.graph_id) ?? run.graph_id} · Run ${String(number)}`,
    version: run.version === null ? `change ${String(run.change)}` : `v${String(run.version)}`,
    status: run.status,
    statusText: runStatusText(run.status, run.reason),
    createdAt: run.created_at,
    started: started.format(new Date(run.created_at)),
    duration: durationLabel(duration(run)),
    llmCalls: run.totals === null ? '—' : String(run.totals.llm_calls),
    cost: run.totals === null ? '—' : moneyLabel(run.totals.cost_usd),
  }));
}
