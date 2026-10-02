import type {GraphReference, LibraryItem} from '../../src/api/index.ts';
import {reply} from './operator-data.ts';

export const reference: GraphReference = {graph_id: 'single-agent', revision: 'personal α / one'};
export const target: GraphReference = {graph_id: 'single-agent', revision: 'variant β / two'};
export const numericSource =
  '{\n "graph_id":"single-agent", "revision":"personal α / one", "float":1.0, "integer":9007199254740993\n}\n';
export const signal = (): AbortSignal => new AbortController().signal;
export const item: LibraryItem = {
  ...reference,
  participants: 1,
  nodes: [{id: 'draft', component: 'proposer'}],
  input_schema: {},
  origin: 'personal',
  derived_from: {graph_id: 'single-agent', revision: 'example-2'},
};

export function errorReply(code: string, status: number, issues?: unknown): Response {
  return reply(
    {
      schema_version: '0.1-draft',
      error: {
        code,
        message: code.replaceAll('_', ' '),
        request_id: 'request',
        ...(issues === undefined ? {} : {issues}),
      },
    },
    status,
  );
}

export function textReply(
  source = numericSource,
  status = 200,
  contentType = 'application/json',
): Response {
  return new Response(source, {status, headers: {'content-type': contentType}});
}
