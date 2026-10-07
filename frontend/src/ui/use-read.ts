import {useEffect, useState} from 'react';
import {errorMessage} from '../api/index.ts';

interface ReadState<T> {
  readonly data: T | null;
  readonly error: string | null;
}
export type ReadResult<T> = ReadState<T> & {readonly refresh: () => void};

/** Run an abortable read whenever its function changes; stale replies are ignored. */
export function useRead<T>(read: (signal: AbortSignal) => Promise<T>): ReadResult<T> {
  const [state, setState] = useState<ReadState<T> & {readonly origin: typeof read | null}>({
    data: null,
    error: null,
    origin: null,
  });
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    read(controller.signal).then(
      (data) => {
        if (!controller.signal.aborted) setState({data, error: null, origin: read});
      },
      (error: unknown) => {
        if (!controller.signal.aborted)
          setState({data: null, error: errorMessage(error), origin: read});
      },
    );
    return () => {
      controller.abort();
    };
  }, [read, revision]);
  const refresh = (): void => {
    setState({data: null, error: null, origin: read});
    setRevision((value) => value + 1);
  };
  const current = state.origin === read ? state : {data: null, error: null};
  return {...current, refresh};
}
