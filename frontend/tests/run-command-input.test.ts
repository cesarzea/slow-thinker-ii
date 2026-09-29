import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {createExecutionModel} from '../src/features/execution/index.ts';
import {graph} from './support/operator-data.ts';
import {singleDetail} from './support/projection-data.ts';
import {OperatorServer} from './support/operator-server.ts';
let server: OperatorServer;
beforeEach(() => {
  localStorage.clear();
  server = new OperatorServer();
  vi.stubGlobal('fetch', server.fetch);
});
afterEach(() => {
  vi.unstubAllGlobals();
});
it.each([[], null])(
  'rejects non-object values at the command boundary as well as in the form',
  async (value) => {
    const model = createExecutionModel('key', localStorage);
    await model.polling.refresh(new AbortController().signal);
    await model.commands.start({...graph, input_schema: {}}, value);
    expect(server.mutations).toHaveLength(0);
  },
);
it('preserves the legacy problem-string command adapter with an explicit object schema', async () => {
  const model = createExecutionModel('key', localStorage);
  await model.polling.refresh(new AbortController().signal);
  await model.commands.start({...graph, input_schema: singleDetail.input_schema}, 'legacy');
  expect(JSON.parse(server.mutations[0]?.body ?? '{}') as unknown).toMatchObject({
    input: {problem: 'legacy'},
  });
});
