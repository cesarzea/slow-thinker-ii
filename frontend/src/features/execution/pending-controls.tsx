import type {ReactElement} from 'react';
import {ActionButton} from '../../ui/index.ts';
import type {ExecutionCommands} from './commands.ts';
import type {ExecutionState} from './state.ts';

interface Props {
  readonly state: ExecutionState;
  readonly commands: ExecutionCommands;
  readonly refresh: () => void;
}

export function PendingControls({state, commands, refresh}: Props): ReactElement | null {
  if (state.pending === null) return null;
  const start = state.pending.startsWith('start-');
  return (
    <aside aria-label="Pending request">
      <p>Request awaiting confirmation. No other start request will be sent.</p>
      <button onClick={refresh}>Check receipt</button>
      <PendingActions state={state} commands={commands} start={start} />
      {!start && <p>Stopping tracking does not cancel a request that reaches the server.</p>}
    </aside>
  );
}

function PendingActions({
  state,
  commands,
  start,
}: Pick<Props, 'state' | 'commands'> & {readonly start: boolean}): ReactElement {
  return (
    <div className="actions">
      {commands.canRetry() && (
        <ActionButton disabled={state.busy} action={() => commands.retry()}>
          Resend the same command
        </ActionButton>
      )}
      {start && (
        <ActionButton action={() => commands.withdraw()}>Withdraw pending start</ActionButton>
      )}
      {!start && (
        <ActionButton
          disabled={state.busy}
          action={() => {
            commands.forgetNonStart();
          }}
        >
          Stop tracking this request
        </ActionButton>
      )}
    </div>
  );
}
