import type {ExecutionPage} from '../../api/index.ts';
import type {AgentPresentation} from './types.ts';

export function agentActivity(
  page: ExecutionPage | undefined,
  node: string,
): AgentPresentation['activity'] {
  if (page === undefined) return undefined;
  const activations = page.activations.filter((item) => item.node === node);
  const latest = activations.reduce<(typeof activations)[number] | undefined>(
    (previous, current) =>
      previous === undefined || current.ordinal > previous.ordinal ? current : previous,
    undefined,
  );
  return {state: latest?.state ?? 'No recorded activations', count: activations.length};
}
