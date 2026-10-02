import {DefinitionError} from './definition-errors.ts';
const MAX_REPLY_BYTES = 1_048_576;
export async function boundedText(response: Response): Promise<string> {
  const reader = response.body?.getReader();
  if (reader === undefined) return '';
  const chunks: Uint8Array[] = [];
  let bytes = 0;
  try {
    for (;;) {
      const part = await reader.read();
      if (part.done) break;
      bytes += part.value.byteLength;
      if (bytes > MAX_REPLY_BYTES) throw new DefinitionError('response_too_large');
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
