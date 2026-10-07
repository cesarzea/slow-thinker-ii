import {useCallback, useEffect, useRef, useState} from 'react';
import type {Dispatch, SetStateAction} from 'react';
import {OperatorClient, observeAuthentication} from '../api/index.ts';
import type {Access} from '../api/index.ts';
import {forgetToken, storeToken, storedToken} from './token-storage.ts';

/** `undefined` before connecting; `null` on a server without operator authentication. */
type Credential = string | null | undefined;
interface Connection {
  readonly credential: Credential;
  readonly generation: number;
  readonly notice: string | null;
  /** Whether the server's access mode is still being read. */
  readonly checking: boolean;
}
interface ConnectionControls {
  readonly connection: Connection;
  readonly connect: (credential: string) => void;
  readonly disconnect: () => void;
}
type SetConnection = Dispatch<SetStateAction<Connection>>;

const INVALID = 'The operator token is no longer accepted. Connect again to continue.';
const REQUIRED = 'This server now asks for the operator token. Connect to continue.';

const started =
  (credential: Credential) =>
  (current: Connection): Connection => ({
    credential,
    generation: current.generation + 1,
    notice: null,
    checking: false,
  });
const ended =
  (notice: string) =>
  (current: Connection): Connection => ({...started(undefined)(current), notice});

/** Changes the credential; a 401 or 403 for it ends the connection and forgets the token. */
function useAuthentication(setConnection: SetConnection): (credential: Credential) => void {
  const unsubscribe = useRef<(() => void) | null>(null);
  useEffect(
    () => () => {
      unsubscribe.current?.();
    },
    [],
  );
  return useCallback(
    (credential: Credential) => {
      const invalidated = (): void => {
        unsubscribe.current?.();
        unsubscribe.current = null;
        if (credential !== null) forgetToken();
        setConnection(ended(credential === null ? REQUIRED : INVALID));
      };
      unsubscribe.current?.();
      unsubscribe.current =
        credential === undefined ? null : observeAuthentication(credential, invalidated);
      setConnection(started(credential));
    },
    [setConnection],
  );
}

/**
 * Reads the server's access mode once. Without operator authentication it connects at
 * once; otherwise, or when the mode cannot be read, it uses the token kept for this tab
 * or asks for one.
 */
function useAccessMode(
  change: (credential: Credential) => void,
  setConnection: SetConnection,
): void {
  useEffect(() => {
    const controller = new AbortController();
    const settle = (mode: Access['authentication'] | null): void => {
      if (controller.signal.aborted) return;
      const credential = mode === 'none' ? null : storedToken();
      if (credential === null && mode !== 'none')
        setConnection((current) => ({...current, checking: false}));
      else change(credential);
    };
    new OperatorClient(null).access(controller.signal).then(
      (access) => {
        settle(access.authentication);
      },
      () => {
        settle(null);
      },
    );
    return () => {
      controller.abort();
    };
  }, [change, setConnection]);
}

/** The operator credential of this tab; a 401 or 403 from the API ends the connection. */
export function useConnection(): ConnectionControls {
  const [connection, setConnection] = useState<Connection>({
    credential: undefined,
    generation: 0,
    notice: null,
    checking: true,
  });
  const change = useAuthentication(setConnection);
  useAccessMode(change, setConnection);
  return {
    connection,
    connect: (credential) => {
      storeToken(credential);
      change(credential);
    },
    disconnect: () => {
      forgetToken();
      change(undefined);
    },
  };
}
