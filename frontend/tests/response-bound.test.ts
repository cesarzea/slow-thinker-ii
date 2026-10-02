import {expect, it} from 'vitest';
import {boundedText} from '../src/api/response-body.ts';
it('joins bounded UTF-8 chunks and releases the stream reader', async () => {
  const bytes = new TextEncoder().encode('Ω source');
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(bytes.slice(0, 1));
      controller.enqueue(bytes.slice(1));
      controller.close();
    },
  });
  expect(await boundedText(new Response(stream))).toBe('Ω source');
  expect(stream.locked).toBe(false);
  expect(await boundedText(new Response(null))).toBe('');
});
it('rejects oversized and malformed UTF-8 response bodies without reconstructing source', async () => {
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(new Uint8Array(1_048_577));
    },
  });
  await expect(boundedText(new Response(stream))).rejects.toMatchObject({
    code: 'response_too_large',
  });
  expect(stream.locked).toBe(false);
  await expect(boundedText(new Response(new Uint8Array([0xff])))).rejects.toThrow();
});
