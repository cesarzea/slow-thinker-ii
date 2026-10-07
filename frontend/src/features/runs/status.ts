/** The run's duration from its totals or from its start and end. */
export function runDuration(run: {
  readonly totals: {readonly duration_ms: number} | null;
  readonly created_at: string;
  readonly ended_at: string | null;
}): number | null {
  if (run.totals !== null) return run.totals.duration_ms;
  return run.ended_at === null ? null : Date.parse(run.ended_at) - Date.parse(run.created_at);
}
