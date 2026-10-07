import type {z} from 'zod';
import {captureAuthentication} from './authentication.ts';
import {ApiError, errorFromReply, requestFailure, unexpectedReply} from './errors.ts';
import {DEFAULT_REPLY_BYTES, boundedText} from './response-body.ts';

const BASE_PATH = '/api/v2';
const TIMEOUT_MS = 30_000;

export interface RequestOptions {
  readonly body?: unknown;
  readonly signal?: AbortSignal | undefined;
  readonly maxBytes?: number;
}
interface Exchange {
  readonly response: Response;
  readonly signal: AbortSignal;
  readonly timeout: AbortSignal;
}

/**
 * JSON exchanges with the operator API, with the bearer credential unless it is `null`;
 * every failure becomes an ApiError.
 */
export class Transport {
  constructor(private readonly credential: string | null) {}

  /** Sends the request and returns the reply when its status is one of `expected`. */
  async read<T>(
    path: string,
    schema: z.ZodType<T>,
    expected: number | readonly number[],
    options: RequestOptions = {},
  ): Promise<T> {
    const exchange = await this.send(path, options);
    const value = await replyValue(exchange, options);
    const {status} = exchange.response;
    if (!exchange.response.ok) throw errorFromReply(status, value);
    const parsed = schema.safeParse(value);
    const statuses = typeof expected === 'number' ? [expected] : expected;
    if (!statuses.includes(status) || !parsed.success) throw unexpectedReply(status);
    return parsed.data;
  }

  private async send(path: string, options: RequestOptions): Promise<Exchange> {
    const invalidated = captureAuthentication(this.credential);
    const timeout = AbortSignal.timeout(TIMEOUT_MS);
    const signal =
      options.signal === undefined ? timeout : AbortSignal.any([options.signal, timeout]);
    let response: Response;
    try {
      response = await fetch(`${BASE_PATH}${path}`, this.init(options, signal));
    } catch {
      throw requestFailure(options.signal, timeout.aborted);
    }
    if ((response.status === 401 || response.status === 403) && !signal.aborted) invalidated();
    return {response, signal: options.signal ?? timeout, timeout};
  }

  private init(options: RequestOptions, signal: AbortSignal): RequestInit {
    const accept = {accept: 'application/json'};
    const headers =
      this.credential === null ? accept : {...accept, authorization: `Bearer ${this.credential}`};
    const common = {credentials: 'omit', cache: 'no-store', signal} as const;
    if (options.body === undefined) return {...common, method: 'GET', headers};
    return {
      ...common,
      method: 'POST',
      headers: {...headers, 'content-type': 'application/json'},
      body: JSON.stringify(options.body),
    };
  }
}

async function replyValue(exchange: Exchange, options: RequestOptions): Promise<unknown> {
  const {response} = exchange;
  let text: string;
  try {
    text = await boundedText(response, options.maxBytes ?? DEFAULT_REPLY_BYTES);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (exchange.signal.aborted) throw requestFailure(options.signal, exchange.timeout.aborted);
    throw unexpectedReply(response.status);
  }
  if (text === '') return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    throw unexpectedReply(response.status);
  }
}
