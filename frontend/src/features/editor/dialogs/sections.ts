import type {
  Catalog,
  ComponentDeclaration,
  GraphDocument,
  GraphNode,
  JsonObject,
  UiSection,
} from '../../../api/index.ts';
import {fieldVisible, previewValue, readPointer, summaryValue} from '../../../ui/index.ts';
import type {SummaryEntry} from '../../../ui/index.ts';
import {setEmbeddedConfig, setNodeConfig} from '../state/document.ts';
import {declarationFor, embeddedAt} from '../state/ports.ts';
import type {EmbeddedPosition} from '../state/ports.ts';

/** One section of a node dialog: the host's sections first, then the embedded component's. */
export interface NodeSection {
  readonly key: string;
  readonly section: UiSection;
  readonly declaration: ComponentDeclaration;
  readonly embedded: boolean;
  /** Where the section's component is embedded; null for the host. */
  readonly position: EmbeddedPosition | null;
}

/** Section keys: the host's, the output component's (as before memories) and the memory's. */
const PREFIXES: Readonly<Record<EmbeddedPosition | 'host', string>> = {
  host: 'host',
  output: 'embedded',
  memory: 'memory',
};

function owned(
  declaration: ComponentDeclaration | undefined,
  position: EmbeddedPosition | null,
): NodeSection[] {
  if (declaration === undefined) return [];
  const prefix = PREFIXES[position ?? 'host'];
  return declaration.ui.sections.map((section) => ({
    key: `${prefix}:${section.id}`,
    section,
    declaration,
    embedded: position !== null,
    position,
  }));
}

/** The host's sections, then the output component's, then the memory's. */
export function nodeSections(node: GraphNode, catalog: Catalog): NodeSection[] {
  return [
    ...owned(declarationFor(catalog, node.component), null),
    ...owned(declarationFor(catalog, embeddedAt(node, 'output')?.component), 'output'),
    ...owned(declarationFor(catalog, embeddedAt(node, 'memory')?.component), 'memory'),
  ];
}

export function sectionConfig(node: GraphNode, entry: NodeSection): JsonObject {
  return entry.position === null ? node.config : (embeddedAt(node, entry.position)?.config ?? {});
}

export function withSectionConfig(
  document: GraphDocument,
  nodeId: string,
  entry: NodeSection,
  config: JsonObject,
): GraphDocument {
  return entry.position === null
    ? setNodeConfig(document, nodeId, config)
    : setEmbeddedConfig(document, nodeId, config, entry.position);
}

/** The visible fields of a section with their summary text. */
export function sectionSummary(
  node: GraphNode,
  entry: NodeSection,
  catalog: Catalog,
): SummaryEntry[] {
  const config = sectionConfig(node, entry);
  return entry.section.fields
    .filter((field) => fieldVisible(field, config))
    .map((field) => ({
      label: field.label,
      value: summaryValue(field, readPointer(config, field.path), catalog.llms),
    }));
}

/** One line for a section's row: the visible fields' short values, joined. */
export function sectionPreview(node: GraphNode, entry: NodeSection, catalog: Catalog): string {
  const config = sectionConfig(node, entry);
  return entry.section.fields
    .filter((field) => fieldVisible(field, config))
    .map((field) => previewValue(field, readPointer(config, field.path), catalog.llms))
    .join(' · ');
}
