import type {ReactElement} from 'react';
import {AccessEntry} from './access-entry.tsx';
import {useConnection} from './use-connection.ts';
import {Workspace} from './workspace.tsx';
import './styles/base.css';
import './styles/shell.css';
import './styles/pages.css';

/**
 * The interface: the product at once on a server without operator authentication;
 * otherwise the access entry until an operator token is given or kept for this tab.
 */
export function App(): ReactElement {
  const {connection, connect, disconnect} = useConnection();
  if (connection.checking) return <p className="muted page-loading">Connecting…</p>;
  if (connection.credential === undefined)
    return (
      <AccessEntry key={connection.generation} notice={connection.notice} onConnect={connect} />
    );
  return (
    <Workspace
      key={connection.generation}
      credential={connection.credential}
      onDisconnect={connection.credential === null ? null : disconnect}
    />
  );
}
