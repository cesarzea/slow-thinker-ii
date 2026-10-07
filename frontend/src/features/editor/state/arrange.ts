import type {Catalog, GraphDocument} from '../../../api/index.ts';
import {forwardLinks, graphLinks, longestPathLayers, orderLayers} from './arrange-graph.ts';

type Position = [number, number];
type Layout = Record<string, Position>;

const MARGIN = 40;
/** Columns of 220px cards with a gap of 90px. */
const COLUMN_STEP = 310;
const ROW_GAP = 40;
/** The height of a card that has not been measured yet. */
const CARD_HEIGHT = 150;

const isTrigger = (component: string): boolean => component.split('@')[0] === 'trigger';

/** The connected nodes in their ordered columns, and the nodes without connections. */
function columnsOf(
  document: GraphDocument,
  catalog: Catalog,
): {columns: string[][]; loose: string[]} {
  const order = document.nodes.map((node) => node.id);
  const links = graphLinks(document, catalog);
  const linked = new Set(links.flatMap((link) => [link.from, link.to]));
  const triggers = document.nodes
    .filter((node) => isTrigger(node.component))
    .map((node) => node.id);
  const forward = forwardLinks(order, triggers, links);
  const layers = longestPathLayers(order, forward);
  const placed = [...triggers, ...order.filter((id) => !triggers.includes(id))].filter((id) =>
    linked.has(id),
  );
  const depth = Math.max(-1, ...placed.map((id) => layers.get(id) ?? 0));
  const columns = Array.from({length: depth + 1}, (_, layer) =>
    placed.filter((id) => (layers.get(id) ?? 0) === layer),
  );
  return {columns: orderLayers(columns, forward), loose: order.filter((id) => !linked.has(id))};
}

/** Stack each column by card heights and centre the columns on one horizontal axis. */
function columnLayout(
  columns: readonly (readonly string[])[],
  height: (id: string) => number,
): {layout: Layout; bottom: number} {
  const sizes = columns.map(
    (column) => column.reduce((total, id) => total + height(id), 0) + ROW_GAP * (column.length - 1),
  );
  const tallest = Math.max(0, ...sizes);
  const layout: Layout = {};
  columns.forEach((column, layer) => {
    let top = MARGIN + (tallest - (sizes[layer] ?? 0)) / 2;
    for (const id of column) {
      layout[id] = [MARGIN + layer * COLUMN_STEP, Math.round(top)];
      top += height(id) + ROW_GAP;
    }
  });
  return {layout, bottom: MARGIN + tallest};
}

/**
 * A layered layout from left to right: loops are set aside, each node goes to the column of
 * its longest path from a Trigger or another source, columns are ordered to limit crossings,
 * and nodes without connections form a row below. The same graph always gets the same layout.
 */
export function arrangedLayout(
  document: GraphDocument,
  catalog: Catalog,
  heights: ReadonlyMap<string, number>,
): Layout {
  const {columns, loose} = columnsOf(document, catalog);
  const {layout, bottom} = columnLayout(columns, (id) => heights.get(id) ?? CARD_HEIGHT);
  const row = columns.length === 0 ? MARGIN : bottom + 2 * ROW_GAP;
  loose.forEach((id, index) => {
    layout[id] = [MARGIN + index * COLUMN_STEP, row];
  });
  return layout;
}

/** The nodes in the order the graph flows: column by column, then those without connections. */
export function flowOrder(document: GraphDocument, catalog: Catalog): string[] {
  const {columns, loose} = columnsOf(document, catalog);
  return [...columns.flat(), ...loose];
}

/** The document with every node placed by `arrangedLayout`. */
export function arrange(
  document: GraphDocument,
  catalog: Catalog,
  heights: ReadonlyMap<string, number>,
): GraphDocument {
  return {...document, layout: {...document.layout, ...arrangedLayout(document, catalog, heights)}};
}
