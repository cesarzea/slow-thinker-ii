import {useEffect, useState} from 'react';

interface ReadState<T> {
  readonly data: T | null;
  readonly error: string | null;
}

export function useRead<T>(read: (signal: AbortSignal) => Promise<T>): ReadState<T> & {
  readonly refresh: () => void;
} {
  const [state, setState] = useState<ReadState<T>>({data: null, error: null});
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void read(controller.signal).then(
      (data) => {
        if (!controller.signal.aborted) setState({data, error: null});
      },
      () => {
        if (!controller.signal.aborted)
          setState({data: null, error: 'No se pudo cargar la evidencia. Vuelve a consultar.'});
      },
    );
    return () => {
      controller.abort();
    };
  }, [read, revision]);
  const refresh = (): void => {
    setState({data: null, error: null});
    setRevision((value) => value + 1);
  };
  return {...state, refresh};
}
