import {useState} from 'react';
import type {ReactElement} from 'react';
import {AccessPanel} from './access-panel.tsx';
import {CatalogPanel} from './catalog-panel.tsx';

interface Connection {
  readonly credential: string | undefined;
  readonly generation: number;
}

export function App(): ReactElement {
  const [connection, setConnection] = useState<Connection>({credential: undefined, generation: 0});
  const connect = (credential: string | undefined): void => {
    setConnection({credential, generation: connection.generation + 1});
  };
  return (
    <main>
      <header>
        <p>Agent collaboration lab</p>
        <h1>Slow Thinker II</h1>
      </header>
      <AccessPanel
        connected={connection.credential !== undefined}
        onConnect={connect}
        onDisconnect={() => {
          connect(undefined);
        }}
      />
      <CatalogPanel credential={connection.credential} generation={connection.generation} />
    </main>
  );
}
