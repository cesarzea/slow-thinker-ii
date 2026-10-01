import type {GraphDetail} from '../../api/index.ts';
import type {AgentConfiguration, ConfigurationValue} from './types.ts';
import {
  componentConfiguration,
  definitionComponent,
  enforcedEffort,
  record,
  resourceTarget,
  textValue,
} from './configuration-records.ts';

export function agentConfiguration(
  detail: GraphDetail | undefined,
  component: string,
): AgentConfiguration {
  const worker = modelWorker(detail, component);
  if (worker === undefined) return unavailableConfiguration();
  const model = resourceTarget(detail, worker, 'model');
  if (model === undefined) return unavailableConfiguration();
  const modelConfig = componentConfiguration(detail, model);
  const modelName = textValue(modelConfig.config['model']) ?? 'Unavailable';
  return {
    model: {value: modelName, source: modelConfig.source},
    effort: reasoningEffort(detail, worker, model),
  };
}
function modelWorker(detail: GraphDetail | undefined, initial: string): string | undefined {
  const visited = new Set<string>();
  let current: string | undefined = initial;
  while (current !== undefined && !visited.has(current)) {
    visited.add(current);
    const type = definitionComponent(detail, current)['type_id'];
    if (type === 'llm-call') return current;
    if (type !== 'routed-call') return undefined;
    current = resourceTarget(detail, current, 'worker');
  }
  return undefined;
}
function reasoningEffort(
  detail: GraphDetail | undefined,
  worker: string,
  model: string,
): ConfigurationValue {
  const enforced = enforcedEffort(detail, model);
  if (enforced !== undefined) return {value: enforced, source: 'Saved configuration'};
  const {config, source} = componentConfiguration(detail, worker);
  const parameters = record(config['parameters']);
  const value =
    textValue(parameters['reasoning_effort']) ??
    textValue(record(parameters['reasoning'])['effort']) ??
    'Not specified';
  return {value, source};
}
function unavailableConfiguration(): AgentConfiguration {
  return {
    model: {value: 'Unavailable', source: 'Graph configuration'},
    effort: {value: 'Not specified', source: 'Graph configuration'},
  };
}
