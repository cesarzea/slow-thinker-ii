import {OperatorClient} from '../../api/index.ts';
import {ExecutionCommands} from './commands.ts';
import {ExecutionPolling} from './polling.ts';
import {ExecutionStore} from './state.ts';
import type {IdentityStorage} from './state.ts';

export interface ExecutionModel {
  readonly store: ExecutionStore;
  readonly commands: ExecutionCommands;
  readonly polling: ExecutionPolling;
}

export function createExecutionModel(credential: string, storage: IdentityStorage): ExecutionModel {
  const client = new OperatorClient(credential);
  const store = new ExecutionStore(storage);
  const commands = new ExecutionCommands(store, client, storage);
  return {store, commands, polling: new ExecutionPolling(store, commands, client)};
}
