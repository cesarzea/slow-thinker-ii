import type {Catalog, ComponentDeclaration, GraphNode} from '../api/index.ts';
import {canonicalJson, readPointer} from './json.ts';

/** The component declaration of a `type@version` reference, when the catalog has it. */
function declarationOf(
  catalog: Catalog | null,
  reference: string,
): ComponentDeclaration | undefined {
  return catalog?.components.find(
    (component) => `${component.type}@${component.version}` === reference,
  );
}

/** The component's label, or its type when the catalog does not know it. */
export function componentLabel(catalog: Catalog | null, reference: string): string {
  return declarationOf(catalog, reference)?.label ?? reference.split('@')[0] ?? reference;
}

function same(before: unknown, after: unknown): boolean {
  return canonicalJson(before) === canonicalJson(after);
}

/** The titles of the declared sections whose fields hold different values. */
function editedSections(
  declaration: ComponentDeclaration | undefined,
  before: GraphNode['config'],
  after: GraphNode['config'],
): string[] {
  if (same(before, after)) return [];
  const sections = declaration?.ui.sections ?? [];
  const titles = sections
    .filter((section) =>
      section.fields.some(
        (field) => !same(readPointer(before, field.path), readPointer(after, field.path)),
      ),
    )
    .map((section) => section.title);
  return titles.length === 0 ? ['Configuration'] : titles;
}

function embeddedEdits(catalog: Catalog | null, before: GraphNode, after: GraphNode): string[] {
  const old = before.embedded ?? [];
  const now = after.embedded ?? [];
  const added = now.filter((item) => !old.some((was) => was.component === item.component));
  const removed = old.filter((was) => !now.some((item) => item.component === was.component));
  const edited = now.filter((item) =>
    old.some((was) => was.component === item.component && !same(was.config, item.config)),
  );
  return [
    ...added.map((item) => `added ${componentLabel(catalog, item.component)} at its outputs`),
    ...removed.map((item) => `removed ${componentLabel(catalog, item.component)}`),
    ...edited.map((item) => `${componentLabel(catalog, item.component)} edited`),
  ];
}

/** What changed in one node: its name, its sections and its embedded components. */
export function nodeEdits(catalog: Catalog | null, before: GraphNode, after: GraphNode): string[] {
  const edits: string[] = [];
  if (before.name !== after.name) edits.push(`Renamed ${before.name} to ${after.name}`);
  const sections = editedSections(
    declarationOf(catalog, after.component),
    before.config,
    after.config,
  );
  if (sections.length > 0) edits.push(`${after.name} · ${sections.join(', ')} edited`);
  const embedded = embeddedEdits(catalog, before, after);
  if (embedded.length > 0) edits.push(`${after.name} · ${embedded.join(', ')}`);
  return edits;
}
