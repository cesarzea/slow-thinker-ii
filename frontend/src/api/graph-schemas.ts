import {z} from 'zod';
import {validDefinition} from './definition-validation.ts';

export const jsonObjectSchema = z.record(z.string(), z.json());
const componentSchema = z.object({
  id: z.string().min(1),
  type_id: z.string().min(1),
  type_version: z.string().min(1),
  roles: z.array(z.string()).readonly(),
  contained_by: z.string().nullable(),
});
const plannedNodeSchema = z.object({id: z.string().min(1), component: z.string().min(1)});
const relationshipSchema = z.object({
  id: z.string().min(1),
  kind: z.enum(['control', 'permission', 'binding']),
  source: z.string().min(1),
  target: z.string().nullable(),
  label: z.string(),
});
const graphStructureSchema = z
  .object({
    components: z.array(componentSchema).readonly(),
    nodes: z.array(plannedNodeSchema).readonly(),
    edges: z.array(relationshipSchema).readonly(),
  })
  .refine(validStructure, 'La estructura contiene identidades o relaciones inválidas.');
export const graphDetailSchema = z
  .object({
    graph_id: z.string().min(1),
    revision: z.string().min(1),
    input_schema: jsonObjectSchema,
    definition: jsonObjectSchema.refine(
      validDefinition,
      'La definición no cumple el contrato del grafo.',
    ),
    structure: graphStructureSchema,
  })
  .refine(
    (detail) =>
      detail.definition['graph_id'] === detail.graph_id &&
      detail.definition['revision'] === detail.revision,
    'La definición no corresponde a su identidad.',
  );

export type ComponentView = Readonly<z.infer<typeof componentSchema>>;
export type PlannedNodeView = Readonly<z.infer<typeof plannedNodeSchema>>;
export type RelationshipView = Readonly<z.infer<typeof relationshipSchema>>;
export type GraphStructure = Readonly<z.infer<typeof graphStructureSchema>>;
export type GraphDetail = Readonly<z.infer<typeof graphDetailSchema>>;

function validStructure(value: {
  components: readonly ComponentView[];
  nodes: readonly PlannedNodeView[];
  edges: readonly RelationshipView[];
}): boolean {
  const components = new Set(value.components.map((item) => item.id));
  const nodes = new Set(value.nodes.map((item) => item.id));
  return (
    components.size === value.components.length &&
    nodes.size === value.nodes.length &&
    new Set(value.edges.map((item) => item.id)).size === value.edges.length &&
    value.nodes.every((node) => components.has(node.component)) &&
    value.components.every((component) => validContainment(component, value.components)) &&
    value.edges.every((edge) => validEndpoints(edge, edge.kind === 'control' ? nodes : components))
  );
}

function validEndpoints(edge: RelationshipView, identities: Set<string>): boolean {
  return identities.has(edge.source) && (edge.target === null || identities.has(edge.target));
}

function validContainment(component: ComponentView, all: readonly ComponentView[]): boolean {
  const visited = new Set([component.id]);
  let parent = component.contained_by;
  while (parent !== null) {
    if (visited.has(parent)) return false;
    visited.add(parent);
    const ancestor = all.find((item) => item.id === parent);
    if (ancestor === undefined) return false;
    parent = ancestor.contained_by;
  }
  return true;
}
