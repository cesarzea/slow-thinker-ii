import {useEffect, useRef, useState, useSyncExternalStore} from 'react';
import {createExecutionModel} from './model.ts';
import type {ExecutionCommands} from './commands.ts';
import type {ExecutionStore} from './state.ts';
import type {ExecutionState} from './state.ts';

interface ExecutionModel {
  readonly state: ExecutionState;
  readonly store: ExecutionStore;
  readonly commands: ExecutionCommands;
  readonly refresh: () => void;
}

export function useExecution(credential: string): ExecutionModel {
  const [model] = useState(() => createExecutionModel(credential, localStorage));
  const state = useSyncExternalStore(model.store.subscribe, model.store.snapshot);
  const lifetime = useRef<AbortController | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    lifetime.current = controller;
    model.store.setClosed(false);
    void model.polling.refresh(controller.signal);
    const timer = setInterval(() => {
      void model.polling.refresh(controller.signal);
    }, 1000);
    return () => {
      model.store.setClosed(true);
      controller.abort();
      clearInterval(timer);
    };
  }, [model, state.runId]);
  const refresh = (): void => {
    if (lifetime.current !== null) void model.polling.refresh(lifetime.current.signal);
  };
  return {state, store: model.store, commands: model.commands, refresh};
}
