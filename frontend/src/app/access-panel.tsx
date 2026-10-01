import {useState} from 'react';
import type {ReactElement} from 'react';

interface Props {
  readonly connected: boolean;
  readonly onConnect: (token: string) => void;
  readonly onDisconnect: () => void;
}

export function AccessPanel({connected, onConnect, onDisconnect}: Props): ReactElement {
  const [token, setToken] = useState('');
  if (connected) return <button onClick={onDisconnect}>Disconnect operator access</button>;
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        onConnect(token);
        setToken('');
      }}
    >
      <label>
        Access key
        <input
          type="password"
          autoComplete="off"
          value={token}
          onChange={(event) => {
            setToken(event.target.value);
          }}
        />
      </label>
      <button disabled={token.trim() === ''}>Connect operator access</button>
    </form>
  );
}
