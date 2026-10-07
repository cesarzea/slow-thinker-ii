import {vi} from 'vitest';

export interface ApiCall {
  readonly method: string;
  readonly path: string;
  readonly query: URLSearchParams;
  readonly body: unknown;
  readonly init: RequestInit;
}
export interface Reply {
  readonly status: number;
  readonly body?: unknown;
}
type Handler = (call: ApiCall) => Reply | Promise<Reply>;

export function reply(body: unknown, status = 200): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: {'content-type': 'application/json'},
  });
}

export function failure(status: number, code: string, message: string, extra = {}): Reply {
  return {status, body: {error: {code, message, ...extra}}};
}

/** A fake operator API: routes are "METHOD /path" without the /api/v2 prefix or query. */
export class FakeApi {
  readonly calls: ApiCall[] = [];
  private readonly routes = new Map<string, Handler>();

  on(route: string, handler: Handler | Reply): this {
    this.routes.set(route, typeof handler === 'function' ? handler : () => handler);
    return this;
  }

  install(): this {
    vi.stubGlobal('fetch', vi.fn(this.fetch));
    return this;
  }

  count(route: string): number {
    return this.calls.filter((call) => `${call.method} ${call.path}` === route).length;
  }

  last(route: string): ApiCall | undefined {
    return this.calls.filter((call) => `${call.method} ${call.path}` === route).at(-1);
  }

  private readonly fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const call = describe(input, init ?? {});
    this.calls.push(call);
    const handler = this.routes.get(`${call.method} ${call.path}`);
    if (handler === undefined)
      return reply({error: {code: 'not_found', message: 'No route.'}}, 404);
    if (init?.signal?.aborted === true) throw new DOMException('Aborted', 'AbortError');
    const answer = await handler(call);
    return reply(answer.body, answer.status);
  };
}

function describe(input: RequestInfo | URL, init: RequestInit): ApiCall {
  const target = input instanceof Request ? input.url : input.toString();
  const url = new URL(target, 'https://interface.test');
  const body = typeof init.body === 'string' ? (JSON.parse(init.body) as unknown) : undefined;
  return {
    method: init.method ?? 'GET',
    path: url.pathname.replace(/^\/api\/v2/u, ''),
    query: url.searchParams,
    body,
    init,
  };
}
