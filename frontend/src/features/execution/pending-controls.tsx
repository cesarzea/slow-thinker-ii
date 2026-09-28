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
    <aside aria-label="Solicitud pendiente">
      <p>Solicitud pendiente de confirmación. No se enviará otro inicio.</p>
      <button onClick={refresh}>Consultar recibo</button>
      <PendingActions state={state} commands={commands} start={start} />
      {!start && <p>Dejar de seguirla no cancela una solicitud que llegue al servidor.</p>}
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
          Reenviar la misma orden
        </ActionButton>
      )}
      {start && (
        <ActionButton action={() => commands.withdraw()}>Retirar inicio pendiente</ActionButton>
      )}
      {!start && (
        <ActionButton
          disabled={state.busy}
          action={() => {
            commands.forgetNonStart();
          }}
        >
          Dejar de seguir esta solicitud
        </ActionButton>
      )}
    </div>
  );
}
