import {z} from 'zod';

const graphSchema = z.object({
  graph_id: z.string(),
  revision: z.string(),
  participants: z.number().int().positive(),
  nodes: z.array(z.object({id: z.string(), component: z.string()})).min(1),
});

export type GraphSummary = z.infer<typeof graphSchema>;

export async function loadGraphs(
  signal: AbortSignal,
  credential?: string,
): Promise<GraphSummary[]> {
  const response = await fetch('/api/v1/graphs', {
    signal,
    ...(credential === undefined
      ? {}
      : {headers: {authorization: `Bearer ${credential}`}, credentials: 'omit' as const}),
  });
  if (!response.ok) throw new Error('No se pudo cargar el catálogo de experimentos.');
  const body: unknown = await response.json();
  return z.array(graphSchema).parse(body);
}
