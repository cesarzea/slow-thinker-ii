import type {CSSProperties} from 'react';
import type {ComponentView} from '../../api/index.ts';

const labels: Readonly<Record<string, string>> = {
  agent: 'Agente',
  resource: 'Recurso',
  control: 'Control',
};
const borders: Readonly<Record<string, string>> = {
  agent: '2px solid #274f85',
  resource: '2px dashed #167060',
  control: '3px double #7751a2',
};
export function componentRole(item: ComponentView): string {
  return item.roles.length === 0
    ? 'Componente'
    : item.roles.map((role) => labels[role] ?? role).join(' / ');
}
export function componentStyle(item: ComponentView): CSSProperties {
  const border = item.roles.map((role) => borders[role]).find((value) => value !== undefined);
  return {border: border ?? '1px solid #bccbd6'};
}
