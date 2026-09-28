import {useEffect, useState, useSyncExternalStore} from 'react';
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
  useEffect(() => {
    const controller = new AbortController();
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
  }, [model]);
  const refresh = (): void => {
    void model.polling.refresh(new AbortController().signal);
  };
  return {state, store: model.store, commands: model.commands, refresh};
}
