import {useEffect, useRef} from 'react';
import type {Requests} from './types.ts';

export function useRequests(): Requests {
  const active = useRef<AbortController | null>(null);
  useEffect(
    () => () => {
      active.current?.abort();
    },
    [],
  );
  return {
    begin: () => {
      active.current?.abort();
      const controller = new AbortController();
      active.current = controller;
      return controller;
    },
    cancel: () => {
      active.current?.abort();
    },
  };
}
