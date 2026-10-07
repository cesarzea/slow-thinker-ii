import type {ComponentDeclaration} from '../../api/index.ts';

/** A labelled fact, shown as a term and its description. */
export type Fact = readonly [string, string];

function listText(items: readonly string[]): string {
  return items.length === 0 ? 'None' : items.join(', ');
}

function placementText(placements: ComponentDeclaration['placements']): string {
  if (placements.includes('memory')) return "Embedded as a node's memory";
  const node = placements.includes('node');
  if (node && placements.includes('output')) return "As a node, or embedded at a node's outputs";
  return node ? 'As a node' : "Embedded at a node's outputs";
}

function outputsText(ports: ComponentDeclaration['ports']): string {
  return ports.outputs_from === undefined
    ? listText(ports.outputs ?? [])
    : 'Outputs from its configuration';
}

/** Where a node chooses the LLM of one service use: the section holding that field. */
function llmText(component: ComponentDeclaration): string {
  if (component.uses.length === 0) return 'None';
  return component.uses
    .map(({pointer}) => {
      const section = component.ui.sections.find((candidate) =>
        candidate.fields.some((field) => field.path === pointer),
      );
      const place = section === undefined ? 'its configuration' : section.title;
      return `Chosen for each node in ${place}`;
    })
    .join('; ');
}

/** Use, ports, state, LLM service and configuration sections of a component. */
export function componentFacts(component: ComponentDeclaration): Fact[] {
  return [
    ['Use', placementText(component.placements)],
    ['Inputs', listText(component.ports.inputs)],
    ['Outputs', outputsText(component.ports)],
    ['State', component.state === 'stateful' ? 'Stateful' : 'Stateless'],
    ['LLM', llmText(component)],
    ['Configuration', listText(component.ui.sections.map((section) => section.title))],
  ];
}

/** “Platform” or “Installed package”. */
export function originText(origin: ComponentDeclaration['origin']): string {
  return origin === 'platform' ? 'Platform' : 'Installed package';
}
