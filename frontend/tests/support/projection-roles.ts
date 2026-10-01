/** Match bundled component descriptor roles, including model resources. */
export function fixtureRoles(type: string): readonly string[] {
  if (type === 'llm-call' || type === 'routed-call') return ['agent'];
  if (type === 'example.model-resource' || type === 'redirector') return ['resource'];
  return ['control'];
}
