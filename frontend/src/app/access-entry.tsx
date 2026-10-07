import {useId, useState} from 'react';
import type {ReactElement, SubmitEvent} from 'react';

interface Props {
  readonly notice: string | null;
  readonly onConnect: (credential: string) => void;
}

function TokenForm({onConnect}: Pick<Props, 'onConnect'>): ReactElement {
  const id = useId();
  const [token, setToken] = useState('');
  const submit = (event: SubmitEvent): void => {
    event.preventDefault();
    if (token.trim() !== '') onConnect(token.trim());
  };
  return (
    <form className="access-form" onSubmit={submit}>
      <label htmlFor={id}>Operator token</label>
      <input
        id={id}
        type="password"
        autoComplete="off"
        value={token}
        onChange={(event) => {
          setToken(event.target.value);
        }}
      />
      <button type="submit" className="primary" disabled={token.trim() === ''}>
        Connect
      </button>
    </form>
  );
}

/** Asks for the operator token configured on this server. */
export function AccessEntry({notice, onConnect}: Props): ReactElement {
  return (
    <main className="access-entry">
      <h1>Slow Thinker II</h1>
      <p>
        Build graphs of LLM calls and components, run them within limits and budgets, and see
        everything they did.
      </p>
      {notice !== null && <p role="alert">{notice}</p>}
      <TokenForm onConnect={onConnect} />
      <p className="muted">
        Use the operator token configured on this server. It is kept in this tab until you
        disconnect or close it.
      </p>
    </main>
  );
}
