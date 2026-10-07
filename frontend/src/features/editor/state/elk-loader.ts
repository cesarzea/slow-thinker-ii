import type {ELK} from 'elkjs/lib/elk-api.js';

let loading: Promise<ELK> | null = null;

/**
 * ELK, loaded on first use: its small API in a chunk of its own, and the layout engine as a
 * web worker script served as a file, so neither weighs on the main bundle.
 */
export async function loadElk(): Promise<ELK> {
  loading ??= (async () => {
    const [{default: Elk}, {default: workerUrl}] = await Promise.all([
      import('elkjs/lib/elk-api.js'),
      import('elkjs/lib/elk-worker.min.js?url'),
    ]);
    return new Elk({workerUrl});
  })();
  try {
    return await loading;
  } catch (error) {
    loading = null;
    throw error;
  }
}
