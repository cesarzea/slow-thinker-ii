import type {ConfigurationCatalog, EffectiveLimits, LimitsCommand} from '../../api/index.ts';

export type LimitName = keyof EffectiveLimits;
export interface LimitField {
  readonly name: LimitName;
  readonly label: string;
  readonly budget: boolean;
}
export const limitFields: readonly LimitField[] = [
  {name: 'run_seconds', label: 'Run deadline (seconds)', budget: false},
  {name: 'call_seconds', label: 'Call deadline (seconds)', budget: false},
  {name: 'startup_seconds', label: 'Startup deadline (seconds)', budget: false},
  {name: 'shutdown_seconds', label: 'Shutdown deadline (seconds)', budget: false},
  {name: 'max_calls', label: 'Maximum calls', budget: false},
  {name: 'max_depth', label: 'Maximum call depth', budget: false},
  {name: 'max_payload_bytes', label: 'Maximum payload (bytes)', budget: false},
  {name: 'run_budget', label: 'Run budget (USD)', budget: true},
  {name: 'session_budget', label: 'Session budget (USD)', budget: true},
  {name: 'month_budget', label: 'Month budget (USD)', budget: true},
];
export interface LimitsState {
  readonly revision: string;
  readonly current: EffectiveLimits;
  readonly edits: Partial<Record<LimitName, string>>;
  readonly frozen: string | null;
  readonly pending: boolean;
  readonly uncertain: boolean;
  readonly message: string | null;
}
export function initialLimits(catalog: ConfigurationCatalog): LimitsState {
  return {
    revision: catalog.configuration_revision,
    current: catalog.limits.current,
    edits: {},
    frozen: null,
    pending: false,
    uncertain: false,
    message: null,
  };
}
export function commandBody(state: LimitsState): string {
  const limits = Object.fromEntries(
    limitFields
      .filter((field) => state.edits[field.name] !== undefined)
      .map((field) => [
        field.name,
        field.budget ? state.edits[field.name] : Number(state.edits[field.name]),
      ]),
  );
  return JSON.stringify({
    command_id: crypto.randomUUID().replaceAll('-', ''),
    expected_revision: state.revision,
    limits,
  });
}
export function acceptedLimits(state: LimitsState, body: string, revision: string): LimitsState {
  const command = JSON.parse(body) as LimitsCommand;
  return {
    ...state,
    current: mergedLimits(state.current, command.limits),
    revision,
    edits: {},
    frozen: null,
    pending: false,
    uncertain: false,
    message: `Settings confirmed under revision ${revision}. Existing spending is retained.`,
  };
}

function mergedLimits(current: EffectiveLimits, changes: LimitsCommand['limits']): EffectiveLimits {
  // The frozen command has passed the public API validator; its JSON body cannot contain undefined.
  return {...current, ...changes} as EffectiveLimits;
}
