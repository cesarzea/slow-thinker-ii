import type {GraphDetail} from './graph-schemas.ts';
import type {GraphSummary} from './catalog.ts';
import {graphDetailSchema} from './graph-schemas.ts';
import {DefinitionTransport} from './definition-transport.ts';
import {DefinitionError, unconfirmedDefinitionFailure} from './definition-errors.ts';
import {patchBody} from './source-patch.ts';
import type {PatchOperation} from './source-patch.ts';
import {
  libraryPageSchema,
  validationResultSchema,
  saveResultSchema,
} from './definition-library-schemas.ts';

export {DefinitionError} from './definition-errors.ts';
export type {DefinitionIssue} from './definition-errors.ts';

export interface GraphReference {
  readonly graph_id: string;
  readonly revision: string;
}
export interface LibraryItem extends GraphSummary {
  readonly origin: 'bundled' | 'personal';
  readonly derived_from: GraphReference | null;
}
export interface LibraryPage {
  readonly items: LibraryItem[];
  readonly next_cursor: string | null;
}
export interface ValidationResult extends GraphReference {
  readonly validation_scope: 'definition';
}
export interface SaveResult extends GraphReference {
  readonly created: boolean;
}
export class DefinitionClient extends DefinitionTransport {
  async patch(
    source: string,
    operations: readonly PatchOperation[],
    signal: AbortSignal,
  ): Promise<string> {
    return await this.objectText('/definitions/patch', signal, patchBody(source, operations));
  }
  async list(signal: AbortSignal, cursor?: string, limit?: number): Promise<LibraryPage> {
    if (limit !== undefined && (!Number.isInteger(limit) || limit < 1 || limit > 100))
      throw new DefinitionError('invalid_query');
    const query = new URLSearchParams();
    if (cursor !== undefined) query.set('cursor', cursor);
    if (limit !== undefined) query.set('limit', String(limit));
    const suffix = query.size === 0 ? '' : `?${query.toString()}`;
    return await this.read(`/definitions${suffix}`, libraryPageSchema, signal);
  }
  async detail(reference: GraphReference, signal: AbortSignal): Promise<GraphDetail> {
    const query = new URLSearchParams({graph_id: reference.graph_id, revision: reference.revision});
    const detail = await this.read(
      `/definitions/detail?${query.toString()}`,
      graphDetailSchema,
      signal,
    );
    if (detail.graph_id !== reference.graph_id || detail.revision !== reference.revision)
      throw unconfirmedDefinitionFailure(false);
    return detail;
  }
  async validate(source: string, signal: AbortSignal): Promise<ValidationResult> {
    return await this.read('/definitions/validate', validationResultSchema, signal, source);
  }
  async source(reference: GraphReference, signal: AbortSignal): Promise<string> {
    const query = new URLSearchParams({graph_id: reference.graph_id, revision: reference.revision});
    return await this.text(`/definitions/source?${query.toString()}`, reference, signal);
  }
  async draft(
    reference: GraphReference,
    target: GraphReference,
    signal: AbortSignal,
  ): Promise<string> {
    const body = JSON.stringify({
      source: {graph_id: reference.graph_id, revision: reference.revision},
      target: {graph_id: target.graph_id, revision: target.revision},
    });
    return await this.text('/definitions/draft', target, signal, body);
  }
  async save(source: string, signal: AbortSignal): Promise<SaveResult> {
    return await this.read('/definitions', saveResultSchema, signal, source, (saved, status) =>
      saved.created ? status === 201 : status === 200,
    );
  }
}
