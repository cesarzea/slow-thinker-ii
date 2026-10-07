import type {GraphDocument} from '../../../api/index.ts';

/** React Flow's bezier or simple bezier curves between handles; or routes around the cards. */
export type ConnectionStyle = 'curved' | 'simple' | 'routed';
/** How a graph's connections are drawn, saved with the graph. */
export interface ConnectionView {
  readonly connections: ConnectionStyle;
  /** React Flow's bezier curvature, from 0 to 1. */
  readonly curvature: number;
}

export const DEFAULT_VIEW: ConnectionView = {connections: 'curved', curvature: 0.25};

/** The document's view, with curved connections of curvature 0.25 unless it says otherwise. */
export function viewOf(document: GraphDocument): ConnectionView {
  return {
    connections: document.view?.connections ?? DEFAULT_VIEW.connections,
    curvature: document.view?.curvature ?? DEFAULT_VIEW.curvature,
  };
}

/** The document with part of its view changed. */
export function withView(document: GraphDocument, change: Partial<ConnectionView>): GraphDocument {
  return {...document, view: {...document.view, ...change}};
}
