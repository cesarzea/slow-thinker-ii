import type {Catalog, GraphDocument, RunEvent} from '../../api/index.ts';

/** Readable names for the identifiers recorded in a run's events. */
export interface Names {
  readonly nodes: readonly {readonly id: string; readonly name: string}[];
  readonly node: (nodeId: string | null) => string;
  readonly component: (ref: string) => string;
  readonly llm: (id: string) => string;
  /** The component that made a report: the next call of its activation, or the node's host. */
  readonly reporter: (event: RunEvent, events: readonly RunEvent[]) => string;
}

export function activityNames(document: GraphDocument | null, catalog: Catalog | null): Names {
  const component = (ref: string): string =>
    catalog?.components.find((item) => `${item.type}@${item.version}` === ref)?.label ?? ref;
  const nodes = (document?.nodes ?? []).map((node) => ({id: node.id, name: node.name}));
  const host = (nodeId: string | null): string =>
    document?.nodes.find((node) => node.id === nodeId)?.component ?? 'component';
  return {
    nodes,
    node: (nodeId) =>
      nodeId === null ? 'Run' : (nodes.find((item) => item.id === nodeId)?.name ?? nodeId),
    component,
    llm: (id) => catalog?.llms.find((entry) => entry.id === id)?.label ?? id,
    reporter: (event, events) => {
      const call = events.find(
        (item) =>
          item.seq > event.seq &&
          item.kind === 'component.called' &&
          item.activation_id === event.activation_id,
      );
      return component(
        call?.kind === 'component.called' ? call.data.component : host(event.node_id),
      );
    },
  };
}
