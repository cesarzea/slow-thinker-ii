import type {ComponentView} from '../../api/index.ts';

const labels: Readonly<Record<string, string>> = {
  agent: 'Agent',
  resource: 'Resource',
  control: 'Controller',
};
export function componentRole(item: ComponentView): string {
  return item.roles.length === 0
    ? 'Component'
    : item.roles.map((role) => labels[role] ?? role).join(' / ');
}
