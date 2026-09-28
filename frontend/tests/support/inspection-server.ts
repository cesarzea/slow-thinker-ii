import {childCall, events, retained, activation} from './inspection-data.ts';
import {reply} from './operator-data.ts';
import {OperatorServer} from './operator-server.ts';

export class InspectionServer {
  readonly operator = new OperatorServer();
  readonly reads: string[] = [];
  events = structuredClone(events);
  call = structuredClone(childCall);
  activation = structuredClone(activation);
  failed = false;
  missingUsage = false;

  readonly fetch = async (input: string, init?: RequestInit): Promise<Response> => {
    const url = new URL(input, 'https://fixture.invalid');
    const path = decodeURIComponent(url.pathname);
    this.reads.push(input);
    if (path.endsWith('/events'))
      return this.failed ? reply({}, 503) : reply(this.eventPage(url.searchParams.has('cursor')));
    if (path.includes('/calls/')) return reply(this.callPage(path, url.searchParams.has('cursor')));
    if (path.includes('/activations/'))
      return reply(
        url.searchParams.has('cursor')
          ? {...this.activation, calls: {items: [], next_cursor: null}}
          : this.activation,
      );
    if (path.includes('/payloads/')) return reply(this.payload(path.split('/').at(-1) ?? ''));
    return await this.operator.fetch(input, init);
  };

  private eventPage(next: boolean): typeof events {
    return next ? {...this.events, items: [], next_cursor: null} : this.events;
  }

  private callPage(path: string, next: boolean): typeof childCall {
    if (path.endsWith('/parent'))
      return {
        ...this.call,
        call_id: 'parent',
        accounting: null,
        pricing_payload_id: null,
        context: {
          ...this.call.context,
          caller: null,
          parent_call_id: null,
          node_id: null,
          activation_id: null,
        },
        receipts: {items: [], next_cursor: null},
      };
    return next ? {...this.call, receipts: {items: [], next_cursor: null}} : this.call;
  }

  private payload(id: string): ReturnType<typeof retained> {
    const value = retained(id);
    return this.missingUsage && id.startsWith('usage:')
      ? {
          ...value,
          status: 'unavailable',
          reason: 'not_recorded',
          content: null,
          size_bytes: null,
        }
      : value;
  }
}
