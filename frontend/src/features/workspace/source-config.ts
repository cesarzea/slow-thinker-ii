import {sourceString, sourceTree} from '../../ui/index.ts';
import type {SourceValue} from '../../ui/index.ts';
import type {InstalledType, ConfigurationCatalog} from '../../api/index.ts';
export function controllerSource(source: string): {
  readonly id: string;
  readonly config: SourceValue | undefined;
  readonly conditional: boolean;
} {
  const root = sourceTree(source);
  const id = sourceString(root?.entries.get('controller')?.entries.get('component'));
  const components = root?.entries.get('components');
  return {
    id,
    config: components?.entries.get(id)?.entries.get('config'),
    conditional: sourceString(root?.entries.get('execution_profile')) === 'bounded-conditional',
  };
}
export function registeredType(
  catalog: ConfigurationCatalog | null,
  component: SourceValue | undefined,
): InstalledType | undefined {
  const type = sourceString(component?.entries.get('type_id'));
  const version = sourceString(component?.entries.get('type_version'));
  return catalog?.components.find((item) => item.type_id === type && item.type_version === version);
}
