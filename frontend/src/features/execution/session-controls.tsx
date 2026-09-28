import {useState} from 'react';
import type {ReactElement} from 'react';
import {PageControls} from './page-controls.tsx';
import type {ExecutionCommands} from './commands.ts';
import type {ExecutionState, ExecutionStore} from './state.ts';

interface Props {
  readonly state: ExecutionState;
  readonly store: ExecutionStore;
  readonly commands: ExecutionCommands;
}

export function SessionControls({state, store, commands}: Props): ReactElement {
  return (
    <fieldset disabled={state.pending !== null || state.busy}>
      <legend>Sesión de trabajo</legend>
      <SessionSelector state={state} store={store} />
      <PageControls
        kind="workspace"
        current={state.workspaceCursor}
        next={state.workspace?.sessions.next_cursor ?? null}
        store={store}
      />
      <NewSession commands={commands} />
    </fieldset>
  );
}

function NewSession({commands}: Pick<Props, 'commands'>): ReactElement {
  const [name, setName] = useState('');
  return (
    <div>
      <label>
        Nueva sesión
        <input
          value={name}
          onChange={(event) => {
            setName(event.target.value);
          }}
          maxLength={200}
        />
      </label>
      <button
        disabled={name.trim() === ''}
        onClick={() => {
          void commands.createSession(name);
        }}
      >
        Crear sesión
      </button>
    </div>
  );
}

function SessionSelector({state, store}: Pick<Props, 'state' | 'store'>): ReactElement {
  const sessions = state.workspace?.sessions.items ?? [];
  return (
    <label>
      Sesión guardada
      <select
        value={state.sessionId}
        onChange={(event) => {
          store.selectSession(event.target.value);
        }}
      >
        <option value="">Selecciona una sesión</option>
        {state.sessionId !== '' &&
          !sessions.some((item) => item.session_id === state.sessionId) && (
            <option value={state.sessionId}>Sesión seleccionada</option>
          )}
        {sessions.map((session) => (
          <option key={session.session_id} value={session.session_id}>
            {session.name}
          </option>
        ))}
      </select>
    </label>
  );
}
