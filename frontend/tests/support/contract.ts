import triggerJson from '../../../docs/contracts/examples/trigger.component.json';
import outputJson from '../../../docs/contracts/examples/output.component.json';
import llmCallJson from '../../../docs/contracts/examples/llm-call.component.json';
import routerJson from '../../../docs/contracts/examples/router.component.json';
import memoryJson from '../../../docs/contracts/examples/memory.component.json';
import llmCatalogJson from '../../../docs/contracts/examples/llm-catalog.json';
import j1Json from '../../../docs/contracts/examples/funny-story.graph.json';
import j2Json from '../../../docs/contracts/examples/story-triage.graph.json';
import j3Json from '../../../docs/contracts/examples/funny-story-with-review.graph.json';
import {catalogSchema} from '../../src/api/schemas/catalog.ts';
import {graphDocumentSchema} from '../../src/api/schemas/graph.ts';
import type {Catalog, ComponentDeclaration, GraphDocument, LlmEntry} from '../../src/api/index.ts';

/** The catalog body served by GET /catalog, built from the contract examples. */
export const catalogBody = {
  components: [
    {...triggerJson, origin: 'platform'},
    {...outputJson, origin: 'platform'},
    {...llmCallJson, origin: 'package'},
    {...routerJson, origin: 'package'},
  ],
  llms: llmCatalogJson,
};

export const catalog: Catalog = catalogSchema.parse(catalogBody);

/** The catalog with the Memory package as well, a component that only goes inside a node. */
export const memoryCatalogBody = {
  ...catalogBody,
  components: [...catalogBody.components, {...memoryJson, origin: 'package'}],
};

export function declaration(type: string): ComponentDeclaration {
  const found = catalog.components.find((component) => component.type === type);
  if (found === undefined) throw new Error(`Missing declaration ${type}`);
  return found;
}

export function llm(id: string): LlmEntry {
  const found = catalog.llms.find((entry) => entry.id === id);
  if (found === undefined) throw new Error(`Missing LLM ${id}`);
  return found;
}

export const j1: GraphDocument = graphDocumentSchema.parse(j1Json);
export const j2: GraphDocument = graphDocumentSchema.parse(j2Json);
export const j3: GraphDocument = graphDocumentSchema.parse(j3Json);

export function copy<T>(value: T): T {
  return structuredClone(value);
}
