import {ApiError} from './errors.ts';

export const DEFAULT_REPLY_BYTES = 4_194_304;

/** Read a response body as UTF-8 text, refusing bodies above the given size. */
export async function boundedText(response: Response, maxBytes: number): Promise<string> {
  const reader = response.body?.getReader();
  if (reader === undefined) return '';
  const chunks: Uint8Array[] = [];
  let bytes = 0;
  try {
    for (;;) {
      const part = await reader.read();
      if (part.done) break;
      bytes += part.value.byteLength;
      if (bytes > maxBytes)
        throw new ApiError(response.status, 'response_too_large', 'The server reply is too large.');
      chunks.push(part.value);
    }
    const content = new Uint8Array(bytes);
    let offset = 0;
    for (const chunk of chunks) {
      content.set(chunk, offset);
      offset += chunk.byteLength;
    }
    return new TextDecoder('utf-8', {fatal: true}).decode(content);
  } finally {
    await reader.cancel();
    reader.releaseLock();
  }
}
