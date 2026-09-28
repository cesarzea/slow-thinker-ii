import {act, render} from '@testing-library/react';
import {vi} from 'vitest';
import {ExecutionPanel} from '../../src/features/execution/index.ts';
import {graph} from './operator-data.ts';
import {OperatorServer} from './operator-server.ts';

export function executionView(server = new OperatorServer()): OperatorServer {
  vi.stubGlobal('fetch', server.fetch);
  render(<ExecutionPanel credential="fixture-key" graph={graph} onInspect={vi.fn()} />);
  return server;
}

export async function tick(): Promise<void> {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(1000);
  });
}
