import type {RunReason, RunStatus} from '../api/index.ts';

const REASONS: Readonly<Record<RunReason, string>> = {
  activation_limit: 'activation limit reached',
  time_limit: 'time limit reached',
  budget_run: 'run budget exhausted',
  budget_day: 'daily budget exhausted',
  budget_month: 'monthly budget exhausted',
  startup_failed: 'a component could not start',
  activation_failed: 'an activation failed',
  interrupted: 'interrupted by a server restart',
  internal_error: 'internal error',
  cancelled: 'stopped by the operator',
};

/**
 * The status line of a run: “Completed”, “Cancelled”, “Running”, “Starting”, or
 * “Stopped: <reason>” and “Failed: <reason>”; the detail is shown separately.
 */
export function runStatusText(status: RunStatus, reason: RunReason | null): string {
  const label = reason === null ? '' : `: ${REASONS[reason]}`;
  const texts: Readonly<Record<RunStatus, string>> = {
    starting: 'Starting',
    running: 'Running',
    completed: 'Completed',
    stopped: `Stopped${label}`,
    failed: `Failed${label}`,
    cancelled: 'Cancelled',
  };
  return texts[status];
}

export function durationLabel(milliseconds: number | null): string {
  if (milliseconds === null) return '—';
  if (milliseconds < 1000) return `${String(Math.round(milliseconds))} ms`;
  return `${(milliseconds / 1000).toFixed(1)} s`;
}

/** What a run executed: “version 3”, or “change 151” for a change never activated. */
export function runSourceText(run: {
  readonly version: number | null;
  readonly change: number;
}): string {
  return run.version === null ? `change ${String(run.change)}` : `version ${String(run.version)}`;
}
