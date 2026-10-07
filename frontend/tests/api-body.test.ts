import {afterEach, expect, it, vi} from 'vitest';
import {boundedText} from '../src/api/response-body.ts';
import {OperatorClient} from '../src/api/index.ts';

afterEach(() => {
  vi.unstubAllGlobals();
});

function streamOf(...parts: Uint8Array[]): ReadableStream<Uint8Array> {
  return new ReadableStream<Uint8Array>({
    start(controller) {
      for (const part of parts) controller.enqueue(part);
      controller.close();
    },
  });
}

it('joins bounded UTF-8 chunks and releases the stream reader', async () => {
  const bytes = new TextEncoder().encode('Ω source');
  const stream = streamOf(bytes.slice(0, 1), bytes.slice(1));
  expect(await boundedText(new Response(stream), 100)).toBe('Ω source');
  expect(stream.locked).toBe(false);
  expect(await boundedText(new Response(null), 100)).toBe('');
});

it('rejects oversized bodies, including command replies, before parsing them', async () => {
  const stream = streamOf(new Uint8Array(11));
  await expect(boundedText(new Response(stream), 10)).rejects.toMatchObject({
    code: 'response_too_large',
  });
  expect(stream.locked).toBe(false);
  const large = new Uint8Array(4_194_305).fill(32);
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(large, {status: 202})));
  await expect(new OperatorClient('credential').stopRun('run-1')).rejects.toMatchObject({
    code: 'response_too_large',
  });
});

it('rejects malformed UTF-8 as an unexpected reply', async () => {
  const body = new Response(new Uint8Array([0xff]), {status: 200});
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(body));
  await expect(new OperatorClient('credential').usage()).rejects.toMatchObject({
    code: 'invalid_response',
  });
});

it('reports a body interrupted by cancellation as a cancelled request', async () => {
  const controller = new AbortController();
  const stream = new ReadableStream<Uint8Array>({
    pull() {
      controller.abort();
      throw new Error('interrupted');
    },
  });
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(stream, {status: 200})));
  await expect(new OperatorClient('credential').usage(controller.signal)).rejects.toMatchObject({
    code: 'aborted',
  });
});
